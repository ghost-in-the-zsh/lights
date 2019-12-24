'''Commands for automated unit tests.'''

from invoke import task


COMMAND = 'FLASK_ENV=testing coverage run -m pytest -vv --disable-pytest-warnings --verbose'


@task
def all(c):
    '''Run all available unit tests.'''
    c.run(f'{COMMAND} tests/')


@task
def models(c):
    '''Run the set of unit tests, but only for data models.'''
    c.run(f'{COMMAND} tests/models')


@task
def services(c):
    '''Run the set of unit tests, but only for the services layer.'''
    c.run(f'{COMMAND} tests/services')
