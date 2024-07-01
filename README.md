# FastAPI-MySQL-CRUD-API-EXAMPLE
This is an example of a FAST API based API for CRUD Operations on a MYSQL database.

Make sure your mysql database is properly setup, i recommend you go ahead and set up PHP My Admin as well too be able too administrer your database.

This is a basic starting template. You need too configure your mysql backend here, and add some authentication.

Fast API has a very versitle structure easy too get ahold of!

usage - 

pip install -r requierments.txt

uvicorn test:app  ( this setup depends on the name of your main file , uvicorn nameoffile:app 

assuming we want too use https, we will need the proper commands too serve the api

uvicorn test:app --ssl-keyfile ./private.key --ssl-certfile ./certificate.crt --host 0.0.0.0
This is assuming you have your ssl key and cert in the same directory!!!

