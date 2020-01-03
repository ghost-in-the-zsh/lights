# Lights

A "simple" Flask-based web application that allows you to manage lights and their on/off power states.

This is a relatively simple project for demo purposes. It's intended to show a practical and working example of how you can structure your application in a way that allows it to grow more easily while reducing the likelihood of major refactoring efforts down the road. The application is architected as follows:

* RESTful API service
* Web-GUI service
* Business logic
* Database backend

Currently, this is still a **Work In Progress and not yet complete** at this time. This file will receive updates as needed and the repository tagged when necessary.


## RESTful API

A publicly exposed service responsible for implementing the system's functionality. It implements the necessary logic to handle HTTP requests, its different methods (e.g. `GET`, `POST`, etc.), and client responses. It uses JSON as the data transfer format and is intended to be human and machine readable.


## Web-GUI Service

The human and browser-friendly view of the system using HTML, CSS, and JavaScript. This part of the system is expected to rely on JavaScript to handle requests between the client and the server. This is important because HTML forms do not support HTTP methods beyond `GET` and `POST`, making operations like `DELETE` impossible from it when specifically trying to contact the API. In other words, the following:

```html
<form ... method="delete">
    ...
</form>
```

will not work as expected because it is not valid HTML5.


## Business Logic

This is a server-side layer of the application and implements some application functionality, mostly the CRUD operations, in a way that avoids proliferating database knowledge throughout the rest of the application code base.


## Database Backend

A PostgreSQL database server used through an ORM (Object-Relational Mapper) implemented by the SQLAlchemy library.


## Misc.

Each service container is defined by its own `Dockerfile` under the `docker/` directory and orchestrated by the `docker-compose.yaml` file in the project's root directory.

The project's structure and organization will appear overkill for such a simple system, but it's intended to work as a template or reference guide of sorts for your own larger projects, whether hobby or professional.
