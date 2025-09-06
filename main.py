from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel #does data validation and settings management using python type annotations
from random import randrange

#activate virtual environment in terminal: myenv\Scripts\activate
#Can use uvicorn main:app to start the server , add --reload to auto reload on code changes
app = FastAPI()

class Post(BaseModel):
    title: str #does not check for string, will try to convert if possible
    content: str
    published: bool = True
    rating: int | None = None

# you can use any data structure that can be serialized to JSON
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
    return {"data": my_posts} #json converts arrays and dicts automatically

@app.get("/posts/{id}") #this path parameter is dynamic, can be anything, even if you do sometting like /posts/apple it will still 'work'. order matters
def get_post(id: int, response:Response): #path parameters are always strings, need to convert to int
    result = find_post(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found") #cleaner way to handle errors
        #response.status_code = status.HTTP_404_NOT_FOUND #can control status code manually!
        #return {"message": f"post with id: {id} was not found"}
    return {"post_detail": result}

@app.post("/posts", status_code=status.HTTP_201_CREATED) #201 means something was created, default was 200 and wrong
#can also use payload : dict = Body(...) if you don't want to create a class
def create_posts(new_post: Post):
    post_dict = new_post.model_dump() #convert to dictionary
    post_dict['id'] = str(randrange(0,1000000)) #assign random id to new posts until we have a database setup 
    my_posts.append(post_dict)
    print(post_dict)
    return {"data": post_dict}

@app.delete("/posts/{id}")
def delete_post(id:int):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    my_posts.pop(index) #when deleteing we don;t send back any content, but can use response object to set status code 
    return Response(status_code=status.HTTP_204_NO_CONTENT) #204 means no content, but successful
  
@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post_dict = updated_post.model_dump()
    post_dict['id'] = id 
    my_posts[index] = post_dict
    return {"data": post_dict}
