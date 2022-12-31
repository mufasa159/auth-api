# Auth API

**Contents**
- [Setup Local Dev Environment](#setup-local-dev-environment)
- [Connect to Database](#connect-to-database)
- [Backlog](#backlog)

---

## Setup Local Dev Environment

### Step 1: Basics
Open terminal or shell. Go to the root directory of this project.
```
cd auth-api
```

Install PDM if you don't already have it.
Installation instructions can be found [here](https://pdm.fming.dev/latest/).

Run the following command to install the dependency packages.
```
pdm install
```

Activate virtual environment by running:
```
pdm venv activate
```

You can use PDM to add any libraries to the project.  
There is no need to worry about creating or activating your virtual environment.


### Step 2: The Environment Variables
Get `.env` file from one of the devs working on the project to connect to database and place in server's root directory.  

The `DB_URL` variable needs to be updated using Heroku Postgres config data, for which you need to be the collaborator in Heroku project. There are 2 ways to get the URL.

1. Go to Heroku website > login to your account > go to `exibit-me` > select `settings` tab > in "Config Vars" section click `Reveal Config Vars` button > Copy `DATABASE_URL` value and paste it in `DB_URL` env variable.
2. Install `Heroku Cli` on your machine > run `heroku login` > authenticate via browser > run `heroku config:get DATABASE_URL -a exibit-me`

For `JWT_SECRET` in `.env` file, you can regenerate new secret using the following command:
```
openssl rand -hex 32
```

### Step 3: Running the API Server
Start API server using the following command:
```
pdm run uvicorn main:app --reload  
```

FastAPI uses Swagger UI to display all the API routes and test them. Once the server is running, go to `127.0.0.1:8000/docs` (or wherever it's running at + `/docs`) to see the UI version of API.

---

## Connect to Database

We're using Postgres for storing user data while their respective media files are being stored somehwere else.  

Ideally there should be a separate database for development, but currently everything is done in the main database. The main configs you need to connect to db is in `.env` file. Once you run the API server, it should automatically connect to Postgres DB based on the configs in `.env` file.    

But if you want to connect to database separately using terminal, Google how to do that. Or, you may use the following apps to interact with the database:
- [Postico](https://eggerapps.at/postico/) (Simple UI/UX)
- [PgAdmin4](https://www.pgadmin.org/)

If you want, you can set up you own local database too. The original schema for database can be found at `/server/db/schema.sql`. If you're using local database, make sure to update your environment variables in `.env` file.

---

## Backlog

- [ ] User authentication implementation
   - [x] Role-based access to certain routes
   - [x] Handling bearer token and refresh token
   - [x] Protect routes using `auth_wrapper`
   - [ ] Review and Test
- [ ] Dockerize the entire project
- [ ] Separate Authentication code and Classes from `main.py`
- [ ] Organize folder structure
- [ ] Make functions asynchronous
- [ ] Replace psycopg2 with asyncpg