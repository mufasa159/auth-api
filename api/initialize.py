from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config
from auth import AuthHandler
from config import settings
import asyncpg


env = Config("../.env")
auth_handler = AuthHandler()
app = FastAPI(
   title = "Authentication API",
   description = "Authentication API for user accounts management built with FastAPI and JWT tokens",
   version = "2.1",
   contact = {
      "name"  : "mufasa159",
      "url"   : "https://mufasa.cc",
      "email" : "hello@mufasa.cc",
   },
   license_info = {
      "name"  : "MIT-0",
      "url"   : "https://opensource.org/license/mit-0/",
   },
   docs_url="/docs",
   redoc_url="/redoc",
)
app.add_middleware(
   CORSMiddleware,
   allow_origins=settings.allowed_hosts,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)


async def connection():
   return await asyncpg.connect(
      user     = env("DB_USER"), 
      password = env("DB_PASS"), 
      database = env("DB_NAME"), 
      host     = env("DB_HOST"),
      port     = env("DB_PORT"),
      ssl      = "require",
   )


@app.on_event("startup")
async def startup():
   app.state.db = await connection()


@app.on_event("shutdown")
async def shutdown():
   await app.state.db.close()