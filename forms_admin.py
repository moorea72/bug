from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])
    type = SelectField('Type', choices=[
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error')
    ], default='info')
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create Notification')

class SalaryPlanForm(FlaskForm):
    plan_name = StringField('Plan Name', validators=[DataRequired(), Length(min=1, max=100)])
    referrals_required = IntegerField('Referrals Required', validators=[DataRequired(), NumberRange(min=0)], default=0)
    balance_required = FloatField('Balance Required ($)', validators=[DataRequired(), NumberRange(min=0)], default=0.0)
    monthly_salary = FloatField('Monthly Salary ($)', validators=[DataRequired(), NumberRange(min=0)], default=0.0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Plan')

class SupportResponseForm(FlaskForm):
    trigger_words = StringField('Trigger Words (comma-separated)', validators=[DataRequired(), Length(min=1, max=500)])
    response_text = TextAreaField('Response Text', validators=[DataRequired(), Length(min=1, max=2000)])
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('account', 'Account'),
        ('staking', 'Staking'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('referral', 'Referral'),
        ('technical', 'Technical')
    ], default='general')
    priority = IntegerField('Priority', validators=[DataRequired(), NumberRange(min=0)], default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Response')

class SupportTicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('account', 'Account'),
        ('staking', 'Staking'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('referral', 'Referral'),
        ('technical', 'Technical')
    ], default='general')
    submit = SubmitField('Submit Ticket')

class SupportTicketReplyForm(FlaskForm):
    message = TextAreaField('Reply Message', validators=[DataRequired(), Length(min=1, max=1000)])
    status = SelectField('Status', choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], default='open')
    submit = SubmitField('Send Reply')