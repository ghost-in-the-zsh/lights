# Lights

A simple web-enabled application that allows you to turn a light on and off.

This is a relatively simple project for demo purposes. It's intended to show a working example of a web-based application that is broken down into the following services:

* Web-GUI service
* RESTful API service
* Business logic layer
* Database backend

Each service is defined by its own `Dockerfile` under the `docker` directory and orchestrated by the `docker-compose.yaml` file in the project's root directory.

The project's structure and organization will appear overkill for such a simple system, but it's intended to work as a template or reference for your own larger projects.
