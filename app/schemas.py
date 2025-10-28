from pydantic import BaseModel #does data validation and settings management using python type annotations

#splitting models helps if we only want certain fields to be required for creation vs update
class PostBase(BaseModel): 
    title: str #does not check for string, will try to convert if possible
    content: str
    published: bool = True

class PostCreate(PostBase): 
    pass
