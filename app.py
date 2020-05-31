#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/fyyur'


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
    genres = db.Column(db.String(120))
    show = db.relationship('Show', backref='venue', lazy=True)
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(500))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    show = db.relationship('Show', backref='artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "Show"
  
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime())
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en') #https://github.com/udacity/FSND/issues/39#issue-603539653

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  citys = db.session.query(Venue.city, Venue.state).distinct()
  data = []
  for city in citys:
    venues = Venue.query.filter_by(city=city.city, state=city.state).all()
    cityData = {
      "city" : city.city,
      "state": city.state,
      "venues": []
    }
    for venue in venues: 
      showByVenue = Show.query.filter_by(venue_id=venue.id).all()
      upcomingShows = []
      counter = 0
      for show in showByVenue:
        if show.start_time > datetime.now():
          counter = counter + 1

      venueData = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": counter
      } 
      cityData['venues'].append(venueData)
      # print (dd)

    # print (xx)
    data.append(cityData)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {
    "data": []
  }
  search_term = request.form.get('search_term')
  searchResults = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  response['count'] = len(searchResults)

  for venue in searchResults:
    showByVenue = Show.query.filter(Show.venue_id==venue.id).all()
    counter = 0
    for show in showByVenue:
      if show.start_time > datetime.now():
        counter = counter + 1
    response['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": counter,
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.strip('}{').split(',') ,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":  venue.seeking_description,
    "website": venue.website
  }
  # showByVenue = Show.query.filter_by(venue_id=venue_id).all()
  showByVenue = db.session.query(Artist.name, Artist.image_link, Show.venue_id, Show.artist_id, Show.start_time).join(Show, Show.artist_id == Artist.id).filter(Show.venue_id == venue_id)
  print (showByVenue[0].name)
  upcomingShows = []
  pastShows = []
  for show in showByVenue:
    if show.start_time > datetime.now():
      upcomingShows.append({
          "artist_id" : show.artist_id,
          "artist_name" : show.name,
          "artist_image_link" : show.image_link,
          "start_time" : format_datetime(str(show.start_time))
      })
    else:
      pastShows.append({
          "artist_id" : show.artist_id,
          "artist_name" : show.name,
          "artist_image_link" : show.image_link,
          "start_time" : format_datetime(str(show.start_time))
      })
  data['past_shows'] = pastShows
  data['past_shows_count'] = len(pastShows)
  data['upcoming_shows'] = upcomingShows
  data['upcoming_shows_count'] = len(upcomingShows)
  # print(data)
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
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
  form = VenueForm()
  error = False
  seeking_talent = False
  if form.seeking_description.data != '':
    seeking_talent = True

  try:
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      website = form.website.data,
      seeking_description = form.seeking_description.data,
      seeking_talent = seeking_talent
    )
    db.session.add(venue)
    db.session.commit()
  except: 
    error = True
    db.seesion.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {
    "data": []
  }
  search_term = request.form.get('search_term')
  searchResults = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  response['count'] = len(searchResults)
  for artist in searchResults:
    showByArtist = Show.query.filter(Show.artist_id==artist.id).all()
    counter = 0
    for show in showByArtist:
      if show.start_time > datetime.now():
        counter = counter + 1
    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": counter,
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data = list(filter(lambda d: d['id'] == artist_id, a))[0]
  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.strip('}{').split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link
  }
  # showByVenue = Show.query.filter_by(artist_id=artist_id).all()
  showByArtist = db.session.query(Venue.name, Venue.image_link, Show.venue_id, Show.artist_id, Show.start_time).join(Show, Show.venue_id == Venue.id).filter(Show.artist_id == artist_id)

  upcomingShows = []
  pastShows = []
  for show in showByArtist:
    venueData = Venue.query.get(show.venue_id)
    if show.start_time > datetime.now():
      upcomingShows.append({
          "venue_id" : show.venue_id,
          "venue_name" : show.name,
          "venue_image_link" : show.image_link,
          "start_time" : format_datetime(str(show.start_time))
      })
    else:
      pastShows.append({
          "venue_id" : show.venue_id,
          "venue_name" : show.name,
          "venue_image_link" : show.image_link,
          "start_time" : format_datetime(str(show.start_time))
      })
  data['past_shows'] = pastShows
  data['past_shows_count'] = len(pastShows)
  data['upcoming_shows'] = upcomingShows
  data['upcoming_shows_count'] = len(upcomingShows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  form.name.data = artist.name
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.image_link.data = artist.image_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  try:    
      artist.name = form.name.data
      artist.phone = form.phone.data
      artist.facebook_link = form.facebook_link.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.image_link = form.image_link.data
      db.session.commit()
  except: 
      db.session.rollback()
  finally:
      db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website.data = venue.website
  form.seeking_description.data = venue.seeking_description
  # form.seeking_talent.data = venue.seeking_talent

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  try: 
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.website = form.website.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    if form.seeking_description.data != '':
      venue.seeking_talent = True
    else: 
      venue.seeking_talent = False
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except:
    db.session.rollback() 
  finally:
    db.session.close()
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
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data
    )
    db.session.add(artist)
    db.session.commit()
  except: 
    error = True
    db.seesion.rollback()
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link":Artist.query.get(show.artist_id).image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  error = False
  try:
    show = Show(
      start_time=form.start_time.data,
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
    )
    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.seesion.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  # e.g., flash('An error occurred. Show could not be listed.')
  # flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
