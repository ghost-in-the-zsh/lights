#!/bin/bash
#
# This script generates a set of self-signed SSL certificates for itself
# and service applications. Certificates are used by Postgres and Apache
# to encrypt in-transit client/server connections.
#
# The Postgres certificate is only needed if you keep the database service
# exposed for remote administration and management using pgAdmin4, which
# allows you to require SSL connections.
#
# NOTE: Postgres and Apache-based services only need the their respective
#       `<service>.crt` and `<service>.key` files. Do NOT include the root
#       CA cert and/or key files in the service containers.
#

# set -x  # echo commands to stdout
set -e  # automatically exit on any error w/o checking every exit code

# IFS = Input Field Separator; save before use and restore afterwards
OLDIFS=${IFS}
IFS=','

HOST=$(hostname)
BASEDIR=$(dirname "${0}")

ROOTCA_CRT=${BASEDIR}/ca.crt
ROOTCA_KEY=${BASEDIR}/ca.key
ROOTCA_PASS=$(openssl rand -base64 128)

# Subject values for SSL certs; change them to whatever you want
# before running this script
CERT_COUNTRY=US
CERT_STATE=YourState
CERT_CITY=YourCity
CERT_ORG=YourOrganization
CERT_ORG_UNIT=YourBusinessUnit
CERT_CNAME=your-domain.tld      # e.g. localhost, app.example.org, etc.


# Callback when exiting, for some cleanup.
function cleanup_atexit {
    IFS=${OLDIFS}
}
trap cleanup_atexit EXIT


# Generate the root CA certificate used to sign the client service certs
# that get generated later. This root CA cert is self-signed, which means
# it won't be trusted by your client programs (e.g. browser). But since
# you generated your own and you're visiting your own local system, you can
# trust the the server actually is who it claims to be. Root CA certs must
# always be kept private; they exist only to sign certs that are lower in
# the "chain of command".
function generate_root_ca_cert {
    local rootca_keypass=${BASEDIR}/rca.pass.key

    rm -f ${ROOTCA_CRT} || true
    rm -f ${ROOTCA_KEY} || true

    # generate a key for our root CA certificate
    openssl genrsa \
        -des3 \
        -passout pass:"${ROOTCA_PASS}" \
        -out ${rootca_keypass} 2048
    openssl rsa \
        -passin pass:"${ROOTCA_PASS}" \
        -in ${rootca_keypass} \
        -out ${ROOTCA_KEY}
    rm ${rootca_keypass}

    # create and self sign the root CA certificate
    openssl req \
        -x509 \
        -new \
        -nodes \
        -key ${ROOTCA_KEY} \
        -sha256 \
        -days 365 \
        -out ${ROOTCA_CRT} \
        -subj "/C=${CERT_COUNTRY}/ST=${CERT_STATE}/L=${CERT_CITY}/O=${CERT_ORG}/OU=${CERT_ORG_UNIT}/CN=${CERT_CNAME}"
}


# Generate the certificates used by the running services. These are the
# ones your client programs (e.g. browser, cURL, wget, etc) actually get
# to see from the servers.
function generate_client_certs {
    local service_name="${1}"
    local filename="${2}"

    local service_csr=${BASEDIR}/${service_name}/${filename}.csr   # cert signing request
    local service_crt=${BASEDIR}/${service_name}/${filename}.crt   # certificate
    local service_key=${BASEDIR}/${service_name}/${filename}.key   # private key
    local service_keypass=${BASEDIR}/${service_name}/${service_name}.pass.key

    # Clean up files to be replaced, if present
    rm -f ${service_csr} || true
    rm -f ${service_crt} || true
    rm -f ${service_key} || true

    # generate a key for our service certificate
    openssl genrsa \
        -des3 \
        -passout pass:"${ROOTCA_PASS}" \
        -out ${service_keypass} 2048
    openssl rsa \
        -passin pass:"${ROOTCA_PASS}" \
        -in ${service_keypass} \
        -out ${service_key}
    rm ${service_keypass}

    # create a certificate signing request for our service, including a
    # subject alternative name
    openssl req \
        -new \
        -key ${service_key} \
        -out ${service_csr} \
        -subj "/C=${CERT_COUNTRY}/ST=${CERT_STATE}/L=${CERT_CITY}/O=${CERT_ORG}/OU=${CERT_ORG_UNIT}/CN=${CERT_CNAME}" \
        -reqexts SAN \
        -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:${HOST},DNS:localhost"))

    # use our CA cert and key to create a signed service certificate from
    # the service's cert signing request
    openssl x509 \
        -req \
        -sha256 \
        -days 365 \
        -in ${service_csr} \
        -CA ${ROOTCA_CRT} \
        -CAkey ${ROOTCA_KEY} \
        -CAcreateserial \
        -out ${service_crt} \
        -extensions SAN \
        -extfile <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:${HOST},DNS:localhost"))

    # remove `rwx` from group and others
    chmod go-rwx ${service_key}
}


# Start
generate_root_ca_cert

# tuple format: service,filename
for tuple in proxy,lights db,postgres; do
    # "Any arguments remaining after option processing are treated as
    # values for the positional parameters and are assigned, in order,
    # to $1, $2, ... $n"[1]
    #
    # [1] See `man builtins` for docs.
    set -- ${tuple}

    # $1 = service name, as per `docker-compose.yaml` file, etc.
    # $2 = cert filename
    generate_client_certs ${1} ${2}
done

exit 0
