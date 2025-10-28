from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from random import randrange
import psycopg #python postgres library to connect to a postgres database
from psycopg.rows import dict_row  # This is the new location for RealDictRow, instead of tuples, you get dictionaries with column names.
import time
from . import models, schemas
from .database import engine, Base, SessionLocal, get_db
from sqlalchemy.orm import Session

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

#this decorator is what makes this function useful for API calls, where do we land in the page?
#@FastAPIinstance.httpmethod("path")
#fastapi will go down this list until it finds a first match, order matters! 
@app.get("/")
async def root():
    return {"message": "Hello World 2"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    """ cur.execute("SELECT * FROM posts;") #pyscopg example 
    posts = cur.fetchall() #to actually run the query """
    posts= db.query(models.Post).all() #sqlalchemy example
    return {"data": posts} #json converts arrays and dicts automatically

@app.get("/posts/{id}") #this path parameter is dynamic, can be anything, even if you do sometting like /posts/apple it will still 'work'. order matters
def get_post(id: int, response:Response, db: Session = Depends(get_db)): #path parameters are always strings, need to convert to int for data validation!
    # cur.execute("SELECT * FROM posts WHERE id = %s", (id,)) #pscopg: the second argument must always be a sequence , even if it contains a single variable (remember that Python requires a comma , to create a single element tuple)
    # result = cur.fetchone() #get one result
    
    result = db.query(models.Post).filter(models.Post.id == id).first() #sqlalchemy
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found") #cleaner way to handle errors
        #response.status_code = status.HTTP_404_NOT_FOUND #can control status code manually!
        #return {"message": f"post with id: {id} was not found"}
    return {"post_detail": result}

@app.post("/posts", status_code=status.HTTP_201_CREATED) #201 means something was created, default was 200 and wrong
#can also use payload : dict = Body(...) if you don't want to create a class
def create_posts(new_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # psycopg example
    # #post_dict = new_post.model_dump() #convert to dictionary for pydantic
    # #using f string leaves you open to sql injection attacks, use %s and a tuple instead
    # #psycopg will check for sql injection attacks when using %s
    # cur.execute("""INSERT INTO Posts (title, content, published) VALUES (%s,%s,%s) RETURNING * """, (new_post.title, new_post.content, new_post.published))
    # new_post = cur.fetchone() #get the new post that was just created
    # conn.commit() #save the changes 

    #new_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published) #sqlalchemy example
    #we can also use dict unpacking if we convert to dictionary first, make sure pydantic model field names match db column names
    new_post = models.Post(**new_post.model_dump())
    db.add(new_post)
    db.commit() #save the changes
    db.refresh(new_post) #get the new post that was just created
    return {"data": new_post}

@app.delete("/posts/{id}")
def delete_post(id:int, db: Session = Depends(get_db)):
    # cur.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,)) #RETURNING * will return the deleted row
    # deleted_post = cur.fetchone() #if nothing was deleted, this will be None
    deleted_post = db.query(models.Post).filter(models.Post.id == id)  #sqlalchemy, this is a query object
    if deleted_post.first() is None: #first is the actual post object not the query, so we need to call first() to see if it exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    #conn.commit() #save the changes
    deleted_post.delete(synchronize_session=False) #synchronize_session=False is for performance, we don't need to sync the session here
    db.commit()
    #when deleteing we don;t send back any content, but can use response object to set status code 
    return Response(status_code=status.HTTP_204_NO_CONTENT) #204 means no content, but successful
  
@app.put("/posts/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cur.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (updated_post.title, updated_post.content, updated_post.published, id))
    # new_post = cur.fetchone() #if nothing was updated, this will be None
    new_post = db.query(models.Post).filter(models.Post.id == id) #sqlalchemy
    if new_post.first() is None: #first is the actual post object not the query, so we need to call first() to see if it exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # conn.commit() #save the changes
    new_post.update(updated_post.model_dump(), synchronize_session=False) 
    db.commit() #save the changes
    return {"data": new_post.first()}