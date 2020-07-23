from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from forms import Genres
db = SQLAlchemy(app,session_options={

    'expire_on_commit': False

})

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