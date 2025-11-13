from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from random import randrange
import psycopg #python postgres library to connect to a postgres database
from psycopg.rows import dict_row  # This is the new location for RealDictRow, instead of tuples, you get dictionaries with column names.
import time
from . import models, schemas, utils
from .database import engine, Base, SessionLocal, get_db
from sqlalchemy.orm import Session
from typing import List #for type hinting lists
from .routers import post, user, auth

#sqlachemy setup
models.Base.metadata.create_all(bind=engine) #create the database tables

#activate virtual environment in terminal: myenv\Scripts\activate
#Can use uvicorn app.main:app --reload to start the server , --reload to auto reload on code changes
#firs app is the folder where main is stored, 2nd app is the name of the instance below
app = FastAPI()



########################################### DATABASE #########################################################
while True: #keep trying to connect to database until it works
    try:
        conn = psycopg.connect(host='localhost', dbname='APISimulator', user='postgres', password='Freely-Erased7-Headsman', row_factory=dict_row)#
            # Open a cursor to perform database operations
        cur = conn.cursor()
        print("Database connection was successful!")
        # Query the database and obtain data as Python objects.
        cur.execute("SELECT * FROM information_schema.tables;")
        print(cur.fetchone())
        # will print dict of first row in products table
        break
    except Exception as error:
        print("Connecting to database failed or database operation failed")
        print("Error: ", error)
        time.sleep(2) #wait 2 seconds before trying to reconnect

#Testing only - you can use any data structure that can be serialized to JSON
my_posts = [{"title": "great food spots", "content": "Smittys and Yen Du", "id":"1"}, {"title": "Economy growing weaker", "content": "All under president trumps tariffs", "id":"2"}] #temporary storage, will reset on server restart

############################################ HELPER FUNCTIONS ##########################################################

def find_post(id: int): #grab one post by id
    for post in my_posts:
        if post['id'] == str(id):
            return post
    return None

def find_index_post(id: int): #grab index of post by id
    for i, p in enumerate(my_posts):
        if p['id'] == str(id):
            return i
    return None
############################################ API ROUTES ##########################################################
app.include_router(post.router) #include the post router
app.include_router(user.router) #include the user router
app.include_router(auth.router) #include the auth router

@app.get("/")
async def root():
    return {"message": "Hello World 2"}