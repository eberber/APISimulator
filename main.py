from fastapi import FastAPI
from fastapi.params import Body
#Can use uvicorn main:app to start the server , add --reload to auto reload on code changes
app = FastAPI()

#this decorator is what makes this function useful for API calls, where do we land in the page?
#@FastAPIinstance.httpmethod("path")
#fastapi will go down this list until it finds a first match, order matters! 
@app.get("/")
async def root():
    return {"message": "Hello World 2"}

@app.get("/posts")
def get_posts():
    return {"data": "some posts"}

@app.post("/createposts")
def create_posts(payload : dict = Body(...)):
    print(payload)
    return {"data": f"post created: {payload["message"]}"}