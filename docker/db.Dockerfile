FROM postgres:alpine

LABEL maintainer="Raymond L. Rivera <ray.l.rivera@gmail.com>"

COPY --chown=postgres:postgres ./utils/db/00-postgres-init.sh /docker-entrypoint-initdb.d/

# Run `gen-certs.sh` to generate these.
COPY --chown=postgres:postgres ./conf/db/postgres.crt /var/lib/postgresql/certs/postgres.crt
COPY --chown=postgres:postgres ./conf/db/postgres.key /var/lib/postgresql/certs/postgres.key

COPY --chown=postgres:postgres ./conf/db/pg_hba.conf /var/lib/postgresql/pg_hba.conf
