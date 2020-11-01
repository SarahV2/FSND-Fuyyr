#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# (Done): connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLALCHEMY_TRACK_MODIFICATIONS = False


db = SQLAlchemy(app)
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
    facebook_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy=True)
    # (Done): implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    # (Done): implement any missing fields, as a database migration using Flask-Migrate

# (Done) Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#


def convert_date(date_time_value):

  stringified_date = date_time_value = (
      date_time_value).strftime("%m/%d/%Y, %H:%M:%S")

  return stringified_date
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
    data = [{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # (Done): implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    try:
        search_term = request.form.get('search_term', '')
        search_query = Venue.name.ilike("%{}%".format(search_term))
        search_results = Venue.query.filter(search_query).all()
        if len(search_results) == 0:
            abort(404)
        response = {
            "count": len(search_results),
            "data": search_results
        }
    except:
        print('an error occured')
        flash('Your search did not yeild any results', 'danger')
        abort(404)

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # (Done): replace with real venue data from the venues table, using venue_id

    venueData = Venue.query.get(venue_id)

    if not venueData:
        abort(404)

    pastShows = []
    upcomingShows = []

    shows = venueData.shows
    for show in shows:
      showDetails={
        "artist_id":show.artist_id,
        "artist_name":show.Artist.name,
        "artist_image_link":show.Artist.image_link,
        # Convert show's start time to string to ve able to render it in the html file
        "start_time":convert_date(show.start_time)

      }
      if show.start_time > datetime.now():
        upcomingShows.append(showDetails)
      else:
        pastShows.append(showDetails)

    venueData.upcoming_shows = upcomingShows
    venueData.past_shows = pastShows
    venueData.past_shows_count=len(pastShows)
    venueData.upcoming_shows_count=len(upcomingShows)

    return render_template('pages/show_venue.html', venue=venueData)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    # (Done): modify data to be the data object returned from db insertion
    error = False
    # (Done): insert form data as a new Venue record in the db, instead
    try:
        venue_name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone_number = request.form['phone']
        genres = request.form.getlist('genres')
        website = request.form['website']
        image_link = request.form['image_link']
        seeking_talent = request.form['seeking_talent']
        seeking_description = request.form['seeking_description']
        facebook_link = request.form['facebook_link']
        newVenue = Venue(name=venue_name, city=city, state=state, address=address, phone=phone_number, genres=genres, facebook_link=facebook_link, website=website,
                         image_link=image_link, seeking_talent=eval(seeking_talent), seeking_description=seeking_description)

        print(request.form['name'], file=sys.stderr)
        db.session.add(newVenue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')

    except:
        error = True
        db.session.rollback()
        print('an error occured')
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()

    if error:
        # (Done): on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # (Done): Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info(), file=sys.stderr)
    finally:
        db.session.close()
       # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
       # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # (Done): replace with real data returned from querying the database

    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # (Done): implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    try:
        search_term = request.form.get('search_term', '')
        search_query = Artist.name.ilike("%{}%".format(search_term))
        search_results = Artist.query.filter(search_query).all()
        if len(search_results) == 0:
            abort(404)
        response = {
            "count": len(search_results),
            "data": search_results
        }
    except:
        print('an error occured')
        flash('Your search did not yeild any results', 'danger')
        abort(404)

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given artist_id
    # (Done): replace with real venue data from the venues table, using venue_id
    artistData = Artist.query.get(artist_id)

    if not artistData:
        abort(404)
        
    pastShows = []
    upcomingShows = []

    shows = artistData.shows
    for show in shows:
      showDetails={
        "venue_id":show.venue_id,
        "venue_name":show.Venue.name,
        "venue_image_link":show.Venue.image_link,
        # Convert show's start time to string to ve able to render it in the html file
        "start_time":convert_date(show.start_time)

      }
      if show.start_time > datetime.now():
        upcomingShows.append(showDetails)
      else:
        pastShows.append(showDetails)

    artistData.upcoming_shows = upcomingShows
    artistData.past_shows = pastShows
    artistData.past_shows_count=len(pastShows)
    artistData.upcoming_shows_count=len(upcomingShows)

    return render_template('pages/show_artist.html', artist=artistData)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    # make sure to reflect the previously selected state, genres and venue seeking option on the edit form
    form.state.data = artist.state
    form.seeking_venue.data = artist.seeking_venue
    form.genres.data = artist.genres

    # (Done): populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # (Done): take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error = False

    # (Done): insert form data as a new Artist record in the db, instead
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.website = request.form['website']
        artist.image_link = request.form['image_link']
        artist.seeking_venue = eval(request.form['seeking_venue'])
        artist.seeking_description = request.form['seeking_description']
        artist.facebook_link = request.form['facebook_link']
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
        # (Done): modify data to be the data object returned from db insertion

    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()

    if error:
        flash('Unable to update infomation for ' + request.form['name'])
        print(sys.exc_info())

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    # make sure to reflect the previously selected state, genres and venue seeking option on the edit form
    form.state.data = venue.state
    form.seeking_talent.data = venue.seeking_talent
    form.genres.data = venue.genres
    # (Done): populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # (Done): take values from the form submitted, and update existing
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.website = request.form['website']
        venue.image_link = request.form['image_link']
        venue.seeking_talent = eval(request.form['seeking_talent'])
        venue.seeking_description = request.form['seeking_description']
        venue.facebook_link = request.form['facebook_link']

        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
        # (Done): modify data to be the data object returned from db insertion

    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()

    if error:
        flash('Unable to update infomation for ' + request.form['name'])
        print(sys.exc_info())

    # venue record with ID <venue_id> using the new attributes
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
    error = False
    # (Done): insert form data as a new Artist record in the db, instead
    try:
        artist_name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone_number = request.form['phone']
        genres = request.form.getlist('genres')
        website = request.form['website']
        image_link = request.form['image_link']
        seeking_venue = request.form['seeking_venue']
        seeking_description = request.form['seeking_description']
        facebook_link = request.form['facebook_link']
        newArtist = Artist(name=artist_name, city=city, state=state, phone=phone_number, genres=genres, facebook_link=facebook_link, website=website,
                           image_link=image_link, seeking_venue=eval(seeking_venue), seeking_description=seeking_description)

        print(request.form['name'], file=sys.stderr)
        db.session.add(newArtist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # (Done): modify data to be the data object returned from db insertion

    except:
        error = True
        db.session.rollback()
        print('an error occured')
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()

    if error:
        # (Done): on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real shows data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # (Done): insert form data as a new Show record in the db, instead
    error = False

    try:
        venue_id = request.form['venue_id']
        artist_id = request.form['artist_id']
        start_time = request.form['start_time']

        newShow = Show(venue_id=venue_id, artist_id=artist_id,
                       start_time=start_time)

        db.session.add(newShow)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except:
        error = True
        db.session.rollback()
        print('an error occured')
        print(sys.exc_info(), file=sys.stderr)

    finally:
        db.session.close()

    if error:
        # (Done): on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
