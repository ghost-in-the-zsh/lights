'''Commands for application management.'''

from sys import exit
from os import environ

from invoke import task


# For the containers to work as expected, the environment variables below
# *MUST* be properly defined in the shell session where commands are
# being run. See docs and the `app.settings` module for more details.
REQUIRED_VARS = (
    'POSTGRES_PASSWORD',
    'LIGHTS_HOST',
    'LIGHTS_PORT',
    'LIGHTS_DB',
    'LIGHTS_USER',
    'LIGHTS_PASSWORD'
)


@task
def setup(c):
    '''(Re-)Build and launch the whole system.

    This command (re-)builds images and launches the containers that host
    the application. It also ensures that required environment variables
    are properly defined as a pre-requisite.
    '''
    for var in REQUIRED_VARS:
        if not environ.get(var, None):
            print(f'Required environment variable is not defined: {var}')
            print(f'For example (Bash): export {var}=<your-value-here>')
            print('Setup will now abort.')
            exit(1)

    c.run('docker-compose up --build -d')


@task(
    optional=['keep_data'],
    help={
        'keep_data': 'Whether to keep or remove data volumes (default: `False`).'
    }
)
def teardown(c, keep_data=False):
    '''Stop and destroy the whole system and (optionally) its data.

    This command stops containers, removes images, and destroys the data
    volumes created during setup and used by the application during exe-
    cution.
    '''
    command = 'docker-compose down --rmi all'
    if not keep_data:
        command += ' -v'

    c.run(command)
