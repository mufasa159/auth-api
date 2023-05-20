from fastapi import Depends, HTTPException, Request
from models import NewUser, UserLogin, Profile, Token
from auth import TokenType
from initialize import app, auth_handler
from config import settings
import bcrypt
import validate

@app.get("/")
async def root():
   return {
      "message": "Welcome to Authentication API v2.0"
   }


@app.get('/users/{username}', summary="Get a user", status_code=200)
async def get_users(username: str):
   try:
      q = "SELECT * FROM accounts WHERE username = $1;"
      r = await app.state.db.fetch(q, username)
      
      if len(r) == 0:
         return {
            "status_code": 404,
            "detail" : "User not found"
         }
      
      user = r[0]
      
      user_data = Profile(
         name_first = user['name_first'],
         name_last  = user['name_last'],
         image      = user['image'],
         username   = user['username'],
         bio        = user['bio']
      )
      return user_data
   
   except Exception as e:
      raise HTTPException(status_code=500, detail=e)


@app.get('/users', summary="Get all users", status_code=200)
async def get_users(uid = Depends(auth_handler.auth_wrapper)):
   try:
      
      if uid['payload'] is not None:
         q = "SELECT * FROM accounts WHERE uid = $1;"
         r = await app.state.db.fetch(q, uid['payload'])
         
         if len(r) == 0:
            return {
               "status_code": 401,
               "detail" : "Invalid token"
            }
         
         user = r[0]
         
         if user['role'] == "admin":
            return await app.state.db.fetch("SELECT * FROM accounts;")
         else:
            return {
               "status_code" : 401,
               "detail" : "You are not authorized to access this resource"
            }
      else:
         return {
            "status_code" : 401,
            "detail" : uid['message']
         }
   except Exception as e:
      raise HTTPException(status_code=500, detail=e)


@app.post('/register', summary="Register")
async def register(user_data: NewUser):
   """
   Register a new user. Make sure to provide a unique `username`, a valid `email` address
   and a `password` that is at least 8 characters long.
   """
   
   try:
      u = "SELECT * FROM accounts WHERE username = $1;"
      e = "SELECT * FROM accounts WHERE email = $1;"
      res_u = await app.state.db.fetch(u, user_data.username)
      res_e = await app.state.db.fetch(e, user_data.email)
      
      if len(res_u) > 0:
         return {
            "status_code" : 409,
            "detail" : "Username already exists"
         }
      elif len(res_e) > 0:
         return {
            "status_code" : 409,
            "detail" : "Email already exists"
         }
      else:
         if not validate.email(user_data.email):
            return {
               "status_code" : 400, 
               "detail" : "Invalid email"
            }
      
         if len(user_data.password) < 8:
            return {
               "status_code" : 400, 
               "detail" : "Password must be at least 8 characters long"
            }
      
         encrypted_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt(10))
         q = "INSERT INTO accounts (name_first, name_last, username, email, hash) VALUES ($1, $2, $3, $4, $5);"
         
         await app.state.db.execute(
            q, 
            user_data.name_first, 
            user_data.name_last, 
            user_data.username, 
            user_data.email, 
            encrypted_password.decode('utf8')
         )
         
         if settings.active_mail_service:
            # send email
            pass
         
         return {
            "status_code" : 201, 
            "detail" : "User created successfully"
         }
   
   except Exception as e:
      raise HTTPException(status_code=500, detail=e)


@app.post('/login', summary="Login")
async def login(user_data: UserLogin, request: Request):
   try:
      q = "SELECT * FROM accounts WHERE username = $1;"
      r = await app.state.db.fetch(q, user_data.username)
      
      if len(r) == 0:
         return {
            "status_code" : 404, 
            "detail" : "User does not exist"
         }
         
      user = r[0]

      if settings.active_mail_service and not user['confirmed_email']:
         return {
            "status_code" : 401, 
            "detail" : "Please verify your email address to enter"
         }

      isCorrectPassword = str(user['hash']).encode('utf-8') == bcrypt.hashpw(user_data.password.encode('utf-8'), str(user['hash']).encode('utf-8'))
      
      if isCorrectPassword:
         access_token = auth_handler.encode_token(user['uid'], TokenType.access)     # aka. bearer token
         refresh_token = auth_handler.encode_token(user['uid'], TokenType.refresh)   # to create new token after expired
         
         await app.state.db.execute("UPDATE accounts SET last_login_at=CURRENT_TIMESTAMP, last_login_ip=$1, login_count=login_count+1 WHERE uid=$2", str(request.client.host), user['uid'])
         r = await app.state.db.fetch("SELECT * FROM token_management WHERE uid=$1 ORDER BY created_at DESC;", user['uid'])
         
         if len(r) == 0:
            await app.state.db.execute("INSERT INTO token_management (uid, refresh_token) VALUES ($1, $2);", user['uid'], refresh_token)
         else:
            latest_token = r[0]
            await app.state.db.execute("INSERT INTO token_management (uid, refresh_token, pair_count) VALUES ($1, $2, $3);", user['uid'], refresh_token, latest_token['pair_count']+1)
         
         return {
            "status_code" : 200,
            "detail" : {
               "message": "Login successful",
               "access_token": access_token,
               "refresh_token": refresh_token
            }
         }
      else:
         return {
            "status_code" : 401,
            "detail" : "Incorrect password"
         }

   except Exception as e:
      raise HTTPException(status_code=500, detail=e)


@app.post('/token', summary="Generate access token")
async def validate_refresh_token(token: Token):
   try:      
      uid = auth_handler.decode_token(token.value, TokenType.refresh)
      
      if uid["message"] is not None:
         return {
            "status_code" : 401,
            "detail" : uid["message"]
         }
      
      new_access_token = auth_handler.encode_token(uid['payload'], TokenType.access)
      new_refresh_token = auth_handler.encode_token(uid['payload'], TokenType.refresh)
      
      return {
         "status_code" : 200,
         "detail" : {
            "message": "Token refreshed successfully",
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
         }
      }
      
   except Exception as e:
      raise HTTPException(
         status_code=500,
         detail=e
      )


@app.delete('/logout', summary="Delete token")
async def delete_refresh_token():
   """
   Doesn't do anything. Just here for documentation purposes.  
   If you wish to logout, just remove the token from your client.
   """
   return {
      "status_code" : 410,
      "detail" : "This route is gone. Here's what you can do instead: (1) delete the token from your client, or (2) blacklist the token, or (3) make token expiration short and rotate them often."
   }

