#!/usr/bin/env python

from flask import Flask, render_template, request, make_response
from flask import redirect, jsonify, url_for, flash, Response, json
from flask import session as login_session
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
import bleach
import random
import string
import json
import requests
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from database_setup import Base, Category, Candy, Pagination, User

app = Flask(__name__)

CLIENT_ID = json.loads(
     open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog"

# Connect to Database and Create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Number of items per pages for pagination
PER_PAGE = 8


# Simple Pagination on some pages
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Facebook connection
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.2/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.2/me?%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    ''' The token must be stored in the login_session in order to
    properly logout, let's strip out the information before the
    equals sign in our token '''
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius:\
        50px;-webkit-border-radius: 50px;-moz-border-radius: 50px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output


# Disconnect function for facebook
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s%s/permissions'\
          % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Function to connect with facebook
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is \
                                 already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; \
              border-radius: 150px;-webkit-border-radius: 150px;\
              -moz-border-radius: 150px; margin:auto;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# PAGES TEMPLATES
# CATEGORIES - PAGES

# Show Home Page
@app.route('/')
def homePage():
        return render_template('home.html')


@app.route('/category')
def showCategories():
    # Return All Categories of Candies
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('category.html', categories=categories)

    elif 'username' in login_session:
        return render_template('privatecategory.html', categories=categories)

    else:
        return render_template('category.html', categories=categories)


# API for Category pages - convert to JSON
@app.route('/category/json')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Pages to VIEW an individual category
# If connected see the private page with the options
@app.route('/view/category/<int:category_id>')
def seeOneCategory(category_id):
    seeCategory = session.query(Category).filter_by(id=category_id).one()
    candies = session.query(Candy).filter(Candy.category_id ==
                                          category_id).all()

    if 'username' in login_session:
        return render_template('viewcategoryprivate.html',
                               category=seeCategory,
                               candies=candies)
    else:
        return render_template('viewcategory.html', category=seeCategory,
                               candies=candies)


# Page to EDIT a category, must be connected
@app.route('/edit/category/<int:category_id>', methods=['GET', 'POST'])
def editCategory(category_id):
    # Select to category to edit
    editCategory = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        flash("You must be connected to edit a category.")
        return redirect('/login')

    if request.method == 'POST':

        if request.form['name']:
            editCategory.name = request.form['name']

        if request.form['description']:
            editCategory.description = request.form['description']

        session.commit()
        return redirect(url_for('showCategories'))

    elif 'username' in login_session:
        return render_template('editCategory.html', category=editCategory)

    else:
        flash("You must be connected to edit a category.")
        return redirect('/login')


# Page to ADD a new category, must be connected
@app.route('/new/category', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        flash("You must be connected to add a new category")
        return redirect('/login')

    if request.method == 'POST':
        # Clean the data before adding to the database
        newCategory = Category(name=bleach.clean(request.form['name']),
                               description=bleach.clean
                               (request.form['description']),
                               image=bleach.clean(request.form['image']))
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))

    elif 'username' in login_session:
        return render_template('newCategory.html')

    else:
        flash("You must be connected to add a new category")
        return redirect('/login')


# Page to DELETE a category, must be connected
@app.route('/delete/category/<int:category_id>', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()

    if 'username' not in login_session:
        flash("You must be connected to delete a category")
        return redirect('/login')

    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash("Category has been deleted")
        return redirect(url_for('showCategories'))

    elif 'username' in login_session:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)

    else:
        flash("You must be connected to delete a category")
        return redirect('/login')


# CANDIES - PAGES
# Page to see ALL candies in one page
@app.route('/candy', defaults={'page': 1})
@app.route('/candy/page/<int:page>')
def showCandies(page):
    # Count the number of Candies for the pagination
    count = session.query(Candy).count()
    # Set the offset by page for the pagination
    if page == 1:
        # Starting with the first element(0)
        OffsetLimit = page - 1
    else:
        OffsetLimit = (page - 1) * PER_PAGE

    # Return the 5 worst candies
    if request.args.get('orderby') == 'worst':
        query = session.query(Candy, Category)\
            .filter(Candy.category_id == Category.id)\
            .order_by(desc(Candy.cavity)).limit(5)\
            .all()
        # If showPagination = 0 then hide it
        showPagination = 0

    # Return the 5 best candies
    elif request.args.get('orderby') == 'good':
        query = session.query(Candy, Category)\
            .filter(Candy.category_id == Category.id)\
            .order_by(asc(Candy.cavity)).limit(5)\
            .all()
        showPagination = 0

    # Return every candies with a score between 5-8
    elif request.args.get('orderby') == 'bad':
        query = session.query(Candy, Category)\
            .filter(Candy.category_id == Category.id, Candy.cavity >= 5,
                    Candy.cavity <= 8)\
            .order_by(desc(Candy.cavity)).limit(PER_PAGE)\
            .all()
        showPagination = 0

    # Return the query by category
    elif request.args.get('orderby') == 'categories':
        query = session.query(Candy, Category)\
            .filter(Candy.category_id == Category.id)\
            .order_by(asc(Category.name)).limit(PER_PAGE)\
            .offset(OffsetLimit).all()
        # If showPagination = 1 then show it
        showPagination = 1

    # Return the query by cavity score
    elif request.args.get('orderby') == 'cavity':
        query = session.query(Candy, Category)\
            .filter(Candy.category_id == Category.id)\
            .order_by(asc(Candy.cavity)).limit(PER_PAGE)\
            .offset(OffsetLimit).all()
        showPagination = 1

    # Select the right amount of candies per page
    else:
        query = session.query(Candy, Category)\
            .filter(Candy.category_id == Category.id)\
            .order_by(asc(Candy.name)).limit(PER_PAGE)\
            .offset(OffsetLimit).all()
        showPagination = 1

    # Set the pagination with this function
    pagination = Pagination(page, PER_PAGE, count)

    if 'username' not in login_session:
        return render_template('candies.html', pagination=pagination,
                               query=query, showPagination=showPagination)

    elif 'username' in login_session:
        return render_template('privatecandies.html', pagination=pagination,
                               query=query, showPagination=showPagination)

    else:
        return render_template('candies.html', pagination=pagination,
                               query=query, showPagination=showPagination)


# API for category pages - JSON
@app.route('/candy/json')
def candyJSON():
    candies = session.query(Candy).all()
    return jsonify(candies=[r.serialize for r in candies])


# Pages to VIEW an individual candy
# If connected show the private page with the options
@app.route('/view/candy/<int:candy_id>')
def seeOneCandy(candy_id):
    seeCandy = session.query(Candy).filter_by(id=candy_id).one()

    if 'username' not in login_session:
        return render_template('viewCandy.html', candy=seeCandy)

    elif 'username' in login_session:
        return render_template('privateviewCandy.html', candy=seeCandy)

    else:
        return render_template('viewCandy.html', candy=seeCandy)


# Pages to ADD an individual candy, must be connected
@app.route('/new/candy', methods=['GET', 'POST'])
def AddCandy():
    if 'username' not in login_session:
        flash("You must be connected to add a candy.")
        return redirect('/login')

    if request.method == 'POST':
        newCandy = Candy(name=bleach.clean(request.form['name']),
                         description=bleach.clean
                         (request.form['description']),
                         image=bleach.clean(request.form['image']),
                         cavity=request.form['points'],
                         category_id=request.form['category'])
        session.add(newCandy)
        session.commit()
        return render_template('viewCandy.html', candy=newCandy)

    elif 'username' in login_session:
        categories = session.query(Category).all()
        return render_template('newCandy.html', categories=categories)

    else:
        flash("You must be connected to add a candy.")
        return redirect('/login')


# Pages to EDIT an individual candy, must be connected
@app.route('/edit/candy/<int:candy_id>', methods=['GET', 'POST'])
def editCandy(candy_id):
    editCandy = session.query(Candy).filter_by(id=candy_id).one()
    cats = session.query(Category).all()

    if 'username' not in login_session:
        flash("You must be connected to edit a candy.")
        return redirect('/login')

    if request.method == 'POST':
        if request.form['name']:
            editCandy.name = bleach.clean(request.form['name'])
        if request.form['description']:
            editCandy.description = bleach.clean(request.form['description'])
        if request.form['cavity']:
            editCandy.cavity = request.form['cavity']
            return redirect(
                url_for('seeOneCandy', candy_id=editCandy.id))

    elif 'username' in login_session:
        return render_template('editCandy.html', candy=editCandy,
                               categories=cats)

    else:
        flash("You must be connected to edit a candy.")
        return redirect('/login') 


# Page to DELETE a candy, must be connected
@app.route('/delete/candy/<int:candy_id>', methods=['GET', 'POST'])
def deleteCandy(candy_id):
    candyToDelete = session.query(Candy).filter_by(id=candy_id).one()

    if 'username' not in login_session:
        flash("You must be connected to delete a candy.")
        return redirect('/login')

    if request.method == 'POST':
        session.delete(candyToDelete)
        session.commit()
        flash("Candy has been deleted")
        return redirect(url_for('showCandies'))

    elif 'username' in login_session:
        return render_template('deleteCandy.html',
                               candy=candyToDelete)

    else:
        flash("You must be connected to delete a candy.")
        return redirect('/login')


# USERS - PAGES
# See your profil
@app.route('/profil')
def seeProfil():
    if 'provider' in login_session:
        return render_template('profil.html',
                               picture=login_session['picture'],
                               name=login_session['username'],
                               email=login_session['email'])
    else:
        flash("You were not logged in")
        return redirect(url_for('homePage'))


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('homePage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('homePage'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
