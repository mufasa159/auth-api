import os
import psycopg2
import bcrypt
from fastapi import FastAPI, Depends, HTTPException, Query
from dotenv import load_dotenv
from pydantic import BaseModel
from auth import AuthHandler, TokenType
from dataclasses import dataclass

load_dotenv(".env")
app = FastAPI()
auth_handler = AuthHandler()

# database configurations
DB_URL = os.environ.get("DATABASE_URL")
DB_USER = DB_URL.split(':')[1][2:]
DB_DATABASE = DB_URL.split(':')[3].split('/')[1]
DB_HOST = DB_URL.split(':')[2].split('@')[1]
DB_PORT = DB_URL.split(':')[3].split('/')[0]
DB_PASSWORD = DB_URL.split(':')[2].split('@')[0]


# connect to postgres database
def connection():
   return psycopg2.connect(
      database=DB_DATABASE,
      user=DB_USER,
      password=DB_PASSWORD,
      host=DB_HOST,
      port=DB_PORT
   )


# used when creating a new user
class NewUser(BaseModel):
   name_first: str
   name_last: str
   username: str
   email: str
   password: str
   bio: str


# used when logging in
class UserLogin(BaseModel):
   username: str
   password: str
   

# used when getting a user's profile
@dataclass(frozen=True)
class PublicUserProfile(BaseModel):
   username: str
   name_first: str
   name_last: str
   image: str
   bio: str


# used when regenerating tokens
class Token(BaseModel):
   value: str = Query(max_length=128, min_length=128)


# ------------------------------------------------------------------------------
# IMPORTANT REMINDER
# ALWAYS MAKE SURE TO SANITIZE USER INPUTS BEFORE QUERYING THE DATABASE
# ------------------------------------------------------------------------------


@app.get("/")
async def root():
   return {
      "message": "Welcome to Exibit"
   }


@app.get('/users', summary="Get all user accounts data")
def get_users(uid = Depends(auth_handler.auth_wrapper), conn = Depends(connection)):
   try:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM accounts WHERE uid=%s", (uid,))
      current_user = cursor.fetchall()
      current_user_role = current_user[0][4]
      if current_user_role == "admin":
         cursor.execute("SELECT * FROM accounts")
         users = cursor.fetchall()
         conn.commit()
         return users
      else:
         raise HTTPException(status_code=401, detail="You are not authorized to view this page")
   finally:
      conn.close()
      

@app.get('/users/{username}', summary="Get public information of a user account")
def get_users(username: str, conn = Depends(connection)):
   try:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM accounts WHERE username=%s", (username,))
      current_user = cursor.fetchall()
      
      if len(current_user) == 0:
         raise HTTPException(status_code=404, detail="User not found")
      
      current_user_data = PublicUserProfile(
         current_user[0][5],
         current_user[0][1],
         current_user[0][2],
         current_user[0][3],
         current_user[0][8]
      )
      conn.commit()
      return current_user_data
   finally:
      conn.close()


@app.post('/register', summary="Create a new user")
async def register(user_data: NewUser, conn = Depends(connection)):
   # todo:
   # - return msg if username or email already exists
   # - reject weak passwords
   # - check if username is valid
   # - send verification email once registration is complete
   
   try:
      cursor = conn.cursor()
      encrypted_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt(10))
      cursor.execute("INSERT INTO accounts (name_first, name_last, username, email, hash, bio) VALUES (%s, %s, %s, %s, %s, %s);", (user_data.name_first, user_data.name_last, user_data.username, user_data.email, encrypted_password.decode('utf8'), user_data.bio))
      conn.commit()
      raise HTTPException(status_code=201, detail="User created successfully")
   finally:
      conn.close()


@app.post('/login', summary="Login to an account")
async def login(user_data: UserLogin, conn = Depends(connection)):
   try:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM accounts WHERE username = %s;", (user_data.username,))
      user = cursor.fetchall()
      conn.commit()

      if len(user) == 0:
         return {"message": "User doesn't exist"}

      isCorrectPassword = user[0][7].encode('utf-8') == bcrypt.hashpw(user_data.password.encode('utf-8'), user[0][7].encode('utf-8'))
      
      if isCorrectPassword:
         # todo: 
         # - don't let them enter unless email is verified
         
         # generate tokens
         access_token = auth_handler.encode_token(user[0][0], TokenType.access)     # aka. bearer token
         refresh_token = auth_handler.encode_token(user[0][0], TokenType.refresh)   # to create new token after expired
         
         # update database
         cursor.execute("UPDATE accounts SET last_login_at=CURRENT_TIMESTAMP, last_login_ip=%s, login_count=login_count+1 WHERE uid=%s", ("localhost", user[0][0])) # Implement IP address fetching
         cursor.execute("SELECT * FROM token_management WHERE uid=%s ORDER BY created_at DESC;", (user[0][0],))
         latest_token = cursor.fetchall()
         if len(latest_token) == 0:
            cursor.execute("INSERT INTO token_management (uid, access_token, refresh_token) VALUES (%s, %s, %s);", (user[0][0], access_token, refresh_token))
         else:
            cursor.execute("INSERT INTO token_management (uid, access_token, refresh_token, pair_count) VALUES (%s, %s, %s, %s);", (user[0][0], access_token, refresh_token, latest_token[0][5] + 1))
         conn.commit()
         
         return {
            "message": "Login successful",
            "access-token": access_token,
            "refresh-token": refresh_token
         }
      else:
         return {"message": "Incorrect password"}

   finally:
      conn.close()


@app.post('/token', summary="Re-authenticate with a refresh token")
def validate_refresh_token(token: Token, conn=Depends(connection)):
   
   # todo:
   # - remove old refresh token from database
   # - perhaps a better pair count system for tokens
   
   uid = auth_handler.decode_token(token.value, TokenType.refresh)
   new_access_token = auth_handler.encode_token(uid, TokenType.access)
   new_refresh_token = auth_handler.encode_token(uid, TokenType.refresh)
   
   try:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM token_management WHERE refresh_token=%s;", (token.value,))
      token_data = cursor.fetchall()
      conn.commit()
      
      # check if token exists in database
      if len(token_data) == 0:
         raise HTTPException(status_code=401, detail="Invalid refresh token")
      
      # delete token on 3rd use
      if token_data[0][6] == 2:
         cursor.execute("DELETE FROM token_management WHERE refresh_token=%s;", (token.value,))
      
      cursor.execute("SELECT * FROM token_management WHERE uid=%s ORDER BY created_at DESC;", (uid,))
      latest_token = cursor.fetchall()
      cursor.execute("UPDATE token_management SET refresh_token_use_count=refresh_token_use_count+1, refresh_token_last_used_at=CURRENT_TIMESTAMP WHERE refresh_token=%s;", (token.value,))
      cursor.execute("INSERT INTO token_management (uid, access_token, refresh_token, pair_count) VALUES (%s, %s, %s, %s);", (uid, new_access_token, new_refresh_token, latest_token[0][5] + 1))
      conn.commit()
   
      return {
         "message": "token validated",
         "new-access-token": new_access_token,
         "new-refesh-token": new_refresh_token
      }
   finally:
      conn.close()


@app.delete('/logout', summary="Delete all tokens")
def delete_refresh_token(token: Token, conn=Depends(connection)):
   try:
      cursor = conn.cursor()
      cursor.execute("DELETE FROM token_management WHERE refresh_token=%s;", (token.value,))
      return {"message": "Token has been deleted successfully"}
   finally:
      conn.close()


@app.post('/upload', summary="Upload media files")
def upload(uid=Depends(auth_handler.auth_wrapper)):
   # work in progress
   return { 'uid': uid }