# Geo-Serverless API

## Installing and building for development purposes

Requirements:

-   Docker 18.09.0+
-   Docker Compose 1.23.2+

### First Time

If this is the first time running the API for development purposes you'll need to:

1. Copy `.flask.env.tmpl` to `.flask.env` (no settings need to be changed yet)
2. Copy `.geolambda.env.tmpl` to `.geolambda.env` (enter your AWS secrets)

### Running the API

Run `docker-compose up base_flask` to bring up the development version of the API.

You'll now have a nice shiny WFS API available at:

`http://localhost/?COGJ_URL={YOUR_COGJ_S3_URL}&SERVICE=WFS&REQUEST=GetCapabilities&VERSION=1.0.0`

This runs the local dev server provided with Flask (`flask run`) and provides nice things like hot reload. However, in dev testing against QGIS we've noticed a few "Broken pipe" errors that may (unconfirmed yet) break things in QGIS.

### The Nginx option

For that reason you can also run the API with Nginx sitting in front of it and uWSGI running the API.

Run `docker-compose up base_nginx` to bring up the Nginx-ified development version of the API and then use the same URL as above.

## Deploy

WIP.

1. Deploy with Geolambda
2. ...
3. Profit!

### flake8

`flake8 --ignore=E501,E731,W504 cogj/flask/api/`
