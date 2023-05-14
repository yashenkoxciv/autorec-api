import os
from typing import List
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from autorecapi.models import ImageModel, SubcategoryModel
from autorecapi.recognition.recognition_rpc_client import RecognitionRpcClient
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.autorec

recognition_rpc = RecognitionRpcClient(os.environ["MQ_HOST"])


@app.post("/image", response_description="Add new image", response_model=ImageModel)
async def create_image(image: ImageModel = Body(...)):
    image_dict = jsonable_encoder(image)
    new_student = await db["images"].insert_one(image_dict)
    created_student = await db["images"].find_one({"_id": new_student.inserted_id})

    print(image)
    print(image_dict)
    print(new_student)
    print(created_student)

    # recognize image
    # TODO: send created_student.id as long as created_student.url
    recognition_response = recognition_rpc.call(image_id=str(created_student['_id']), image_url=image.url)

    created_student['category'] = recognition_response['category_id']
    created_student['subcategory'] = recognition_response['subcategory_id']

    student = await db["images"].update_one(
        {'_id': created_student['_id']},
        {'$set': {'category': created_student['category'], 'subcategory': created_student['subcategory']}}
    )
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)


@app.get("/images", response_description="List all images", response_model=List[ImageModel])
async def list_images():
    students = await db["images"].find().to_list(10)
    return students


@app.get("/images/{id}", response_description="Get a single image", response_model=ImageModel)
async def show_image(id: str):
    if (student := await db["images"].find_one({"_id": id})) is not None:
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


# @app.put("/{id}", response_description="Update a student", response_model=StudentModel)
# async def update_student(id: str, student: UpdateStudentModel = Body(...)):
#     student = {k: v for k, v in student.dict().items() if v is not None}

#     if len(student) >= 1:
#         update_result = await db["students"].update_one({"_id": id}, {"$set": student})

#         if update_result.modified_count == 1:
#             if (
#                 updated_student := await db["students"].find_one({"_id": id})
#             ) is not None:
#                 return updated_student

#     if (existing_student := await db["students"].find_one({"_id": id})) is not None:
#         return existing_student

#     raise HTTPException(status_code=404, detail=f"Student {id} not found")


@app.delete("/image/{id}", response_description="Delete an image")
async def delete_image(id: str):
    delete_result = await db["images"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Image {id} not found")


# Subcategory CRUD

@app.post("/subcategory", response_description="Add new subcategory", response_model=SubcategoryModel)
async def create_subcategory(subcategory: SubcategoryModel = Body(...)):
    subcategory = jsonable_encoder(subcategory)
    new_subcategory = await db["subcategory"].insert_one(subcategory)
    created_subcategory = await db["subcategory"].find_one({"_id": new_subcategory.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_subcategory)


@app.get("/subcategory", response_description="List all subcategories", response_model=List[SubcategoryModel])
async def list_subcategories():
    students = await db["subcategory"].find().to_list(10)
    return students
