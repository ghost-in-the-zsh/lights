#!/bin/ash

config_filepath="${1}"

# Since this new service instance could be a new release, we must make
# sure any outstanding database migrations that may've been added get
# applied before we actually start running. The `api` service has a
# dependency on the `db` service specified in the `docker-compose.yaml`
# file, so the database is expected to be online, as required, by the
# time we get to this point.
#
# We use a retry loop because, while the database container may be online,
# the database itself may not yet be ready to accept connections and fail
# as soon as this one gets started.
while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo "Database migration attempt failed. Retrying in 5 secs..."
    sleep 5
done

exec uwsgi ${config_filepath}
