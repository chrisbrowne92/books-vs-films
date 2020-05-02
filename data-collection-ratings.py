import pandas as pd
from bs4 import BeautifulSoup as Soup
import requests


def get_imdb_search_url(title, year):
    return 'https://www.imdb.com/search/title/?' + \
           'title={}&'.format(title.replace(' ', '+')) + \
           'title_type=feature&' + \
           'release_date={}-01-01,{}-12-31'.format(year-1, year+1)  # +/- 1 year as they seem to differ sometimes


def imdb_rating(film):
    # returns the imdb rating for film
    # returns -1 if there are no search results for film
    # returns -2 if mulitple films were found for film's name and year (+/- 1 year)
    url = get_imdb_search_url(title=film['film_title'], year=film['film_year'])
    results_page = Soup(requests.get(url).text, features='html.parser')  # search for film & year and cook
    results = results_page.find_all('div', {'class': 'inline-block ratings-imdb-rating'})  # ratings-imdb-rating
    if len(results) == 0:
        return -1  # no results
    if len(results) > 1:
        return -2  # more than one result
    return float(results[0]['data-value'])

# import data
books_and_films = pd.read_csv('books_and_films.csv').head(20)

# gather film rating from IMDb & save
books_and_films['film_rating_imdb'] = books_and_films.apply(imdb_rating, axis=1)
books_and_films.to_csv('book_and_films_with_imdb_rating.csv')


