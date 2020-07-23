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
import sys
from sqlalchemy.dialects import postgresql
import itertools
from datetime import date,datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


# TODO: connect to a local postgresql database
# app.config['SQLALCHEMY_DATABASE_URI']='postgresql://eman:e1@localhost:5434/fyyur'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app,session_options={

    'expire_on_commit': False

})
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=True)
    image_link = db.Column(db.String(500),nullable=True)
    genres = db.Column(postgresql.ARRAY(db.Enum(Genres)),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=True)
    seeking_talent = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(500),nullable=True)
    website =db.Column(db.String(120),nullable=True)
    shows = db.relationship('Show',backref='VShow',lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=True)
    image_link = db.Column(db.String(500),nullable=True)
    genres = db.Column(postgresql.ARRAY(db.Enum(Genres)),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=True)
    seeking_venue=db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(500),nullable=True)
    website =db.Column(db.String(120),nullable=True)
    shows = db.relationship('Show',backref='AShow',lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model) :
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  start_time = db.Column(db.DateTime,nullable=False)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #data =Venue.query.all()
  keys = db.session.query(Venue.city,Venue.state).distinct().all()
  res = db.session.query(Venue.id,Venue.name,Venue.city,Venue.state,db.func.count(Show.id)).outerjoin(Show,Venue.id==Show.id).group_by(Venue.id).all()
  data=[]
  for k in keys:
    obj = {}
    obj["city"] =k.city
    obj["state"]=k.state
    obj["venues"]=[]
    for r in res:
      if r.city == k.city and r.state == k.state :
        ven = {}
        ven['id'] = r.id
        ven['name']=r.name
        ven['num_upcoming_shows'] = r[4]
        obj['venues'].append(ven)
    data.append(obj)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchTerm = request.form.get("search_term")
  search = "%{}%".format(searchTerm.lower())
  data= db.session.query(Venue.id,Venue.name,db.func.count(Show.id)).outerjoin(Show,Venue.id==Show.id).group_by(Venue.id).filter(db.func.lower(Venue.name).like(search)).all()
  response = {}
  response["count"]= len(data)
  response['data']=[]
  for d in data :
    info={}
    info['id']=d.id
    info['name']=d.name
    info['num_upcoming_shows']=d[2]
    response['data'].append(info)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows= db.session.query(Show,Artist).filter_by(venue_id=venue_id).join(Artist).all()
  data={}
  if venue is not None :
    data['id']=venue.id
    data['name']=venue.name
    data['genres']=venue.genres
    data['address']=venue.address
    data['city']=venue.city
    data['state']=venue.state
    data['phone']=venue.phone
    data['website'] = venue.website
    data['facebook_link']=venue.facebook_link
    data['seeking_talent']=venue.seeking_talent
    data['seeking_description']=venue.seeking_description
    data['image_link']=venue.image_link
    data['past_shows']=[]
    data['upcoming_shows']=[]
    past = 0
    upcoming=0
    for s in shows :
      if s.Show.start_time < datetime.now() :
        artist={
          "artist_id": s.Artist.id,
          "artist_name": s.Artist.name,
          "artist_image_link":s.Artist.image_link,
          "start_time": s.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        data['past_shows'].append(artist)
        past += 1
      else :
        artist={
          "artist_id": s.Artist.id,
          "artist_name": s.Artist.name,
          "artist_image_link":s.Artist.image_link,
          "start_time": s.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        data['upcoming_shows'].append(artist)
        upcoming +=1
    data['past_shows_count']=past
    data['upcoming_shows_count']=upcoming
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
    data = {}
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address =request.form.get('address')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        genres =request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website')
        seeking_talent = request.form.get('seeking_talent')
        if seeking_talent == "True":
          seeking_talent = True
        else :
          seeking_talent = False

        seeking_description = request.form.get('seeking_description')
        venue = Venue(name = name,
        city = city,state = state,address =address,phone = phone,image_link = image_link,
        genres =genres,facebook_link = facebook_link,website=website,
        seeking_talent=seeking_talent,seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
        data= venue
        print(data)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
       # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + data.name + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    data = {}
    try:
        venue = Venue.query.get(venue_id)
        data=venue
        db.session.delete(venue)
        db.session.commit()
    except:
        error=True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + data.name + ' could not be Deleted.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + data.name + ' was successfully Deleted!')

   
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists =Artist.query.all()
  data=[]
  for artist in artists :
    obj={}
    obj['id']=artist.id
    obj['name']=artist.name
    data.append(obj)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchTerm = request.form.get("search_term")
  search = "%{}%".format(searchTerm.lower())
  data= db.session.query(Artist.id,Artist.name,db.func.count(Show.id)).outerjoin(Show,Artist.id==Show.id).group_by(Artist.id).filter(db.func.lower(Artist.name).like(search)).all()
  response = {}
  response["count"]= len(data)
  response['data']=[]
  for d in data :
    info={}
    info['id']=d.id
    info['name']=d.name
    info['num_upcoming_shows']=d[2]
    response['data'].append(info)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  shows=db.session.query(Show,Venue).filter_by(artist_id=artist_id).join(Venue).all()
  data={}
  if artist is not None :
    data ={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }
    data['past_shows']=[]
    data['upcoming_shows']=[]
    past = 0
    upcoming=0
    for s in shows :
      if s.Show.start_time < datetime.now() :
        artist={
          "venue_id": s.Venue.id,
          "venue_name": s.Venue.name,
          "venue_image_link":s.Venue.image_link,
          "start_time": s.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        data['past_shows'].append(artist)
        past += 1
      else :
        artist={
          "venue_id": s.Venue.id,
          "venue_name": s.Venue.name,
          "venue_image_link":s.Venue.image_link,
          "start_time": s.Show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }
        data['upcoming_shows'].append(artist)
        upcoming +=1
    data['past_shows_count']=past
    data['upcoming_shows_count']=upcoming 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id): 
  form = ArtistForm()
  artistData = Artist.query.get(artist_id)
  form.genres.default= [(genre.name)for genre in artistData.genres]
  form.state.default=artistData.state
  form.process()
  artist={
    "id": artistData.id,
    "name": artistData.name,
    "genres": artistData.genres,
    "city": artistData.city,
    "state": artistData.state,
    "phone": artistData.phone,
    "website": artistData.website,
    "facebook_link": artistData.facebook_link,
    "seeking_venue": artistData.seeking_venue,
    "seeking_description": artistData.seeking_description,
    "image_link": artistData.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  data = {}
  artist = Artist.query.get(artist_id)
  try:
    artist.name=request.form.get('name')
    artist.genres=request.form.getlist('genres')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.image_link=request.form.get('image_link')
    artist.facebook_link=request.form.get('facebook_link')
    artist.website=request.form.get('website')
    seeking_venue=request.form.get('seeking_venue')
    if seeking_venue == "True":
      artist.seeking_venue = True
      artist.seeking_description=request.form.get('seeking_description')
    else :
      artist.seeking_venue = False
      artist.seeking_description=''
    db.session.commit()
    data= artist
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
        db.session.close()
  if error:
    flash('An error occurred. Artist ' + data.name + ' could not be Edited.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully Edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venueData = Venue.query.get(venue_id)
  form.genres.default= [(genre.name)for genre in venueData.genres]
  form.state.default=venueData.state
  form.process()
  venue={
    "id": venueData.id,
    "name": venueData.name,
    "genres": venueData.genres,
    "address": venueData.address,
    "city": venueData.city,
    "state": venueData.state,
    "phone": venueData.phone,
    "website": venueData.website,
    "facebook_link": venueData.facebook_link,
    "seeking_talent": venueData.seeking_talent,
    "seeking_description": venueData.seeking_description,
    "image_link": venueData.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  data = {}
  venue = Venue.query.get(venue_id)
  try:
    venue.name=request.form.get('name')
    venue.genres=request.form.getlist('genres')
    venue.address=request.form.get('address')
    venue.city=request.form.get('city')
    venue.state=request.form.get('state')
    venue.phone=request.form.get('phone')
    venue.image_link=request.form.get('image_link')
    venue.facebook_link=request.form.get('facebook_link')
    venue.website=request.form.get('website')
    seeking_talent=request.form.get('seeking_talent')
    if seeking_talent == "True":
      venue.seeking_talent = True
      venue.seeking_description=request.form.get('seeking_description')
    else :
      venue.seeking_talent = False
      venue.seeking_description=''
    db.session.commit()
    data= venue
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
        db.session.close()
  if error:
    flash('An error occurred. Venue ' + data.name + ' could not be Edited.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully Edited!')
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
    error = False
    data = {}
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        genres =request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website')
        seeking_venue = request.form.get('seeking_venue')
        if seeking_venue == "True":
          seeking_venue = True
        else :
          seeking_venue = False

        seeking_description = request.form.get('seeking_description')
        artist = Artist(name = name,
        city = city,state = state,phone = phone,image_link = image_link,
        genres =genres,facebook_link = facebook_link,website=website,
        seeking_venue=seeking_venue,seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
        data= artist
        print(data)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    else:
          # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data=[]
  for s in shows:
    venue = Venue.query.get(s.venue_id)
    artist=Artist.query.get(s.artist_id)
    obj={
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    }
    data.append(obj)

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
  error = False
  try:
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time=request.form.get('start_time')
    show=Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:   
    # on successful db insert, flash success
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
