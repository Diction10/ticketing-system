import secrets
import os
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt, mail
from sqlalchemy import func
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, BookTicketForm, SearchForm, RequestResetForm, ResetPasswordForm
from app.models import Users, Flights
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



# Dummy data
# flights = [
#     {
#         'passenger': 'Rasheed Amolegbe',
#         'take_off': 'Ibadan',
#         'destination': 'Abuja',
#         'ticket_num': '001',
#         'date_of_flight': 'March 01, 2021'
#     },

#     {
#         'passenger': 'Fola Amolegbe',
#         'take_off': 'Ibadan',
#         'destination': 'Canada',
#         'ticket_num': '002',
#         'date_of_flight': 'March 02, 2021'
#     }
# ]



#set route
@app.route('/home', methods=['GET', 'POST'])
def home():
    # num_users = db.session.query(Users.username, func.count(Users.username)).group_by(Users.username).all()
    # num_users = db.session.query(Users.username, func.count(Users.username)).all()
    users = db.session.query(func.count(Users.username)).scalar()
    # session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
   
    tickets = db.session.query(func.count(Flights.take_off)).scalar()

    # date = datetime.date().now
    #today's date
    date = datetime.today().strftime('%Y-%m-%d')    
    return render_template('home.html', title='Home Page', users=users, tickets=tickets, date=date)


@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data, first_name=form.first_name.data, 
                last_name=form.last_name.data, email=form.email.data.lower(), password=hashed)
        #add user
        db.session.add(user)
        #commit user
        db.session.commit()

        flash(f'You have successfully registered { form.username.data }', 'success')

        #send message to user email
        message = Message(f'You have been registered {form.first_name.data}.', sender=os.environ('EMAIL_USER'), recipients=[form.email.data])
        message.body = f''' You are welcome {form.username.data}. Thanks for using our Ticketing service.
'''
        mail.send(message)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/',  methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login Successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))          
        else:
            flash('Login Unsuccessful!, please check your email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



def save_picture(form_picture):
    #to generate random image name for picture
    random_hex = secrets.token_hex(8)
    #to grab the file extensio
    _, f_ext = os.path.splitext(form_picture.filename)

    #to get the full filename and extension
    picture_name = random_hex + f_ext

    #to set where to store the updated profile pictures
    picture_path = os.path.join(app.root_path, 'static/profile', picture_name)

    #to resize pictures before saving
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)


    #to save
    i.save(picture_path)
    #return filename
    return picture_name


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            #to set user picture to the newly updated picture
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    form=BookTicketForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            if form.take_off.data != form.destination.data:
                flight = Flights(take_off=form.take_off.data, destination=form.destination.data, 
                date_of_flight=form.date_of_flight.data, user_id=current_user.id)
                db.session.add(flight)
                db.session.commit()
                flash('You have succesfully booked a ticket.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Please choose a diiferent destination', 'danger')
    return render_template('book.html', form=form)

@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    flights = Flights.query.filter_by(user_id = current_user.id).all()
    return render_template('history.html',title='Flight History', flights=flights )
    # if request.method == 'POST':
    #     user = request.form.get('search')
    #     return redirect(url_for('search'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    return render_template('search.html', title='Search Page')



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=os.environ('EMAIL_USER'),
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then please ignore this email.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)



@app.route('/contact')
def contact():
    return render_template('contactus.html', title='Contact Us')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html', title='Calendar')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', title='Gallery')

@app.route('/latest')
def latest():
    return render_template('latest.html', title='Latest News')