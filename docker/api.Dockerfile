FROM python:3-alpine

LABEL maintainer="Raymond L. Rivera <ray.l.rivera@gmail.com>"

# Container environment
ENV USER=light
ENV HOME=/var/www/lights
ENV PATH="${HOME}/.local/bin:${PATH}"
ENV FLASK_ENV=production

# update OS, install dependencies, setup non-root user, etc
RUN apk update && \
    apk upgrade && \
    apk add --update --no-cache build-base python3-dev linux-headers pcre-dev postgresql-dev musl-dev && \
    apk del --purge && \
    python -m pip install --upgrade pip && \
    python -m pip install uwsgi && \
    # -S: system user
    # -D: no password
    # -h: home dir
    # -g: GECOS
    # -G: group
    # -s: shell (ash; there's no bash)
    addgroup -S ${USER} && \
    adduser -S -D -s /bin/ash -h ${HOME} -G ${USER} -g '' ${USER} && \
    # force .local and .cache dirs to be owned by new user to prevent
    # warnings when installing requirements.txt with --user option...
    chown -R ${USER}:${USER} ${HOME}

# drop from root; switch to new user
USER ${USER}:${USER}
WORKDIR ${HOME}

# * the USER command does not apply to COPY, so the --chown option is needed
#   to prevent root ownership;
# * this command does NOT understand ENV vars, so USER must be hard-coded
COPY --chown=light:light ./app/ app
COPY --chown=light:light ./utils/api/ utils
COPY --chown=light:light ./migrations/ migrations
COPY --chown=light:light ./wsgi.py wsgi.py
COPY --chown=light:light ./conf/api/uwsgi.ini conf/uwsgi.ini
COPY --chown=light:light ./requirements.txt requirements.txt

RUN python -m pip install --user --requirement requirements.txt

ENTRYPOINT ["utils/entrypoint.sh"]
CMD ["conf/uwsgi.ini"]
