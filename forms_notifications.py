from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()], render_kw={"rows": 4})
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
    submit = SubmitField('Save Notification')

class AdminSalaryPlanForm(FlaskForm):
    plan_name = StringField('Plan Name', validators=[DataRequired(), Length(max=100)])
    referrals_required = IntegerField('Referrals Required', validators=[DataRequired(), NumberRange(min=0)])
    balance_required = FloatField('Balance Required', validators=[DataRequired(), NumberRange(min=0)])
    monthly_salary = FloatField('Monthly Salary', validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Plan')