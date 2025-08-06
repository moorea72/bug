"""
Simple NFT Forms
Clean implementation without field conflicts
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class SimpleNFTForm(FlaskForm):
    """Simple NFT form with essential fields only"""
    collection_id = SelectField('Collection', coerce=int, validators=[DataRequired()])
    name = StringField('NFT Name', validators=[DataRequired(), Length(max=100)])
    image_file = FileField('Upload Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files allowed!')
    ])
    price = FloatField('Price (USDT)', validators=[DataRequired(), NumberRange(min=0)])
    is_verified = BooleanField('Verified (Blue Tick)', default=False)
    blue_tick_file = FileField('Blue Tick PNG', validators=[
        FileAllowed(['png'], 'Only PNG files allowed!')
    ])
    is_active = BooleanField('Active', default=True)
    submit = StringField('Submit')