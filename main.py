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

API_KEY = "2dae2be14e69d38534b342165f01d738"
#create a table in this database called "movie"
class Movie(db.Model):
    # These are the different fields with respective limitations
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.Integer, nullable=True)
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


class AddMovieForm(FlaskForm):
    movie_title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie", validators=[DataRequired()])


@app.route('/add', methods=['GET', 'POST'])
def add():
    addmovie_form = AddMovieForm()
    if request.method == 'POST':
        movie_title = addmovie_form.movie_title.data
        parameters = {
            "api_key": API_KEY,
            "query": movie_title,
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=parameters)
        response.raise_for_status()
        data = response.json()["results"]
        print(data)
        return render_template("select.html", data=data)
    return render_template("add.html", addmovie_form=addmovie_form)


@app.route('/select/<int:movie_id>', methods=['GET', 'POST'])
def select(movie_id):
    if request.method == 'GET':
        # movie_id = requests.args.get("id")
        parameters = {
            # "movie_id": movie_id,
            "api_key": API_KEY
        }
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params=parameters)
        response.raise_for_status()
        data = response.json()
        print(data)
        # Add new movie data in the database
        basic_img_url = "https://image.tmdb.org/t/p/w500"
        new_movie_data = Movie(
            title=data["original_title"],
            year=data["release_date"].split("-")[0],
            description=data["overview"],
            img_url=f"{basic_img_url}{data['poster_path']}",
        )
        db.session.add(new_movie_data)
        db.session.commit()
        # title = data["original_title"]
        # img_url = data["poster_path"]
        # year = data["release_date"].split("-")[0]
        # description = data["overview"]
        return redirect(url_for('home'))
    return render_template("select.html")

if __name__ == '__main__':
    app.run(debug=True)
