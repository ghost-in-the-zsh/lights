'''The top-level GUI views module.

Views act as a presentation layer that decides how data is presented to
the users. Views make use of forms and HTML templates in order to present
data for given routes.
'''

from flask import render_template
from flask_classful import (
    FlaskView,
    route
)

from .light import LightView


class HomeView(FlaskView):
    '''View for the application's home page.'''

    @route('/', methods=['GET'], endpoint='gui.home.index')
    def index(self):
        return render_template('common/index.html')

    @route('/about', methods=['GET'], endpoint='gui.home.about')
    def about(self):
        return render_template('common/about.html')
