from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, IntegerField, DecimalField, SelectField, TextField, FileField
from wtforms.validators import Required, Email, EqualTo, Length, Regexp, ValidationError
from market.models import User
import re

class ProductForm(FlaskForm):
    name = StringField("Name", validators=[Required(message='Required - Name'), Length(min=5, max=50, message="Name should be minimum 5 characters")], render_kw={"placeholder":"iphone x"})
    price = DecimalField("Price", validators=[Required(message='Required - Price')], render_kw={"placeholder":"xxx.xx"})
    barcode = IntegerField("Barcode", validators=[Required(message='Required - Barcode')], render_kw={"placeholder":"00000000"})
    image = FileField("Image File")#, validators=[Regexp(".*\\.(png|jpg|gif|bmp)", message='File extension should be one of png, jpg, gif, bmp')])
    description = TextField("description")
    submit = SubmitField('Add')

class UserForm(FlaskForm):
    def validate_email(self, email_to_check):
        user = User.query.filter_by(email=email_to_check.data).first()
        if user:
            raise ValidationError('Email already exists! Please try a different email')
    email = StringField("Email", validators=[Required(message='Required - Email'), Email(message='Invalid email format')], render_kw={"placeholder":"example@email.com"})
    name = StringField("Name", validators=[Required(message="Required - Name"), Length(min=3, max=50, message="Name should be minimum 3 characters")], render_kw={"placeholder":"John"})
    password = PasswordField("Password", validators=[Required(message="Input required - Password"), Length(min=5, message="Password should be minimum 5 characters")], render_kw={"placeholder":"*****"})
    confirm = PasswordField("Confirm Password", render_kw={"placeholder":"*****"}, validators=[EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up', render_kw={'class':'btn-primary btn'})

class InfoForm(FlaskForm):
    email = StringField("Email", render_kw={'disabled':'True'})
    name = StringField("Name", validators=[Required(message="Required - Name"), Length(min=3, max=50, message="Name should be minimum 3 characters")])
    budget = StringField("Budget", render_kw={'disabled':'True'})
    submit = SubmitField('Edit', render_kw={'class':'btn-primary btn'})

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Required(message='Required - Email'), Email(message='Invalid email format')], render_kw={"placeholder":"example@email.com"})
    password = PasswordField("Password", validators=[Required(message="Input required - Password"), Length(min=5, message="Password should be minimum 5 characters")], render_kw={"placeholder":"*****"})
    submit = SubmitField("Login", render_kw={'class':'btn-primary btn'})

class SubmitForm(FlaskForm):
    submit = SubmitField('submit')

class DeleteForm(FlaskForm):
    email = StringField("Email", validators=[Required(message='Required - Email'), Email(message='Invalid email format')], render_kw={"placeholder":"example@email.com"})
    password = PasswordField("Password", validators=[Required(message='Required - Password')], render_kw={"placeholder":"*****"})
    submit = SubmitField('Delete Account')
