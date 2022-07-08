from crypt import methods
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import EditProfileForm, EmptyForm, LoginForm, PostForm, ResitrationForm
from app.models import User, Post
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    posts = user.followed_posts()
    return render_template('index.html', title="Home", posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    user login
    '''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
    # if form.validate():
        # query the username
        user = User.query.filter_by(username=form.username.data).first()
        # check the intergr
        if user is None or not user.check_password(form.password.data):
        #(form.password.data):
            flash('Invalid username or password')
            flash(form.errors)
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # redirect to index whne there is no next page
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResitrationForm()
    if form.validate_on_submit():
    # if form.validate():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have successfully registered!')
        return redirect(url_for('login'))
    else:
        flash('Sorry, registion unsuccessful.')
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    '''
    user home page
    '''
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.followed_posts()
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''
    edit username and about me
    '''
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/write_post', methods=['GET', 'POST'])
@login_required
def write_post():
    '''
    post a single post, and then redirect to the user home page
    '''
    form = PostForm()
    if form.validate_on_submit():
        username = current_user.username
        user_id = User.query.filter_by(username=username).first().id
        post = Post(body = form.body.data, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        flash('You have successfully posted!')
        return redirect(url_for('user', username=username))
    return render_template('write_post.html', title='Write A Post', form=form)


@app.route('/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    '''
    enter homepages to follow
    '''
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} is not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself.')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are now following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    '''
    entering users homepages to unfollow
    '''
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} is not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself.')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# TODO: 
''' requires admin rights '''
@app.route('/display')
def display():
    return render_template('display.html', users = User.query.all())

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500