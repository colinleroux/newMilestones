from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed

from deeds.models import Tag


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = HiddenField('Content', validators=[DataRequired()])

    # Multiple select field for tags
    tags = SelectMultipleField('Tags', coerce=int)  # Store tag IDs
    image = FileField('Post Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])  # new fie

    submit = SubmitField('Post')

    # Populate the choices dynamically
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.tags.choices = [(tag.id, tag.name) for tag in Tag.query.all()]


class TagForm(FlaskForm):
    name = StringField('Tag name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Save Tag')
