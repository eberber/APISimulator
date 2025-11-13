from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from typing import List #for type hinting lists

 #cannot use app here since we are in a submodule, need to create a router instance
router = APIRouter(
    prefix="/posts", #all routes in this file will have /posts prefix, if empty route then it is just /posts
    tags=['Posts'] #all routes in this file will have 'Posts' tag in the docs at http://127.0.0.1:8000/docs#/
)
############################################ POST API ROUTES ##########################################################

#this decorator is what makes this function useful for API calls, where do we land in the page?
#@FastAPIinstance.httpmethod("path")
#fastapi will go down this list until it finds a first match, order matters! 

@router.get("/", response_model=List[schemas.PostBase]) #response model is a list of PostBase schemas
def get_posts(db: Session = Depends(get_db)):
    """ cur.execute("SELECT * FROM posts;") #pyscopg example 
    posts = cur.fetchall() #to actually run the query """
    posts= db.query(models.Post).all() #sqlalchemy example
    return  posts #json converts arrays and dicts automatically

#orefix /posts from router instance will be added here
@router.get("/{id}", response_model=schemas.PostBase) #this path parameter is dynamic, can be anything, even if you do sometting like /posts/apple it will still 'work'. order matters
def get_post(id: int, response:Response, db: Session = Depends(get_db)): #path parameters are always strings, need to convert to int for data validation!
    # cur.execute("SELECT * FROM posts WHERE id = %s", (id,)) #pscopg: the second argument must always be a sequence , even if it contains a single variable (remember that Python requires a comma , to create a single element tuple)
    # result = cur.fetchone() #get one result
    
    result = db.query(models.Post).filter(models.Post.id == id).first() #sqlalchemy
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found") #cleaner way to handle errors
        #response.status_code = status.HTTP_404_NOT_FOUND #can control status code manually!
        #return {"message": f"post with id: {id} was not found"}
    return result #make sure this matches the response model...

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse) #201 means something was created, default was 200 and wrong
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
    return  new_post

@router.delete("/{id}")
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
  
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cur.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", (updated_post.title, updated_post.content, updated_post.published, id))
    # new_post = cur.fetchone() #if nothing was updated, this will be None
    new_post = db.query(models.Post).filter(models.Post.id == id) #sqlalchemy
    if new_post.first() is None: #first is the actual post object not the query, so we need to call first() to see if it exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # conn.commit() #save the changes
    new_post.update(updated_post.model_dump(), synchronize_session=False) 
    db.commit() #save the changes
    return  new_post.first()
