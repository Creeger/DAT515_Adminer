from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask.helpers import url_for
from . import db
from flask_login import  login_required, current_user
from . models import BlogPost, User, Comment

views = Blueprint('views', __name__)

@views.route('/')
def home():
    posts = db.session.query(BlogPost).order_by(BlogPost.post_id.desc())
    users = db.session.query(User).all()
    return render_template("home.html", posts = posts, user=current_user, users = users)

@views.route('/create_post')
@login_required
def create_post():
    return render_template("create_post.html", user=current_user)