import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.api import add_constant
from statsmodels.regression.linear_model import OLS as lin_reg
from matplotlib import pyplot as plt

data = pd.read_csv('book_and_films_with_ratings.csv')  # read in data
mask = (data['book_rating_goodreads'] == -1) | (data['book_rating_goodreads'] == -2) |\
       (data['book_rating_goodreads'] == 0) |\
       (data['film_rating_imdb'] == -1) | (data['film_rating_imdb'] == -2)
data = data[~mask]  # remove items where there is no rating

# regression plot
ax = sns.regplot('book_rating_goodreads', 'film_rating_imdb', data=data)
ax.set_xlim([0, 5])
ax.set_ylim([0, 10])

# regression model to extrapolate line of best fit down to 0
model = lin_reg(data['film_rating_imdb'], add_constant(data['book_rating_goodreads'])).fit()  # fit model
intercept, slope = model.params  # get slope & intercept
x = np.linspace(0, data['book_rating_goodreads'].min())  # x values for extrapolated lobf
ax.plot(x, model.predict(add_constant(x)),
        '--', color=ax.lines[0].get_color(), linewidth=ax.lines[0].get_linewidth())  # plot extrapolated lobf

# p value & r-squared for label
p_value = model.pvalues['book_rating_goodreads']
rsquared = model.rsquared
ax.lines[0].set_label('$y = {:.2f}x + {:.2f}$\n$p = {:.2f}$\n$R^2 = {:.2f}$'.format(slope, intercept, p_value, rsquared))
plt.legend(loc='upper left')
