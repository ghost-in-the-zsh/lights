# Lights

A "simple" Flask-based web application that allows you to manage lights and their on/off power states.

This is a relatively simple project for demo purposes. It's intended to show a practical and working example of how you can architect a software system in a way that allows it to grow more easily while reducing the likelihood of major refactoring efforts down the road. The application is architected as follows:

* Reverse HTTP proxy for SSL/TLS encryption
* Web service (RESTful API + GUI)
* Business logic
* Database backend

Each service container is defined by its own `<service>.Dockerfile` under the `docker/` directory and orchestrated by the `docker-compose.yaml` file in the project's root directory.

The project's structure and organization will appear overkill for such a simple system, but it's intended to work as a template or reference guide of sorts for your own larger projects, whether hobby or professional.


## Micro-Services (Summary)

A brief description of the micro-services is next.


### Reverse HTTP Proxy

The reverse HTTP proxy service is responsible for providing SSL/TLS encryption and security for client-server connections using HTTPS. The application itself is not responsible for encrypting communication over the network. We use well-established methods and protocols for this purpose for one simple reason: "Rolling out your own crypto" is a dumb idea and you will do it wrong.

The reverse proxy passes client requests along to the web service in the backend.


### RESTful API

A publicly exposed service responsible for implementing the system's functionality. It implements the necessary logic to handle HTTP requests, its different methods (e.g. `GET`, `POST`, etc.), and client responses. It uses JSON as the data transfer format and is intended to be human and machine readable.


### Web-GUI Service

The human and browser-friendly view of the system using HTML, CSS, and JavaScript. This part of the system is expected to rely on JavaScript to handle requests between the client and the server. This is important because HTML forms do not support HTTP methods beyond `GET` and `POST`, making operations like `DELETE` impossible from it when specifically trying to contact the API. In other words, the following:

```html
<form ... method="delete">
    ...
</form>
```

will not work; it is not valid HTML5.


### Business Logic

This is a server-side layer of the system and implements some application functionality, mostly the CRUD operations, in a way that avoids proliferating database knowledge throughout the rest of the code base. It also makes it easier to fix issues when they arise, particularly in the handling of database queries, exceptions that may need handling, etc.


### Database Backend

A PostgreSQL database server used through an ORM (Object-Relational Mapper) implemented by the SQLAlchemy library.


## Usage and Examples

This is a short example of how you can use the REST API.


### Creating Objects: `POST` Requests

To create data, an HTTP `POST` request is to be used.

```bash
$ curl -k -i \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -X POST https://localhost/api/v0/lights/ \
    -d '{"name": "Living Room", "is_powered_on": false}'
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 85
Location: https://localhost/api/v0/lights/1
Server: Werkzeug/0.16.0 Python/3.7.5
Date: Wed, 15 Jan 2020 11:25:38 GMT

{
  "light": {
    "date_created": "2020-02-29T06:56:45+00:00",
    "id": 1,
    "is_powered_on": false,
    "name": "Living Room"
  }
}
```

The URL returned in the HTTP `Location` header shows where you can find the newly created resource.


### Reading Objects: `GET` Requests

To read data, a `GET` request is used. Different endpoints may provide different results. For example, we can get a list of all the objects by using the index URL:

```bash
$ curl -k -i \
    -H 'Accept: application/json' \
    -X GET https://localhost/api/v0/lights/
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 455
Server: Werkzeug/0.16.0 Python/3.7.5
Date: Thu, 16 Jan 2020 08:17:26 GMT

{
  "_meta": {
    "links": [
      {
        "href": "https://localhost/api/v0/lights/",
        "rel": "self"
      }
    ],
    "stats": {
      "total_count": 1
    }
  },
  "lights": [
    {
      "_meta": {
        "links": [
          {
            "href": "https://localhost/api/v0/lights/1",
            "rel": "self"
          }
        ]
      },
      "date_created": "2020-02-29T06:56:45+00:00",
      "id": 1,
      "is_powered_on": false,
      "name": "Living Room"
    }
  ]
}
```

The `_meta` data is provided by the API to make the client's life easier (e.g. programmatic navigation) and uses the `_` prefix to communicate that these data, and its nested children, are not part of the models themselves.

To get a single object, you append the object's ID:

```bash
$ curl -i -k \
    -H 'Accept: application/json' \
    -X GET https://localhost/api/v0/lights/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 239
Server: Werkzeug/0.16.0 Python/3.7.5
Date: Thu, 16 Jan 2020 08:20:48 GMT

{
  "light": {
    "_meta": {
      "links": [
        {
          "href": "https://localhost/api/v0/lights/1",
          "rel": "self"
        }
      ]
    },
    "date_created": "2020-02-29T06:56:45+00:00",
    "id": 1,
    "is_powered_on": false,
    "name": "Living Room"
  }
}
```

For HTTP headers only use the `-I` option instead of `-i`:

```bash
$ curl -k -I \
    -X GET https://localhost/api/v0/lights/
HTTP/1.1 200 OK
Date: Wed, 15 Jan 2020 11:24:17 GMT
Server: Apache/2.4.41 (Unix) OpenSSL/1.1.1d
Content-Type: application/json
Content-Length: 117
```


### Updating Objects: `PUT` Requests

This request allows pre-existing objects to be updated *as a whole*, i.e. they must be *fully*, not partially, replaced. This example shows how to update the light we `POST`ed in the first example.

```bash
$ curl -k \
    -H 'Accept: application/json' \
    -X GET https://localhost/api/v0/lights/1
{
    "light": {
        "_meta": {
            "links": [
                {
                    "href": "https://localhost/api/v0/lights/1",
                    "rel": "self"
                }
            ]
        },
        "date_created": "2020-02-29T06:56:45+00:00",
        "id": 1,
        "is_powered_on": false,
        "name": "Living Room"
    }
}
```

The `PUT` request is structured in the same way as a `POST` request, so the only real change here is the HTTP method/verb used and the object's ID that's included in the path. The JSON string sent as data changes all the object's fields at once.

```bash
$ curl -k \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -X PUT https://localhost/api/v0/lights/1 \
    -d '{"name": "Basement", "is_powered_on": false}'
HTTP/1.0 204 NO CONTENT
Content-Type: application/json
Server: Werkzeug/0.16.0 Python/3.7.5
Date: Thu, 16 Jan 2020 08:07:30 GMT
```

Getting the object again shows that it was updated succesfully:

```bash
$ curl -k \
    -H 'Accept: application/json' \
    -X GET https://localhost/api/v0/lights/1
{
  "light": {
    "_meta": {
      "links": [
        {
          "href": "https://localhost/api/v0/lights/1",
          "rel": "self"
        }
      ]
    },
    "date_created": "2020-02-29T06:56:45+00:00",
    "id": 1,
    "is_powered_on": false,
    "name": "Basement"
  }
}
```


### Deleting Objects: `DELETE` Requests

Objects can be deleted individually, by object ID, or all at once, based on endpoint. For example, to delete all of them, we target the index URL:

```bash
$ curl -i -k \
    -H 'Accept: application/json' \
    -X DELETE https://localhost/api/v0/lights
HTTP/1.0 204 NO CONTENT
Content-Type: application/json
Server: Werkzeug/0.16.0 Python/3.7.5
Date: Thu, 16 Jan 2020 08:33:30 GMT
```

We can confirm they've been deleted.

```bash
$ curl -k \
    -H 'Accept: application/json' \
    -X GET https://localhost/api/v0/lights
{
  "_meta": {
    "links": [
      {
        "href": "https://localhost/api/v0/lights/",
        "rel": "self"
      }
    ],
    "stats": {
      "total_count": 0
    }
  },
  "lights": []
}
```


## Application Setup and Launching

These steps were performed in a GNU+Linux system. If you don't have one, you can create a [VirtualBox](https://www.virtualbox.org/)-based VM and install a distro (e.g. Ubuntu, which is what I used) in there. Installing an OS is not in the scope of this documentation.

TL;DR:

1. Install Docker CE and Docker Compose;
2. Get the sources of this repository;
3. Open a shell inside the project's directory;
4. Define and `export` required environment variables (see below);
5. Run script to generate SSL certificates used by some services;
6. Run `docker-compose up --build -d`
7. Go to https://localhost/api/v0/lights


### Install Docker and Docker Compose

Start out by installing [docker-ce](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and [docker-compose](https://docs.docker.com/compose/install/). The micro-services run within Docker containers for ease of setup and to improve application security. (There're steps for a developer setup for a faster iterative workflow. That may be covered later.)


### Get the Sources

Download the contents of this repository (e.g. `git clone ...`, the compressed archive to extract, etc.) and open a shell inside the project's directory:

```bash
$ cd /path/to/project
```

Whatever this path is, it will be referred as `${ROOT}` from now on.


### Prepare the Environment

The following environment variables *must* be defined in your active shell/session:

```bash
export POSTGRES_PASSWORD=<database-admin-password>

export LIGHTS_HOST=db
export LIGHTS_PORT=5432
export LIGHTS_DB=lights
export LIGHTS_USER=light
export LIGHTS_PASSWORD=<application-password>
```

making sure to replace the `<placeholder>` values for your own and leaving the literals as they are. You must also generate the SSL certificates required by Apache and Postgres. For that, enter the `conf` directory and run the script there:

```bash
$ cd ${ROOT}/conf/
$ ./gen-certs.sh
```

Note that the script uses relative path to write the certs, so you're expected to run it *from within* that directory.


### Launch Containers

From the same session in which the environment variables were `export`ed, and inside the `${ROOT}` directory, run:

```bash
$ docker-compose up --build -d
[...]
Creating lights-db ... done
Creating lights-web ... done
Creating lights-proxy ... done
```

This will generate the docker images used to instantiate your containers and launch the containers in the background. You can verify their current state with `docker ps` and `docker logs <service-name>`. When successful, you can find the application at https://localhost/api/v0/lights.


### Cleanup Containers

To destroy the containers, images, volumes, networks, etc., run:

```bash
$ docker-compose down --rmi all -v
Stopping lights-proxy ... done
Stopping lights-web   ... done
Stopping lights-db    ... done
Removing lights-proxy ... done
Removing lights-web   ... done
Removing lights-db    ... done
Removing network lights-backend
Removing network lights-frontend
Removing volume lights-db-data
Removing volume lights-db-confs
Removing volume lights-postgres-certs
Removing volume lights-proxy-logs
Removing volume lights-proxy-conf
Removing volume lights-proxy-certs
Removing image lights-db:latest
Removing image lights-web:latest
Removing image lights-proxy:latest
```

Remove the `-v` option to preserve volumes and avoid losing data.


## Local Dev Setup

Install PostgreSQL, switch to its account with `sudo -i -u postgres`, and set up the database:

```bash
postgres@pc:~$ psql
postgres=$ create role light with password 'devel' login;
postgres=$ create database lights with owner light;
postgres=$ grant all privileges on database lights to light;
postgres=$ \l
List of databases
Name       |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
-----------+----------+----------+-------------+-------------+-----------------------
lights     | light    | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =Tc/light            +
           |          |          |             |             | light=CTc/light
postgres=$ \q
postgres@pc:~$ exit
```

Create a virtual environment, install the Python packages, export some variables, and apply the database migrations:

```bash
$ sudo apt-get install libpq5 libpq-dev  # optional (to build from source)
$ mkvirtualenv -p python3 lights
$ python3 -m pip install --upgrade pip
$ python3 -m pip install -r requirements.txt
```

Create `instance/.flaskenv` with the following content:

```bash
FLASK_APP=app:create_app('development')
FLASK_ENV=development
```

And `instance/env.sh` with this content:

```bash
export LIGHTS_HOST=localhost
export LIGHTS_PORT=5434     # default port is 5432; yours might be different, depending on your setup
export LIGHTS_DB=lights
export LIGHTS_USER=light
export LIGHTS_PASSWORD=devel
```

Source the above file with `source instance/env.sh` and run the application:

```bash
$ flask db upgrade
$ flask run
Serving Flask app "app:create_app('development')" (lazy loading)
* Environment: development
* Debug mode: on
* Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 364-001-171
```

Other helpful commands you can use:

```bash
$ invoke -l
Available tasks:

app.setup         (Re-)Build and launch the whole system.
app.teardown      Stop and destroy the whole system and (optionally) its data.
report.coverage   Show a report of unit test coverage.
test.all          Run all available unit tests.
test.apis         Run the set of unit tests, but only for the APIs.
test.models       Run the set of unit tests, but only for data models.
test.services     Run the set of unit tests, but only for the services layer.
test.validators   Run the set of unit tests, but only for data validators.
```

For example, to run the full test suite, against an in-memory SQLite3 database, use:

```
$ invoke test.all
============================= test session starts ==============================
platform linux -- Python 3.10.7, pytest-7.2.0, pluggy-1.0.0 -- /home/ray/.virtualenvs/lights/bin/python3
cachedir: .pytest_cache
rootdir: /home/ray/Projects/lights
collecting ... collected 79 items

tests/test_validators.py::TestMinLengthValidator::test_zero_string_length_in_ctor_is_accepted PASSED [  1%]
tests/test_validators.py::TestMinLengthValidator::test_negative_string_length_in_ctor_raises_value_error PASSED [  2%]
[...]
tests/services/test_light_service.py::TestLightService::test_delete_existing_light_is_ok PASSED [ 97%]
tests/services/test_light_service.py::TestLightService::test_delete_non_existent_light_raises_object_not_found_error PASSED [ 98%]
tests/services/test_light_service.py::TestLightService::test_delete_collection_is_ok PASSED [100%]

================== 75 passed, 4 skipped, 3 warnings in 0.74s ===================
```
