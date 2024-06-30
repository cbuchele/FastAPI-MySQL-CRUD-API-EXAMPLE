import firebase_admin
from firebase_admin import credentials
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import FastAPI, UploadFile, HTTPException, Depends, status
from typing import List, Annotated
from pydanticmodels import UserBase
import models
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
import logging


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# Initialize Firebase Admin SDK with the service account key JSON file
cred = credentials.Certificate("./yourfirebasejsokey")
firebase_admin.initialize_app(cred)


# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",  # Add the exact origin where your frontend is hosted
    
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# AWS S3 Setup
s3_client = boto3.client('s3', aws_access_key_id='use.envhere', aws_secret_access_key='use.envhere')
bucket_name = 'youramazonbucketname'






#USER PHOTO##########################################

@app.post("/upload_user_foto/")
async def upload_user_photo(user_id: str ,file: UploadFile, db: db_dependency):
    try:
        contents = await file.read()
        s3_client.put_object(Bucket=bucket_name, Key=file.filename, Body=contents)
        key = f"{file.filename}"
        
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
          # Get current user data
        
        if db_user:
            # Update foto field with the S3 key
            setattr(db_user, 'foto', key)  # Corrected line
            db.commit()  # Commit changes to the database
        else:
            # If db_user is None, create a new user with the provided user_id and foto
            new_user = models.User(id=user_id, foto=key)
            db.add(new_user)
            db.commit()
        
        return {"filename": key }  # Return the S3 key
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="S3 Credential Error")
    finally:
        await file.close()

#GET UPLOAD BY KEY
@app.get("/user-pic/{user_id}", response_model=str)
async def get_user_picture(user_id: str, db: db_dependency):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        profile_pic_filename = user.foto
        if not profile_pic_filename:
            raise HTTPException(status_code=404, detail="Profile picture not found")

        # Generate presigned URL using the filename from the database
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': profile_pic_filename},
            ExpiresIn=None
        )
        return response

    except ClientError as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################################################################
#START USERS
##################################################################
    #CREATE 
@app.post("/create_user/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency, _id: str):
    try:
        # Assign _id to the id attribute of the user
        user_data = user.model_dump()
        user_data["id"] = _id
        user_data["deleted"] = None

        
        # Create a new user instance with the updated data
        db_user = models.User(**user_data)
        
        # Add the new user to the session
        db.add(db_user)
        
        # Commit the transaction
        db.commit()
        
        # Return the created user
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#READ
@app.get("/users/", response_model=List[UserBase])
async def get_users(db: db_dependency):
    users = db.query(models.User).all()
    # Convert id, role, telefone, and any other integer fields to strings
    for user in users:
        if user.id:
            user.id = str(user.id)
        if user.role:
            user.role = str(user.role)
        if user.telefone:
            user.telefone = str(user.telefone)
    return users

#GET SINGLE USER
@app.get("/users/{user_id}", response_model=UserBase)
async def get_user_by_id(user_id: str, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        if user.id:
            user.id = str(user.id)
        if user.role:
            user.role = str(user.role)
        if user.telefone:
            user.telefone = str(user.telefone)
        return user
    raise HTTPException(status_code=404, detail="User not found")

#UPDATE
@app.post("/update_user/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: str, user: UserBase, db: db_dependency):
    # Get the user to update
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user data (excluding id)
    user_data = user.model_dump(exclude_unset=True)

    try:
        for field, value in user_data.items():
            if field != "id" and field != "deleted":  # Exclude id and deleted
                setattr(db_user, field, value)

        # Commit changes
        db.commit()
        return user

    except IntegrityError as e:
        # Handle potential duplicate name error
        if "users.nome" in str(e):
            raise HTTPException(
                status_code=400, detail="User with this name already exists"
            )
        # Raise generic error for other integrity errors
        raise HTTPException(status_code=400, detail=str(e))
    
#DELETE
@app.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: db_dependency):
    # Get the user to delete
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Soft delete by updating deleted field with timestamp
    db_user.deleted = datetime.now()
    db.commit()

    return None
##########################################################
