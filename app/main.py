from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel #does data validation and settings management using python type annotations
from random import randrange
import psycopg #python postgres library to connect to a postgres database
from psycopg.rows import dict_row  # This is the new location for RealDictRow, instead of tuples, you get dictionaries with column names.
import time

#activate virtual environment in terminal: myenv\Scripts\activate
#Can use uvicorn app.main:app --reload to start the server , --reload to auto reload on code changes
#firs app is the folder where main is stored, 2nd app is the name of the instance below
app = FastAPI()

class Post(BaseModel):
    title: str #does not check for string, will try to convert if possible
    content: str
    published: bool = True
    rating: int | None = None

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
def get_posts():
    cur.execute("SELECT * FROM posts;")
    posts = cur.fetchall() #to actually run the query
    print(posts)
    return {"data": posts} #json converts arrays and dicts automatically

@app.get("/posts/{id}") #this path parameter is dynamic, can be anything, even if you do sometting like /posts/apple it will still 'work'. order matters
def get_post(id: int, response:Response): #path parameters are always strings, need to convert to int for data validation!
    cur.execute("SELECT * FROM posts WHERE id = %s", (id,)) #pscopg: the second argument must always be a sequence , even if it contains a single variable (remember that Python requires a comma , to create a single element tuple)
    result = cur.fetchone() #get one result
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found") #cleaner way to handle errors
        #response.status_code = status.HTTP_404_NOT_FOUND #can control status code manually!
        #return {"message": f"post with id: {id} was not found"}
    return {"post_detail": result}

@app.post("/posts", status_code=status.HTTP_201_CREATED) #201 means something was created, default was 200 and wrong
#can also use payload : dict = Body(...) if you don't want to create a class
def create_posts(new_post: Post):
    #post_dict = new_post.model_dump() #convert to dictionary for pydantic
    #using f string leaves you open to sql injection attacks, use %s and a tuple instead
    #psycopg will check for sql injection attacks when using %s
    cur.execute("""INSERT INTO Posts (title, content, published) VALUES (%s,%s,%s) RETURNING * """, (new_post.title, new_post.content, new_post.published))
    new_post = cur.fetchone() #get the new post that was just created
    conn.commit() #save the changes
    return {"data": new_post}

@app.delete("/posts/{id}")
def delete_post(id:int):
    cur.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,)) #RETURNING * will return the deleted row
    deleted_post = cur.fetchone() #if nothing was deleted, this will be None
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    conn.commit() #save the changes
    #when deleteing we don;t send back any content, but can use response object to set status code 
    return Response(status_code=status.HTTP_204_NO_CONTENT) #204 means no content, but successful
  
@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post):
    cur.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (updated_post.title, updated_post.content, updated_post.published, id))
    new_post = cur.fetchone() #if nothing was updated, this will be None
    if new_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    """post_dict = updated_post.model_dump()
    post_dict['id'] = id 
    my_posts[new_post] = post_dict"""
    conn.commit() #save the changes
    return {"data": new_post}
