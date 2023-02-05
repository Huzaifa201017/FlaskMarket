import flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField , RadioField , DateField , SelectField,FloatField ,TextAreaField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired , ValidationError 
from market import connection

class RegisterForm(FlaskForm):
    def validate_email_address(self, email_address_to_check):
        conn  = connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute('SELECT Top 1 email FROM [User] where email = %s' ,email_address_to_check.data )
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        if data:
            raise ValidationError('Email Address already exists! Please try a different email address')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    dob = DateField(label="Date of Birth" , format='%Y-%m-%d' )
    options = RadioField('Category', choices = ['Seller', 'Customer'])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    email = StringField(label='Email:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class PurchaseItem(FlaskForm):
    submit = SubmitField(label='Buy')

class InfoItem(FlaskForm):
    submit = SubmitField(label='Done')

class AddProduct(FlaskForm):
    name=StringField(label='Product Name', validators=[DataRequired()])
    description=TextAreaField(label='Description', validators=[DataRequired()])
    barcode=StringField(label='Barcode', validators=[Length(min=12, max=12),DataRequired()])
    grossprice=FloatField(label='Price To Sell', validators=[DataRequired()])
    stockquantity=IntegerField(label='Quantity', validators=[DataRequired()])
    conn  = connection()
    cursor = conn.cursor()

    cursor.execute("select categoryName from Category")

    categoryLst = []
    for row in cursor:
        categoryLst.append(row[0])
    
    cursor.close()
    conn.close()
    category=SelectField('Category', choices= categoryLst, validators=[DataRequired()])
    submit = SubmitField(label='Sell')

class PlaceOrder(FlaskForm):
    submit = SubmitField(label='Place Order')
    
