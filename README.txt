CATALOG PROJECT  version 1.0.0 07/28/2015
Author : Hugo Boutet Romanowski

GENRERAL USAGE NOTES
-------------------------------------------------

This project is a candy catalog. 
Each candy has a category and each categories has candies.
You need to log in with a Facebook or Google account to edit, delete and add new candy or category.
JSON API are available with this route /candy/json or /category/json
Candies are sort by the risk of cavity they can give to your teeth. 
Each candy need a score.
To add a picture to a new candy, you have to put the picture in the file /static/images/candy/ + photoname.ext
To add a picture to a new category, you have to put the picture in the file /static/images/category/ + photoname.ext


REQUIREMENTS 
-------------------------------------------------

 - Python 
 - Flask 0.9
 - Flask Login 0.1.3
 - Postegre SQL
 - SQL Alchemy
 - Oauth2Client
 - Werkzeug 0.8.3
 - Bleach

See the pg_config file for installation command line



INSTALLATION
-------------------------------------------------

1. Run the database_setup file with this command line : 
	python database_setup.py

2. Populated the database with the file lotsofcandies.py and this command line :
	python lotsofcandies.py

3. Run the application with this command line : 
	python application.py

4. The web application will be running at port:5000.
	Open a browser and enter : localhost:5000

5. To add, edit, delete item or categories
	You need to log in with Facebook or Google account


Copyright 2015 - Hugo Boutet Romanowski for Udacity. 