#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
# import dateutil.parser
import sys
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from dateutil.parser import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:collins1844@localhost:5432/mydatabase'


migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))

    artists = db.relationship('Artist', secondary='shows')
    shows = db.relationship('Show', backref='venues')
    
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))

    venues = db.relationship('Venue', secondary='shows')
    shows = db.relationship('Show', backref='artists')
    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship('Venue' , lazy=True)
    artist = db.relationship('Artist' , lazy=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
   # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.order_by(Venue.state,Venue.city).all()
    data = []
    tmp = {}
    prevcity = None
    prevstate = None
    for venue in venues:
       venuedata = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.today(),
                                                  venue.shows)))
        }
       if venue.city == prevcity and venue.state == prevstate:
            tmp['venues'].append(venuedata)
       else:
            if prevcity is not None:
                data.append(tmp)
            tmp['city'] = venue.city
            tmp['state'] = venue.state
            tmp['venues'] = [venuedata]
       prevcity = venue.city
       prevstate = venue.state
    data.append(tmp)
    return render_template('pages/venues.html', areas=data) 
         
  
 

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(
      Venue.name.islike('%{}%'.format(search_term))).all()

  venue_list = []
  for venue in venues:
    dic = {}
    dic['id'] = venue.id
    dic['name'] = venue.name
    dic['num_upcoming_shows'] = len(venue.shows)
    venue_list.append(dic)

    response = {
    "count":len(venue_list),
    "data": venue_list
    }
   

    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
   # TODO: replace with real venue data from the venues table, using venue_id
   # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)

    upcoming_shows = list(filter(lambda x: x.start_time >=
                                 datetime.today(), venue.shows))
    past_shows = list(filter(lambda x: x.start_time <
                             datetime.today(), venue.shows))
   

    past_shows = list(map(lambda x: x.show_artist(), past_shows))
    upcoming_shows = list(map(lambda x: x.show_artist(), upcoming_shows))

    data = venue.to_dict()
    data['upcoming_shows'] = upcoming_shows
    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

 

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
   error = False
   try:
    seeking_talent = False
    if 'seeking_talent' in request.form:
       seeking_talent = request.form['seeking_talent'] == 'y'
    venue = Venue()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website_link = request.form.get('website_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.seeking_talent = seeking_talent
    venue.seeking_description = request.form.get('seeking_description')
    db.session.add(venue)
    db.session.commit()
   except:
     error = True
     print(sys.exc_info())  
     db.session.rollback()
   finally:
        db.session.close()
        if error:
             # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occurred.  Venue ' +
                  request.form['name'] + ' Could not be listed!')
        else:
             # on successful db insert, flash success
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
   return render_template('pages/home.html')   
  
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue= Venue.query.get(venue_id)
  db.session.delete(venue)
  db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


@app.route('/delete-venue', methods=['POST'])
def deletevenue():
  venueId =  request.get_json()['venue_id']
  venue = Venue.query.get(venueId)
  db.session.delete(venue)
  db.session.commit()
  return redirect(url_for('/home'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data =  artists=Artist.query.all()
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  search_results = Artist.query.filter(
        Artist.name.like('%{}%'.format(search_term))).all()  

  response = {}
  response['count'] = len(search_results)
  response['data'] = search_results

  return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))
 

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  past_shows = list(filter(lambda x: x.start_time <
                             datetime.today(), artist.shows))  #Anoymouse function that filters past shows
  upcoming_shows = list(filter(lambda x: x.start_time >=
                                 datetime.today(), artist.shows))

  past_shows = list(map(lambda x: x.show_venue(), past_shows))
  upcoming_shows = list(map(lambda x: x.show_venue(), upcoming_shows))  #Anoymouse function that filters upcoming shows

  data = artist.to_dict()
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows'] = upcoming_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

 
 
  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        artist.genres = ','.join(tmp_genres)
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website = request.form['website']
        artist.seeking_venue = request.form['seeking_venue']
        artist.seeking_description = request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
  except:
        error = True
        db.session.rollback()
  finally:
        db.session.close()
        if error:
            return redirect(url_for('server_error'))
        else:
            return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
   # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  error = False
  try:
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      venue.genres = ','.join(request.form.getlist('genres'))  
      venue.facebook_link = request.form['facebook_link']
      venue.image = request.form['image_link']
      venue.website_link = request.form['website_link']
      venue.seeking_talent = request.form['seeking_talent']
      venue.seeking_description = request.form['seeking_description']
      db.session.add(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
      if error:
          flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated.')
      else:
          flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))
 

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  error = False
  try:
    seeking_venue = False
    if 'seeking_venue' in request.form:
       seeking_venue = request.form['seeking_venue'] == 'y'

    artist = Artist()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.website_link = request.form.get('website')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.seeking_venue = seeking_venue
    artist.seeking_description = request.form.get('seeking_description')
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())  
    db.session.rollback()
       
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:

    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = request.form['start_time']
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
     flash('An error occurred. Show could not be listed.')
    else:
     flash('Show was successfully listed!')
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
