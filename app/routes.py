from flask_login import current_user, login_required, login_user, logout_user
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import LoginForm, ResitrationForm
from app.models import User, Post


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
    ]
    return render_template('index.html', title="Home", posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
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

# TODO: 
''' requires admin rights '''
@app.route('/display')
def display():
    return render_template('display.html', users = User.query.all())