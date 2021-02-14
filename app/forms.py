from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, email_validator, ValidationError
from app.models import Users


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already taken')

#login form

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

#update account form

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])] )
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already taken')

class BookTicketForm(FlaskForm):
    mychoices = [
        ('Abia',	'Umuahia'),
        ('Adamawa',	'Yola'),
        ('Akwa Ibom',	'Uyo'),
        ('Anambra',	'Awka'),
        ('Bauchi',	'Bauchi'),
        ('Bayelsa',	'Yenogua'),
        ('Benua',	'Markurdi'),
        ('Borno', 'Maiduguri'),
        ('Cross River',	'Calabar'),
        ('Delta',	'Asaba'),
        ('Ebonyi',	'Abakaliki'),
        ('Edo',	'Benin City'),
        ('Ekiti',	'Ado Ekiti'),
        ('Enugu',	'Enugu'),
        ('Gombe',	'Gombe'),
        ('Imo',	'Owerri'),
        ('Jigawa',	'Dutse'),
        ('Kaduna',	'Kaduna'),
        ('Kano',	'Kano'),
        ('Katsina',	'Katsina'),
        ('Kebbi',	'Birnin Kebbi'),
        ('Kogi',	'Lokoja'),
        ('Kwara',	'Ilorin'),
        ('Lagos',	'Ikeja'),
        ('Nasarawa',	'Lafia'),
        ('Niger',	'Minna'),
        ('Ogun',	'Abeokuta'),
        ('Ondo',	'Akure'),
        ('Osun',	'Oshogbo'),
        ('Oyo',	'Ibadan'),
        ('Plateau',	'Jos'),
        ('Rivers',	'Port Harcourt'),
        ('Sokoto',	'Sokoto'),
        ('Taraba',	'Jalingo'),
        ('Yobe',	'Damaturu'),
        ('Zamfara',	'Gusau'),
        ('FCT',	'Abuja')
    ]
    take_off = SelectField('Take Off Point', choices = mychoices, validators=[DataRequired()])
    destination = SelectField('Destination', choices = mychoices, validators=[DataRequired()])
    date_of_flight = DateField('Date Of Flight', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Book Ticket')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Search')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email does not exist. Please register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')