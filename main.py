import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request
import requests
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash,request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import forms from the forms.py
from forms import CreatePostForm,CreateLoginForm,CreateRegisterForm,CommentForm


# Use the variables in your app
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap5(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# OpenWeatherMap API Key (Use your own key)
WEATHER_API_KEY = os.getenv('API_KEY')

# Sample Itineraries (JSON format)
itineraries = {
    "paris": ["Day 1: Eiffel Tower & Louvre", "Day 2: Notre Dame & Seine River", "Day 3: Versailles Palace"],
    "new york": ["Day 1: Times Square & Central Park", "Day 2: Statue of Liberty & Brooklyn", "Day 3: Empire State Building"]
}
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods=['GET','POST'])
def register():
    form = CreateRegisterForm()
    if form.validate_on_submit():
        password = request.form.get('password')
        email = form.email.data
        print(email)
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash('You already sighned up with this email , log-in instead')
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        name = request.form.get('name')
        email = request.form.get('email')
        
        new_user = User(
            name = name,
            email = email,
            password = hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template("register.html",form = form,logged_in = current_user.is_authenticated)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login',methods=['GET','POST'])
def login():
    form = CreateLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Password incorrect! Please try again')
                return redirect(url_for('login'))
        else:
            flash("You have not log-in using this email.Please try again or Register")
            return redirect(url_for('login'))
    return render_template("login.html",form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Itinerary Generator
@app.route('/itinerary', methods=['POST'])
def itinerary():
    city = request.form['city'].lower()
    plan = itineraries.get(city, ["No itinerary found. Try another city!"])
    return render_template('itinerary.html', city=city.title(), plan=plan)

# Weather API
@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']
    
    try:
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses (e.g., 404)

        city_info = response.json()
        if not city_info:
            return render_template('weather.html', weather={"error": "City not found!"})

        lat, lon = city_info[0]['lat'], city_info[0]['lon']
        
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()

        weather_data = weather_response.json()
        return render_template('weather.html', weather={
            "city": city.title(),
            "temperature": weather_data["main"]["temp"],
            "condition": weather_data["weather"][0]["description"].title()
        })

    except requests.exceptions.RequestException as e:
        return render_template('weather.html', weather={"error": f"API Error: {str(e)}"})

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")
if __name__ == '__main__':
    app.run(debug=True)
