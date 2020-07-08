# books-vs-films
Do good books always get made in to bad films?

An exercise in web-scraping, procedural cleaning, and linear regression.

Results:
lobf:  y = 0.80x + 3.51,   y is film rating, x is book rating
p value: 0.00   -> significant result
Rsquared: 0.07  -> poorly fitting the line
corr coef: 0.26 -> minor positive correlation

Conclusion: 
Some positive correlation between ratings of book and film, but plenty of variance. Expected as there's a lot more that goes in to the quality of a film than just the book it came from (screenplay, director, acting, etc.)

Notes: 
- screen scraping wasn't able to process 20% of the films/books, particularly ones with sequels. films with sequels might be higher rated, therefore skewing the film ratings to lower rating. Not sure. Better scraping to follow when there's time.
