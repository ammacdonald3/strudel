from flask import Flask, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests

from app import db
from app.auth import bp

from app.models import App_User

from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm

from app.auth.password_reset import send_password_reset_email


# Define route for login page
@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    google_login_uri = current_app.config['GOOGLE_LOGIN_URI']
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Native login
    form = LoginForm()
    if form.validate_on_submit():
        app_email = form.app_email.data.lower()
        app_user = App_User.query.filter_by(app_email=app_email).first()
        if app_user is None or not app_user.check_password(form.password.data):
            error = 'Invalid email or password'
            return render_template('auth/login.html', title='Sign In', form=form, error=error)
        login_user(app_user, remember=form.remember_me.data)
        app_user.native_authenticated=True
        db.session.flush()
        db.session.commit()
        return redirect(url_for('main.index'))

    # Google account login
    elif 'credential' in request.form:
        print("-------------------")
        print("Credential in form")
        print("-------------------")

        try:
            token = request.form['credential']

            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), google_client_id)

            print("ID-INFO")
            print(idinfo)

            # ID token is valid. Get the user's Google Account information from the decoded token.
            user_id = idinfo['sub']
            given_name = idinfo['given_name']
            family_name = idinfo['family_name']
            user_full_name = idinfo['name']
            user_email = idinfo['email']
            user_pic = idinfo['picture']
            email_ver = idinfo['email_verified']

            # Check to see if user's Google email address is already a registered user
            existing_user = (db.session.query(App_User).filter_by(app_email=user_email).first())

            if existing_user is None:
                app_user = App_User(
                    first_name=given_name,
                    last_name=family_name,
                    google_id=user_id,
                    app_email=user_email,
                    insert_datetime=datetime.now(),
                    google_authenticated=True
                    )
                db.session.add(app_user)
                db.session.commit()
                flash('Congratulations, you are now a registered user!')
                login_user(app_user)
                next_page = url_for('main.index')
                return redirect(next_page)

            else:
                app_user = existing_user
                login_user(app_user)
                next_page = url_for('main.index')
                existing_user.google_authenticated=True
                existing_user.google_id=user_id
                db.session.flush()
                db.session.commit()
                return redirect(next_page)

        except ValueError as valerror:
            # Invalid token
            print(str(valerror))

    else:
        print("------------------------")
        print("Login completely failed")
        print("------------------------")

    return render_template('auth/login.html', title='Sign In', form=form, google_login_uri=google_login_uri, google_client_id=google_client_id)


# Define route for logout functionality
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# Define route for registration page
@bp.route('/register', methods=['GET', 'POST'])
def register():
    google_login_uri = current_app.config['GOOGLE_LOGIN_URI']
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    # Google account registration
    if 'credential' in request.form:
        try:
            token = request.form['credential']
            
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), google_client_id)

            # ID token is valid. Get the user's Google Account information from the decoded token.
            user_id = idinfo['sub']
            given_name = idinfo['given_name']
            family_name = idinfo['family_name']
            user_full_name = idinfo['name']
            user_email = idinfo['email']
            user_pic = idinfo['picture']
            email_ver = idinfo['email_verified']
            
            # Check to see if user's Google email address is already a registered user
            existing_user = (db.session.query(App_User).filter_by(app_email=user_email).first())

            if existing_user is None:

                app_user = App_User(
                    first_name=given_name,
                    last_name=family_name,
                    google_id=user_id,
                    app_email=user_email,
                    insert_datetime=datetime.now(),
                    google_authenticated=True
                    )
                db.session.add(app_user)
                db.session.commit()
                flash('Congratulations, you are now a registered user!')
                login_user(app_user)
                next_page = url_for('main.index')
                return redirect(next_page)

            else:
                app_user = existing_user
                login_user(app_user)
                next_page = url_for('main.index')
                existing_user.google_authenticated=True
                existing_user.google_id=user_id
                db.session.flush()
                db.session.commit()
                return redirect(next_page)

        except ValueError:
            # Invalid token
            pass

    # Native registration
    elif form.validate_on_submit():
        app_email=form.app_email.data

        # Check to see if user is already registered
        existing_user = (db.session.query(App_User).filter_by(app_email=app_email).first())

        if existing_user is None:
            app_user = App_User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                app_email=form.app_email.data.lower(),
                insert_datetime=datetime.now(),
                native_authenticated=True
            )

            app_user.set_password(form.password.data)
            db.session.add(app_user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            login_user(app_user)
            next_page = url_for('main.index')
            return redirect(next_page)

        else:
            # Return an error modal if the user's email is already registered
            error = "Your email has already been registered. Please login or reset your password."
            print(error)

            return render_template('auth/register.html', title='Register', form=form, error=error, google_login_uri=google_login_uri, google_client_id=google_client_id, show_error_modal=True)

    
    return render_template('auth/register.html', title='Register', form=form, google_login_uri=google_login_uri, google_client_id=google_client_id, show_error_modal=False)


# Define route for password reset page
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = App_User.query.filter_by(app_email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


# Define route for password reset form
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = App_User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)