FROM postgres:alpine

LABEL maintainer="Raymond L. Rivera <ray.l.rivera@gmail.com>"

COPY --chown=postgres:postgres ./utils/db/00-postgres-init.sh /docker-entrypoint-initdb.d/
