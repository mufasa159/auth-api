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

You can use PDM to add any libraries to the project.  
There is no need to worry about creating or activating your virtual environment.


### Step 2: The Environment Variables

Copy `.env.example` file in the root directory.
```
cp .env.example .env 
```

Get `.env` secrets from one of the devs working on the project to connect to database.  

For access/refresh tokens in `.env` file, you can regenerate new secret using the following command:
```
openssl rand -hex 32
```

### Step 3: Running the API Server
Start API server using the following command:
```
cd api
pdm run uvicorn main:app --reload  
```

FastAPI uses Swagger UI and ReDoc to display all the API routes and/or test them. Once the server is running locally, go to `/docs` or `/redoc` route to see the API documentation.

---

## Connect to Database

We're using Postgres for storing user data while their respective media files are being stored somehwere else.  

Ideally there should be a separate database for development, but currently everything is done in the main database. The main configs you need to connect to DB is in `.env` file. Once you run the API server, it should automatically connect to PostgreSQL DB based on the configs in `.env` file.    

But if you want to connect to database separately using terminal for interaction purposes, Google how to do that. Or, you may use the following apps:
- [Postico](https://eggerapps.at/postico/) (Simple UI/UX)
- [PgAdmin4](https://www.pgadmin.org/)

If you want, you can set up you own local database, too. The original schema for database can be found at `/db/schema.sql`. If you're using local database, make sure to update your environment variables in `.env` file.
