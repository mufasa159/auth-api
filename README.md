# Authentication API

**Contents**
- [Setup Local Dev Environment](#setup-local-dev-environment)
- [Connect to Database](#connect-to-database)

---

## Setup Local Dev Environment

**⚠️ Read everything before you proceed. Don't run all the commands you see. Some are just examples.**

### Step 1: Basics
Clone this GitHub repository. Then open terminal or shell and go to the root directory of this project.
```
cd auth-api
```

Install PDM if you don't already have it.
Installation instructions can be found [here](https://pdm.fming.dev/latest/).

Run the following command to install all the dependencies.
```
pdm install
```

You can use PDM to add any packages/libraries to the project if needed. For example: 
```
pdm add requests                        # add requests
pdm add requests==2.25.1                # add requests with version constraint
pdm add requests[socks]                 # add requests with extra dependency
pdm add "flask>=1.0" flask-sqlalchemy   # add multiple dependencies with different specifiers
``` 


### Step 2: The Environment Variables

Copy `.env.example` file in the root directory.
```
cp .env.example .env 
```

Populate the `.env` secrets after [setting up](#connect-to-database) the Postgres database. For the tokens, you can regenerate new secret using the following command:
```
openssl rand -hex 32
```

### Step 3: Running the API Server
Start API server using the following command:
```
cd api
uvicorn main:app --reload  
```

FastAPI uses Swagger UI and ReDoc to display all the API routes and/or test them. Once the server is running locally, go to `/docs` or `/redoc` route to see the API documentation.

---

## Connect to Database

Lookup how to install and run Postgres on your operating system and how to create a Postgres database. After creating a database, run the SQL commands in `/db/schema.sql` to create a new table for the users. Then update the `.env` file with the database credentials.

Once you have the database set up, if you want to connect to the database separately for interaction purposes, you can use the following apps:
- [Postico](https://eggerapps.at/postico/) (Simple UI/UX)
- [PgAdmin4](https://www.pgadmin.org/)

If you wish to use PSQL shell to interact with the DB, search online how to do that.
