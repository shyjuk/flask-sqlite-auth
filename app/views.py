"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db
from flask import render_template, request, redirect, url_for, flash, session, logging
from app.forms import UserForm, LoginForm
from passlib.hash import sha256_crypt
from app.models import User
from functools import wraps
# import sqlite3

###
# Routing for your application.
###

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap
   
# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == 'POST':
        # Get Form Fields
        uname = request.form['username']
        password_candidate = request.form['password']

        user = User.query.filter_by(username= uname).first() # Query user row
        if user:
            # Get stored hash
            password = user.password

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = user.username

                flash('You are now logged in', 'success')
                return redirect(url_for('home'))
            else:
                flash('Unknown Username / Password','danger')
                return render_template('login.html', form=login_form)
        else:
            flash('Unknown User','danger')
            return render_template('login.html', form=login_form)

    return render_template('login.html', form=login_form)

    
@app.route('/')
@is_logged_in
def home():
    """Render website's home page."""
    return render_template('home.html')    

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

@app.route('/users')
@is_logged_in
def show_users():
    users = db.session.query(User).all() # or you could have used User.query.all()

    return render_template('show_users.html', users=users)

@app.route('/add-user', methods=['POST', 'GET'])
@is_logged_in
def add_user():
    user_form = UserForm()

    if request.method == 'POST':
        if user_form.validate_on_submit():
            # Get validated data from form
            name = user_form.name.data # You could also have used request.form['name']
            email = user_form.email.data # You could also have used request.form['email']
            username = user_form.username.data # You could also have used request.form['email']
            password = sha256_crypt.encrypt(str(user_form.password.data)) # You could also have used request.form['email']

            # save user to database
            user = User(name, email, username, password)
            db.session.add(user)
            db.session.commit()

            flash('User successfully added')
            return redirect(url_for('show_users'))

    flash_errors(user_form)
    return render_template('add_user.html', form=user_form)

# Delete User
@app.route('/delete_user/<string:user_id>', methods=['POST'])
@is_logged_in
def delete_user(user_id):
    # Query user row
    user = User.query.filter_by(id=user_id).first() 
    # Execute
    db.session.delete(user)
    db.session.commit()

    flash('User Deleted', 'success')

    return redirect(url_for('show_users'))

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    user_form = UserForm()
    if request.method == 'POST' and user_form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # save user to database
        user = User(name, email, username, password)
        db.session.add(user)
        db.session.commit()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('show_users'))
    flash_errors(user_form)
    return render_template('add_user.html', form=user_form)
    
# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
