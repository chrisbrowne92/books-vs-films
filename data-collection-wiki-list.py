from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
from re import match


def get_text_split_by_line_breaks(soup):
    # returns the text of soup split by line break tags, as a list of strings
    # replace <br> tags with unambiguous string because .get_text() ignores <br> tags
    delimiter = '###'
    for line_break in soup.findAll('br'):
        line_break.replaceWith(delimiter)
    return soup.get_text().split(delimiter)


def parse_book(book):
    # extracts book title, author and year from the html of the table cell
    # assumes book is of the format "<title> (<year>), <author>" with no extra brackets
    # check format
    if len(book.find_all('br')) > 1:  # more than one book title in cell, e.g. sequels
        return None
    book_text = book.get_text()
    if (book_text.count('(') != 1) or (book_text.count(')') != 1):
        return None
    # extract book info
    book_data = match(r'(.+) ?\(([0-9]{4})\),? ?(.+)', book_text)
    if book_data is None:  # if data was not found
        return None
    else:
        return dict(zip(['book_title', 'book_year', 'book_author'], map(str.strip, book_data.groups())))


def parse_film(film):
    # extracts film title and year
    # assumes film is in the format <title> (<year>) with no extra brackets in title
    # ignores films with * at the start, as these can be sequels that are not related
    # check format
    if film[0] == '*':
        return None
    if (film.count('(') != 1) or (film.count('(') != 1):  # more than one set of brackets
        return None
    # extract film info
    film_data = match(r'(.+) ?\(([0-9]{4})\)', film)
    if film_data is None:  # if data was not found
        return None
    else:
        return dict(zip(['film_title', 'film_year'], map(str.strip, film_data.groups())))


# gather a list of books that have been made into films
# extract data from tables in wikipedia pages:
wiki_urls = ['https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(0-9,_A-C)',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(D-J)',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(K-R)',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(S-Z)']

reject_count = 0  # count to see how many
books_and_films = []
for url in wiki_urls:
    page = requests.get(url).text  # get page html
    soup = Soup(page, features='html.parser')  # cook it
    for table in soup.find_all('table', {'class': 'wikitable'}):  # loop through tables on page
        for row in table.find_all('tr')[1:]:  # loop through table rows, skipping header row
            cells = row.find_all('td')  # get cells within row
            if len(cells) == 2:  # only collect data for rows with both book & film
                book = parse_book(cells[0])  # extract book data
                if book is not None:  # if book was extracted
                    films = []  # list of films made
                    for film in get_text_split_by_line_breaks(cells[1]):  # go through each film
                        film_data = parse_film(film)  # extract film data
                        if film_data is not None:  # if data was extracted
                            films.append(film_data)  # add to list
                    if len(films) > 0:  # if at least one film was extracted
                        for film in films:
                            film.update(book)  # combine data from each film with the book's
                            books_and_films.append(film)  # add to overall list
                    else:
                        reject_count += 1
                else:
                    reject_count += 1

# print number of rows process, successfully & unsucessfully (rejected)
total = reject_count + len(books_and_films)
print('{} processed\n{} successfully parsed\n{} rejected ({}%)'.format(total,
                                                                       len(books_and_films),
                                                                       reject_count,
                                                                       int(round(100 * reject_count / total))))

books_and_films = pd.DataFrame(books_and_films)  # convert to dataframe
books_and_films.to_csv('books_and_films.csv', index=False)  # save
