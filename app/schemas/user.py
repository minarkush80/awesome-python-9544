# verify_project/app/schemas/user.py
from pydantic import BaseModel, Field
from datetime import datetime

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    phone_number: str = Field(...)

class UserBase(BaseModel):
    # Aliases match the keys stored in MongoDB by your create_user method
    name: str = Field(..., alias="Name")
    lastname: str = Field(..., alias="LastName")
    phone_number: str = Field(..., alias="PhoneNumber")

class UserResponse(UserBase):
    id: str = Field(..., alias="_id") # Maps MongoDB's _id to id
    created_at: datetime = Field(..., alias="createdAt") # Maps MongoDB's createdAt

    class Config:
        populate_by_name = True # Enables the use of aliases for population
        from_attributes = True # For Pydantic V2 (orm_mode for V1)
        json_encoders = {
            datetime: lambda v: v.isoformat() # Ensure datetime is JSON serializable
        }

class UserExistsResponse(BaseModel):
    message: str = "User already exists."
    phone_number: str

# New response model for successful user creation
class UserCreatedResponse(BaseModel):
    message: str = "User registered successfully."
    user_id: str
