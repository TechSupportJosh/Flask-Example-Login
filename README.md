# Flask-Example-Login
Simple repo with boilerplate flask code to provide password authentication.

This is in no way a fully fleshed out login/register system. There is however:
- Proper error messages
- Basic validation on usernames and passwords

Todo List:
- CSRF Protection
- Varying lengths of login (i.e. Remember Me checkbox)

## Example Docker setup
This repo also features 2 docker-compose files, one for development and one for production. The development one features a temporary sqlite database and exposes on port 5000. The production one uses gunicorn and nginx and exposes on port 80. The production one also uses a persistent database, by sharing a folder on the host to use to contain the database - this database (named `flask_app.db`) will be inside the `db` folder in the root folder of the repo.

Development docker-compose (will require elevated permissions):
```
docker-compose up --build
```

Production docker-compose (will require elevated permissions):
```
docker-compose -f ./docker-compose.prod.yml up --build
```

Docker files were modified from https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx.