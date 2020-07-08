import pandas as pd
from bs4 import BeautifulSoup as Soup
import requests
from re import match


def get_imdb_search_url(title, year):
    # produce a search url for imdb for a given title and year
    return 'https://www.imdb.com/search/title/?' + \
           'title={}&'.format(title.replace(' ', '+')) + \
           'title_type=feature&' + \
           'release_date={}-01-01,{}-12-31'.format(year-1, year+1)  # +/- 1 year as they seem to differ sometimes


def get_goodreads_search_url(title, author):
    # produce a search url for goodreads for a given title & year
    return 'https://www.goodreads.com/search?utf8=%E2%9C%93&query={}'.format((title+' '+author).replace(' ', '+'))


def imdb_rating(film):
    # returns the imdb rating for film
    # returns -1 if there are no search results for film
    # returns -2 if no exact title match, when mulitple films were found for film's name and year
    url = get_imdb_search_url(title=film['film_title'], year=film['film_year'])
    results_page = Soup(requests.get(url).text, features='html.parser')  # search for film & year and cook
    results = results_page.find_all('div', {'class': 'inline-block ratings-imdb-rating'})  # ratings-imdb-rating
    if len(results) == 0:
        return -1  # no results found for title and year
    if len(results) > 1:  # more than one result
        film_titles = results_page.find_all('h3', {'class': 'lister-item-header'})  # list search results
        film_titles = [title.find('a').get_text() for title in film_titles]  # extract titles from list
        if film['film_title'] in film_titles:
            return results[film_titles.index(film['film_title'])]['data-value']  # match title, return rating at that index
        else:
            return -2  # more than one result and no exact match to title found
    return float(results[0]['data-value'])


def remove_stars_span(goodreads_search_result):
    # cleaning
    # removes span tag in search results
    for span in goodreads_search_result.find_all('span', {'class': 'stars staticStars notranslate'}):
        span.decompose()
    return goodreads_search_result


def title_from_goodreads_url(url):
    # extract book title from url
    # '/book/show/2956.The_Adventures_of_Huckleberry_Finn?from_search=true&amp;from_srp=true&amp;qid=qcSdUb4S3c&amp;rank=1'
    title = match(r'/book/show/[0-9]+[\.\-](.+)\?from_search.+', url).groups()[0]
    return title.replace('_', ' ')


def clean_up(title):
    # clean up the title for consistent searching
    out = title.lower()
    # remove any leading 'the'
    if out[:4].lower() == 'the ':
        out = out[4:]
    # remove '-', '.' and ',' characters
    out = out.replace('-', ' ').replace('.', ' ').replace('  ', ' ').replace(',', '')
    return out


def extract_rating_from_minirating_span(minirating_span):
    return float(match(r' (.+) avg rating — .+ ratings?', remove_stars_span(minirating_span).get_text()).groups()[0])


def goodreads_rating(book):
    url = get_goodreads_search_url(book['book_title'], book['book_author'])
    results_page = Soup(requests.get(url).text, features='html.parser')  # search for film & year and cook
    results = results_page.find_all('span', {'class': 'minirating'})  # get list of results
    if len(results) == 0:
        return -1  # no results found for title and year
    if len(results) > 1:
        titles = results_page.find_all('a', {'class': 'bookTitle'})  # list search results
        book_title = clean_up(book['book_title'])
        if book_title == 'adventure':
            x = 1
        result_titles = (clean_up(title_from_goodreads_url(title['href']))
                         for title in titles[:min(5, len(titles))])  # generator to extract title from results (top 5)
        i = 0  # index counter
        for result_title in result_titles:
            if result_title == book_title:
                # get rating
                return extract_rating_from_minirating_span(results[i])  # return rating at matching index
            i += 1
        return -2  # more than one result and no exact match to title found
    return extract_rating_from_minirating_span(results[0])  # return rating


# import data
books_and_films = pd.read_csv('books_and_films.csv')
# books_and_films = pd.read_csv('book_and_films_with_imdb_rating.csv').head(100)

# gather film rating from IMDb & GoodReads, and save
books_and_films['film_rating_imdb'] = books_and_films.apply(imdb_rating, axis=1)
books_and_films['book_rating_goodreads'] = books_and_films.apply(goodreads_rating, axis=1)
books_and_films.to_csv('book_and_films_with_ratings.csv', index=False)

pass