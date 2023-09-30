from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, escape
from flask.wrappers import Request
from sqlalchemy.orm import session
from sqlalchemy.orm.query import Query
from werkzeug.exceptions import BadRequest, BadRequestKeyError
from .models import BlogPost, User, Comment, Login
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask import jsonify


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        captcha = request.form.get("capt")
        input_captcha = request.form.get("textinput")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password_hash, password) is True and captcha == input_captcha and input_captcha is not None:
                flash('Logged in to the most secure blog ever!',
                      category='success')
                login_user(user, remember=False)
                next = request.args.get('user/'+user.urlSlug)
                ip_address = request.remote_addr
                log_user(userId=user.get_id(), ipaddress=ip_address)

                return redirect(next or url_for('views.home'))
            else:
                flash('Ai, incorrect passsword, email or captcha lad!',
                      category='error')
        else:
            flash('Ai, incorrect passsword, email or captcha lad!', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out!', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    data = request.form
    if request.method == "POST":
        allowed_chars = "abcdefghijklmnopqrstuvwxyzæøå1234567890.!@_-/()[]{}?|§<>#£¤$%&=+``*'¨^"
        hashed_pswrd = generate_password_hash(
            escape(request.form.get("password")), method="pbkdf2:sha256")
        username = escape(request.form.get("username"))
        first_name = escape(request.form.get("first_name"))
        last_name = escape(request.form.get("last_name"))
        email = escape(request.form.get("email"))
        password = escape(request.form.get("password"))
        password_confirm = escape(request.form.get("password_confirm"))
        date_created = datetime.now()
        descriptiom = "No description yet"
        urlSlug = username
        avatar = None

        user = User(username=username, email=email, password_hash=hashed_pswrd, first_name=first_name,
                    last_name=last_name, description=descriptiom, avatar=avatar, date_created=date_created, urlSlug=urlSlug)

        if not ((2 < len(first_name) <= 30) and (allowed_characters(allowed_chars, first_name))):
            flash(
                f"First name must be within 3 and 30 chars and contain any of these chars: [{allowed_chars}]", "error")

        elif User.query.filter_by(username=username).first() != None:
            flash(f"This username is already in use", "error")

        elif User.query.filter_by(email=email).first() != None:
            flash(f"This email is already in use", "error")

        elif not ((2 < len(last_name) <= 30) and (allowed_characters(allowed_chars, first_name))):
            flash(
                f"Last name must be within 3 and 30 chars and contain any of these chars: [{allowed_chars}]", "error")

        elif not allowed_characters(allowed_chars, email):
            flash(
                f"Email may only contain any of these chars: [{allowed_chars}]", "error")

        elif password != password_confirm:
            flash("Passwords must be matching!", "error")

        elif not allowed_characters(allowed_chars, password):
            flash(
                f"Password may only contain following characters [{allowed_chars}]", "error")

        elif len(password) <= 12 or len(password) >= 64:
            flash(f"Password must be between 12 and 64 characters", "error")
        else:
            flash("Account created with superb extreme security!",
                  category="success")
            db.session.add(user)
            db.session.commit()

    return render_template("sign_up.html", user=current_user)


@auth.route('/user/<urlSlug>', methods=['GET'])
def user(urlSlug):  # Changed function name so that "Your Posts" page will work
    user = db.session.query(User).filter_by(urlSlug=urlSlug).first()
    if user != None:
        blogs = db.session.query(BlogPost).filter_by(
        user_id=str(user.get_id())).order_by(BlogPost.post_id.desc())
        comments = db.session.query(Comment).all()
        users = db.session.query(User).all()
        return render_template("blog.html", urlSlug=urlSlug, posts=blogs, user=user, comments = comments, users = users, current_user = current_user)
    else:
        abort(404)


@auth.route('/user/<urlSlug>/new', methods=["GET", 'POST'])
@login_required
def new(urlSlug):
    if request.method == 'POST':
        if urlSlug == current_user.urlSlug:
            user_id = current_user.get_id()
            title = request.form.get("title")
            escape(title)
            summary = request.form.get("summary")
            escape(summary)
            url_slug = title.replace(" ", "_")
            date_created = datetime.now()
            updated_at = datetime.now()
            content = request.form.get("content")
            escape(content)

            post = BlogPost(user_id=user_id, title=title, summary=summary,
                            created_at=date_created, updated_at=updated_at, url_slug=url_slug, content=content)

            if 0 <= len(title) >= 100:
                flash(f"Title cant be empry or longer than 100 characters", "error")
            elif 0 <= len(summary) >= 500:
                flash(f"Summary cant be empry or longer than 500 characters", "error")
            elif 0 <= len(content) >= 5000:
                flash(f"Content cant be empry or longer than 5000 characters", "error")
            else:
                flash("Post created, very secure, very nice", category="success")
                db.session.add(post)
                db.session.commit()
                blogs = db.session.query(BlogPost).filter_by(
                    user_id=str(current_user.get_id())).order_by(BlogPost.post_id.desc())
                comments = db.session.query(Comment).all()
            users = db.session.query(User).all()
            return render_template("blog.html", urlSlug=urlSlug, posts=blogs, user=current_user, comments = comments, users = users, current_user = current_user)
        else:
            abort(401)
    return render_template("create_post.html", user=current_user)


@auth.route('/user/<urlSlug>/<post_id>/delete', methods=['POST'])
@login_required
def delete(urlSlug, post_id):
    if request.method == 'POST':
        if urlSlug == current_user.urlSlug:
            blogpost = db.session.query(
                BlogPost).filter_by(post_id=int(post_id))
            if blogpost.first().user_id == current_user.get_id():
                flash("Post deleted, very secure, very nice", category="success")
                db.session.delete(blogpost.first())
                db.session.commit()
                blogs = db.session.query(BlogPost).filter_by(
                    user_id=str(current_user.get_id())).order_by(BlogPost.post_id.desc())
                comments = db.session.query(Comment).all()
                users = db.session.query(User).all()
                return render_template("blog.html", urlSlug=urlSlug, posts=blogs, user=current_user, comments = comments, users = users, current_user = current_user)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(400)


@auth.route('/user/<urlSlug>/<post_id>/edit', methods=["GET", 'POST'])
@login_required
def edit(urlSlug, post_id):
    if request.method == 'POST':
        if urlSlug == current_user.urlSlug:
            blogpost = db.session.query(
                BlogPost).filter_by(post_id=int(post_id))
            if blogpost.first() != None:
                if blogpost.first().user_id == current_user.get_id():
                    title = request.form.get("title")
                    escape(title)
                    summary = request.form.get("summary")
                    escape(summary)
                    updated_at = datetime.now()
                    content = request.form.get("content")
                    escape(content)

                    

                    if 0 <= len(title) >= 100:
                        flash(f"Title cant be empry or longer than 100 characters", "error")
                    elif 0 <= len(summary) >= 500:
                        flash(
                        f"Summary cant be empry or longer than 500 characters", "error")
                    elif 0 <= len(content) >= 5000:
                        flash(
                        f"Content cant be empry or longer than 5000 characters", "error")
                    else:
                        flash("Post updated, very secure, very nice",
                          category="success")
                        blogpost.update(
                        {"title": title, "summary": summary, "updated_at": updated_at, "content": content})
                        db.session.commit()
                        blogs = db.session.query(BlogPost).filter_by(
                        user_id=str(current_user.get_id())).order_by(BlogPost.post_id.desc())
                        comments = db.session.query(Comment).all()
                        users = db.session.query(User).all()
                        return render_template("blog.html", urlSlug=urlSlug, posts=blogs, user=current_user, comments=comments, users=users, current_user = current_user)
                else:
                    abort(404)
            else:
                abort(400)
        else:
            abort(401)
    else:
        abort(400)
# Checks if all characters in target_string exists in allowed_chars.


def allowed_characters(allowed_chars: str, target_string: str):
    if all(character in allowed_chars for character in target_string.lower()):
        return True
    return False

def log_user(userId, ipaddress):
    last_login_log = db.session.query(Login).filter_by(user_id=userId).order_by(Login.login_id.desc()).first()
    last_login_date = datetime.now()
    if(last_login_log != None):
        last_login_date = last_login_log.login_time
    
    new_log = Login(user_id=userId, last_login=last_login_date, login_time=datetime.now(),ip_address=ipaddress)
    db.session.add(new_log)
    db.session.commit()
    

@auth.route('/user/<urlSlug>/<post_id>/create_comment', methods=['POST'])
@login_required
def create_comment(post_id, urlSlug):
    if request.method == 'POST':
        text=request.form.get('text')
        user = db.session.query(User).filter_by(urlSlug=urlSlug).first()
        if user != None:
            post = db.session.query(BlogPost).filter_by(post_id=post_id).first()
            if post == None:
                abort(404)
            if not text:
                flash('Comment cannot be empty.', category='error')
                blogs = db.session.query(BlogPost).filter_by(
                    user_id=str(user.get_id())).order_by(BlogPost.post_id.desc())
                comments = db.session.query(Comment).all()
                users = db.session.query(User).all()
                return render_template("blog.html", urlSlug=urlSlug, posts=blogs, user=current_user, comments = comments, users = users, current_user = current_user)
            else:
                comment = Comment(
                text=text, user_id=current_user.get_id(), blog_post_id=post_id, created_at = datetime.now(), updated_at = datetime.now())
                db.session.add(comment)
                db.session.commit()
                blogs = db.session.query(BlogPost).filter_by(
                    user_id=str(user.get_id())).order_by(BlogPost.post_id.desc())
                comments = db.session.query(Comment).all()
                users = db.session.query(User).all()
                return render_template("blog.html", urlSlug=urlSlug, posts=blogs, user=current_user, comments = comments, users = users, current_user = current_user)
        else:
            abort(404)
    else:
        abort(400)

@auth.route('/user/<urlSlug>/<post_id>/<comment_id>/delete_comment', methods=['POST'])
@login_required
def delete_comment(urlSlug, post_id, comment_id):
    if request.method == 'POST':
        user = db.session.query(User).filter_by(urlSlug=urlSlug).first()
        if user == None:
            abort(404)
        post = db.session.query(BlogPost).filter_by(post_id=post_id).first()
        if post == None:
            abort(404)
        comment = db.session.query(Comment).filter_by(comment_id = comment_id).first()
        if comment == None:
            abort(404)
        if(comment.user_id == current_user.get_id()):
            flash("Comment deleted, very secure, very nice", category="success")
            db.session.delete(comment)
            db.session.commit()
            user = db.session.query(User).filter_by(urlSlug=urlSlug).first()
            blogs = db.session.query(BlogPost).filter_by(
                    user_id=str(user.get_id())).order_by(BlogPost.post_id.desc())
            comments = db.session.query(Comment).all()
            users = db.session.query(User).all()
            return render_template("blog.html", urlSlug=urlSlug, posts=blogs, user=current_user, comments = comments, users = users, current_user = current_user)
        else:
            abort(402)
    else:
        abort(400)
