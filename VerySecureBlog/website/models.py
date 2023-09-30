from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey, create_engine, func

#eksempel på et database table
#dette e ikkje sqlite, men sqlalchemy!
class User(UserMixin,db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128),unique=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    description = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(150), nullable=True)
    date_created = db.Column(db.DateTime)
    urlSlug = db.Column(db.String(150), unique=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)

    def get_id(self):
        return (self.user_id)

class Login(db.Model):
    login_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey(User.user_id))
    last_login = db.Column(db.DateTime)
    login_time = db.Column(db.DateTime)
    ip_address = db.Column(db.String(150))

class BlogPost(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey(User.user_id))
    title = db.Column(db.String(150))
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    url_slug = db.Column(db.String(150))
    content = db.Column(db.Text)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)

class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    blog_post_id = db.Column(db.Integer, ForeignKey(BlogPost.post_id))
    user_id = db.Column(db.Integer, ForeignKey(User.user_id))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, nullable=True)


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(150), unique=True)
    url_slug = db.Column(db.String(150), unique=True)

class PostCategory(db.Model):
    post_category_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, ForeignKey(BlogPost.post_id))
    category = db.Column(db.Integer, ForeignKey(Category.category_id))

