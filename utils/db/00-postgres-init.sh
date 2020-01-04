#!/bin/ash
#
# PostgreSQL 12 init script performs the following tasks for clients:
#
#   1. Create application user/role;
#   2. Create application database; and
#   3. Grant privileges to app user on app database.
#
# Note that migrations are performed by the `api` service and that
# default command options have been omitted.
#
# References:
#
#   https://www.postgresql.org/docs/current/sql-createuser.html
#   https://www.postgresql.org/docs/current/sql-createdatabase.html
#   https://www.postgresql.org/docs/current/sql-grant.html
#   https://www.postgresql.org/docs/current/reference.html
#   https://github.com/docker-library/docs/blob/master/postgres/README.md#initialization-scripts
#

# See Compose file for info on `POSTGRES_*` and other environment vars.
# The `replication` privilege allows user to perform backups.
psql -v ON_ERROR_STOP=1 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t <<SQLEND
    create role ${LIGHTS_USER} with password '${LIGHTS_PASSWORD}' login replication;
    create database ${LIGHTS_DB} with owner ${LIGHTS_USER};
    grant all privileges on database ${LIGHTS_DB} to ${LIGHTS_USER};
SQLEND

exit 0
