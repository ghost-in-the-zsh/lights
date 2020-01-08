FROM httpd:alpine

LABEL maintainer="Raymond L. Rivera <ray.l.rivera@gmail.com>"

COPY ./conf/proxy/lights.conf /usr/local/apache2/conf/httpd.conf
COPY ./conf/proxy/lights-ssl.conf /usr/local/apache2/conf/extra/httpd-ssl.conf

# Run `gen-certs.sh` to generate these.
COPY ./conf/proxy/lights.crt /usr/local/apache2/certs/proxy.crt
COPY ./conf/proxy/lights.key /usr/local/apache2/certs/proxy.key
