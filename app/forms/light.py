from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    SubmitField,
    BooleanField
)
from wtforms.validators import DataRequired


class LightForm(FlaskForm):
    '''A form to handle `Light` data from a request.

    Generally, form class fields MUST match model field names, particularly
    for the fields that represent data to be stored within the model itself.

    Other form fields, such as submit buttons, are part of the form itself
    and don't need to match anything in the model.

    The form knows how to render itself within a template.
    '''
    id = IntegerField('ID')
    name = StringField('Name', validators=[DataRequired()])
    is_powered_on = BooleanField('Powered On?', validators=[DataRequired()])
    save_button = SubmitField('Save')
    delete_button = SubmitField('Delete', render_kw={
        # assumes Bootstrap Confirmation and Material Icons are installed
        # for the pop-over behavior and the CSS styling respectively
        'data-toggle': 'confirmation',
        'data-btn-ok-label': 'Continue',
        'data-btn-ok-class': 'btn-success',
        'data-btn-ok-icon-class': 'material-icons',
        'data-btn-ok-icon-content': 'check',
        'data-btn-cancel-label': 'STOP!',
        'data-btn-cancel-class': 'btn-danger',
        'data-btn-cancel-icon-class': 'material-icons',
        'data-btn-cancel-icon-content': 'close',
        'data-title': 'Are you sure?',
        'data-content': 'This is permanent and cannot be undone!'
    })
    cancel_button = SubmitField('Cancel')
