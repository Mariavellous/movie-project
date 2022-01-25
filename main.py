from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

# Create a new SQLlite database with SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chick-flick-collection.db'
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


#create a table in this database called "movie"
class Movie(db.Model):
    # These are the different fields with respective limitations
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String, nullable=False)

db.create_all()

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
# db.session.add(new_movie)
# db.session.commit()

class MovieForm(FlaskForm):
    movie_rating = StringField(label='Your Rating Out of 10 e.g. 6.9', validators=[DataRequired()])
    movie_review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')


@app.route("/")
def home():
    movies = Movie.query.all()
    print(movies)
    return render_template("index.html", movies=movies)


@app.route("/edit/<int:movie_id>", methods=['GET', 'POST'])
def edit(movie_id):
    movie_form = MovieForm()
    movie_to_update = Movie.query.get(movie_id)
    if movie_form.validate_on_submit():
        try:
            is_string = False
            if 0 <= float(movie_form.movie_rating.data) <= 10:
                movie_to_update.rating = movie_form.movie_rating.data
                movie_to_update.review = movie_form.movie_review.data
                db.session.commit()
                return redirect(url_for('home'))
        except ValueError:
            is_string = True
        if is_string:
            return render_template("edit.html", movie_form=movie_form, movie=movie_to_update)
    return render_template("edit.html", movie_form=movie_form, movie=movie_to_update)


@app.route("/delete/<int:movie_id>", methods=['GET'])
def delete(movie_id):
    if request.method == 'GET':
        movie_to_delete = Movie.query.get(movie_id)
        db.session.delete(movie_to_delete)
        db.session.commit()
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
