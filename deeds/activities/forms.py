from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ActivityTypeForm(FlaskForm):
    name = StringField("Activity Name", validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField("Save Activity Type")


class ActivityLogForm(FlaskForm):
    logged_on = DateField("Log Date", validators=[DataRequired()], default=date.today)
    activity_type_id = IntegerField("Activity Type", validators=[DataRequired()])
    duration_minutes = FloatField("Duration (minutes)", validators=[Optional(), NumberRange(min=0)])
    distance_km = FloatField("Distance (km)", validators=[Optional(), NumberRange(min=0)])
    weight_kg = FloatField("Weight (kg)", validators=[Optional(), NumberRange(min=0)])
    sets = IntegerField("Sets", validators=[Optional(), NumberRange(min=0)])
    reps = IntegerField("Reps", validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save Log")
