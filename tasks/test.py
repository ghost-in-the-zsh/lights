'''Commands for automated unit tests.'''

from invoke import task


COMMAND = 'FLASK_ENV=testing coverage run -m pytest -vv --disable-pytest-warnings --verbose'


@task
def all(c):
    '''Run all available unit tests.'''
    c.run(f'{COMMAND} tests/')
