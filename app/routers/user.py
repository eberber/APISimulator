from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from typing import List #for type hinting lists

#cannot use app here since we are in a submodule, need to create a router instance
router = APIRouter(
    prefix="/users", #all routes in this file will have /users prefix
    tags=['Users']
) 


########################################### USER API ROUTE #########################################################
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    #hash the password - user.password
    hashed_pwd = utils.hash_password(new_user.password)
    new_user.password = hashed_pwd
    
    new_user = models.User(**new_user.model_dump()) #dump pydantic model to dict and unpack into sqlalchemy model
    db.add(new_user)
    db.commit() #save the changes
    db.refresh(new_user) 

    return new_user

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")
    return user 