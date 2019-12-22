'''Commands to display cached results and other interesting data.'''

from invoke import task


@task
def coverage(c):
    '''Show a report of unit test coverage.'''
    c.run(r'coverage report -m --include=tests\*.py')
