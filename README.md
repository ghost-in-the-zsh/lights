# Lights

A "simple" Flask-based web application that allows you to manage lights and their on/off power states.

This is a relatively simple project for demo purposes. It's intended to show a practical and working example of how you can architect a software system in a way that allows it to grow more easily while reducing the likelihood of major refactoring efforts down the road. The application is architected as follows:

* Reverse HTTP proxy for SSL/TLS encryption
* RESTful API service
* Web-GUI service (WIP)
* Business logic
* Database backend

Some micro-services are still a **Work In Progress** and are marked as such in this file.

Each service container is defined by its own `<service>.Dockerfile` under the `docker/` directory and orchestrated by the `docker-compose.yaml` file in the project's root directory.

The project's structure and organization will appear overkill for such a simple system, but it's intended to work as a template or reference guide of sorts for your own larger projects, whether hobby or professional.


## Micro-Services (Summary)

A brief description of the micro-services is next.


### Reverse HTTP Proxy

The reverse HTTP proxy service is responsible for providing SSL/TLS encryption and security for client-server connections using HTTPS. The application itself is not responsible for encrypting communication over the network. We use well-established methods and protocols for this purpose for one simple reason: "Rolling out your own crypto" is a dumb idea and you will do it wrong.

The reverse proxy passes client requests along to the API service in the backend


### RESTful API

A publicly exposed service responsible for implementing the system's functionality. It implements the necessary logic to handle HTTP requests, its different methods (e.g. `GET`, `POST`, etc.), and client responses. It uses JSON as the data transfer format and is intended to be human and machine readable.


### Web-GUI Service (WIP)

The human and browser-friendly view of the system using HTML, CSS, and JavaScript. This part of the system is expected to rely on JavaScript to handle requests between the client and the server. This is important because HTML forms do not support HTTP methods beyond `GET` and `POST`, making operations like `DELETE` impossible from it when specifically trying to contact the API. In other words, the following:

```html
<form ... method="delete">
    ...
</form>
```

will not work as expected because it is not valid HTML5.


### Business Logic

This is a server-side layer of the system and implements some application functionality, mostly the CRUD operations, in a way that avoids proliferating database knowledge throughout the rest of the code base. It also makes it easier to fix issues when they arise, particularly in the handling of database queries, exceptions that may need handling, etc.


### Database Backend

A PostgreSQL database server used through an ORM (Object-Relational Mapper) implemented by the SQLAlchemy library.


## Usage and Examples

This is a short example of how you can use the REST API.

```bash
$ curl -k -X GET https://localhost/api/v0/lights/ 2>/dev/null | python3 -m json.tool
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

For HTTP headers only use the `-I` option:

```bash
$ curl -k -I -X GET https://localhost/api/v0/lights/
HTTP/1.1 200 OK
Date: Thu, 09 Jan 2020 09:31:24 GMT
Server: Apache/2.4.41 (Unix) OpenSSL/1.1.1d
Content-Type: application/json
Content-Length: 117
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
Creating lights-api ... done
Creating lights-proxy ... done
```

This will generate the docker images used to instantiate your containers and launch the containers in the background. You can verify their current state with `docker ps` and `docker logs <service-name>`. When successful, you can find the application at https://localhost/api/v0/lights.


### Cleanup Containers

To destroy the containers, images, volumes, networks, etc., run:

```bash
$ docker-compose down --rmi all -v
Stopping lights-proxy ... done
Stopping lights-api   ... done
Stopping lights-db    ... done
Removing lights-proxy ... done
Removing lights-api   ... done
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
Removing image lights-api:latest
Removing image lights-proxy:latest
```

Remove the `-v` option to preserve volumes and avoid losing data.
