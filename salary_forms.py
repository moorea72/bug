"""
Forms for salary system
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class SalaryWalletForm(FlaskForm):
    """Form for setting salary wallet address"""
    wallet_address = StringField('Crypto Wallet Address', 
                                validators=[DataRequired(), 
                                          Length(min=25, max=255, message="Please enter a valid crypto wallet address")])
    network = SelectField('Network', 
                         choices=[('BEP20', 'BEP20 (BSC)'), ('TRC20', 'TRC20 (TRON)')],
                         validators=[DataRequired()])
    submit = SubmitField('Save Wallet Address')

class AdminSalaryApprovalForm(FlaskForm):
    """Form for admin to approve salary withdrawals"""
    status = SelectField('Status',
                        choices=[('approved', 'Approve'), ('rejected', 'Reject')],
                        validators=[DataRequired()])
    transaction_hash = StringField('Transaction Hash (if approved)',
                                  validators=[Optional(), Length(max=255)])
    admin_notes = TextAreaField('Admin Notes',
                               validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Status')