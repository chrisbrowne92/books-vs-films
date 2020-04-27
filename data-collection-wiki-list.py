from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd

### gather a list of books that have been made into films ###

# extract data from tables in wikipedia pages:
wiki_urls = ['https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(0-9,_A-C)',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(D-J)',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(K-R)',
             'https://en.wikipedia.org/wiki/List_of_fiction_works_made_into_feature_films_(S-Z)']

i = 0  # index counter
books_and_films = dict()  # intialise for use in loop
for url in wiki_urls:
    page = requests.get(url).text  # get page html
    soup = Soup(page, features='html.parser')  # cook it
    for table in soup.find_all('table', {'class': 'wikitable'}):  # loop through tables on page
        for row in table.find_all('tr')[1:]:  # loop through table rows, skip header row
            cells = row.find_all('td')  # get cells within row
            if len(cells) == 2:  # only collect data for rows with both book & film
                book = cells[0].get_text()
                films = cells[1]  # handle multiple films made for a book, they are separated by <br> tags in the html
                # replace <br> tags in film cell with unambiguous string because .get_text() ignores them
                delimiter = '###'
                for line_break in films.findAll('br'):
                    line_break.replaceWith(delimiter)
                films = films.get_text().split(delimiter)  # get list of films
                for film in films:  # add each to the dictionary
                    books_and_films[i] = [book, film]
                    i += 1
i_max = i - 1
books_and_films = pd.DataFrame.from_dict(books_and_films, orient='index', columns=['book_raw', 'film_raw'])
