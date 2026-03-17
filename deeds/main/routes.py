import random
from flask import render_template, request, Blueprint
from flask_login import current_user, login_required

from deeds.models import Goal

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html")

@main.route("/about")
def about():
    return render_template('about.html', title='About')

