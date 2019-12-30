'''Database models package.

These models describe the underlying database tables, their structure, and
other attributes such as data integrity constraints and validation rules.

Validators are used to enforce a data validation layer before database
constraints take effect on a per-model basis, which can vary depending
on database server backend. (For more info, see nested packages/modules.)
'''

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# model classes depend on the db instance,
# so it must exist before models are imported
db = SQLAlchemy()
migrate = Migrate()
