from fastapi import Depends, HTTPException, Request
from models import NewUser, UserLogin, Profile, Token, TokenType
from initialize import app, auth_handler
from config import settings
from datetime import datetime
import bcrypt
import validate

@app.get("/")
async def root():
   return {
      "message": "Welcome to Authentication API v2.0"
   }


@app.get('/users', summary="Get all users", status_code=200)
async def get_users(uid = Depends(auth_handler.auth_wrapper)):
   try:
      if uid['payload'] is not None:
         q = "SELECT * FROM accounts WHERE uid = $1;"
         r = await app.state.db.fetch(q, uid['payload'])
         
         if len(r) == 0:
            return {
               "status_code": 201,
               "detail" : "Invalid UID in token"
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


@app.get('/users/{username}', summary="Get a user profile", status_code=200)
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


@app.post('/users/{username}', summary="Update a user profile", status_code=200)
async def update_user_profile(profile_data: Profile, uid = Depends(auth_handler.auth_wrapper)):
   if uid['payload'] is None:
      return {
         "status_code" : 401,
         "detail" : uid['message']
      }
   else:
      try:
         q = "SELECT * FROM accounts WHERE uid = $1;"
         r = await app.state.db.fetch(q, uid['payload'])
         
         if len(r) == 0:
            return {
               "status_code": 404,
               "detail" : "User not found"
            }
         
         user = r[0]
         
         wantsToChangeUsername = False
         if profile_data.username != "" and profile_data.username != None and profile_data.username != user['username']:
            wantsToChangeUsername = True
         
         for key, value in profile_data.dict().items():
            if value is None or value == "":
               profile_data.__setattr__(key, user[key])
               
         if settings.allow_username_change == False:
            q = "UPDATE accounts SET name_first=$1, name_last=$2, image=$3, bio=$4, updated_at=CURRENT_TIMESTAMP WHERE uid=$5;"
            await app.state.db.execute(q, profile_data.name_first, profile_data.name_last, profile_data.image, profile_data.bio, uid['payload'])
            
            if wantsToChangeUsername:
               profile_data.__setattr__('username', user['username'])
               return {
                  "status_code": 200,
                  "detail" : {
                     "message" : "Profile updated partially. Username cannot be changed.",
                     "profile" : profile_data
                  }
               }
         else:
            if wantsToChangeUsername:
               q = "SELECT * FROM accounts WHERE username = $1;"
               r = await app.state.db.fetch(q, profile_data.username)
               
               if len(r) > 0:
                  return {
                     "status_code": 409,
                     "detail" : "Username already exists"
                  }
               
            q = "UPDATE accounts SET name_first = $1, name_last = $2, image = $3, username = $4, bio = $5, updated_at=CURRENT_TIMESTAMP WHERE uid = $6;"
            await app.state.db.execute(q, profile_data.name_first, profile_data.name_last, profile_data.image, profile_data.username, profile_data.bio, uid['payload'])
         
         return {
            "status_code": 200,
            "detail" : {
               "message" : "Profile updated successfully",
               "profile" : profile_data
            }
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
   """
   When access token is expired, the client must send a valid refresh token to generate a new access token.
   """
   try:      
      uid = auth_handler.decode_token(token.value, TokenType.refresh)
      
      if uid["message"] is not None:
         return {
            "status_code" : 401,
            "detail" : uid["message"]
         }
      
      new_access_token = auth_handler.encode_token(uid['payload'], TokenType.access)
      
      return {
         "status_code" : 200,
         "detail" : {
            "message": "Token refreshed successfully",
            "access_token": new_access_token
         }
      }
      
   except Exception as e:
      raise HTTPException(
         status_code=500,
         detail=e
      )


@app.post('/validate', summary="Validate access token")
def validate_access_token(token: Token):
   """
   Why would you need this? So that you don't need to calculate when the token has expired
   or if it's invalid from the client side. It will cost you a HTTP request though.
   """
   try:
      uid = auth_handler.decode_token(token.value, TokenType.access)
      
      if uid["message"] is not None:
         return {
            "status_code" : 401,
            "detail" : uid["message"]
         }
      
      return {
         "status_code" : 200,
         "detail" : "Token is valid"
      }
      
   except Exception as e:
      raise HTTPException(
         status_code = 500,
         detail = e
      )


@app.delete('/logout', summary="Delete token")
async def delete_refresh_token():
   """
   Doesn't do anything. Just here for documentation purposes.  
   If you wish to logout, just remove the tokens from your client.
   """
   return {
      "status_code" : 410,
      "detail" : "This route is gone. Here's what you can do instead: (1) delete the tokens from your client, or (2) blacklist the tokens, or (3) make token expiration short and rotate them often."
   }

