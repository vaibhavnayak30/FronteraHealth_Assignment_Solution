from typing import Union
from config import config
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import json
import base64
import zlib
from contextlib import asynccontextmanager
from utils.redis_manager import RedisManager
import logging
from utils import logging_config
import asyncio
import numpy as np

# logging.basicConfig(level= logging.INFO)
logger = logging.getLogger(__name__)
    

# Context manager to handle startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # All setups during startup
    logger.info(f"Starting up app server for {config.APP_NAME}... ")

    # Initialize redis connection object
    redis_store= await RedisManager.connect(db=config.REDIS_SERVER['db_store'])

    try:
        if not redis_store:
            raise Exception("Cannot start backend server without a valid redis connection. Please check the connection setting.")
        
        # Store the redis connection object in the app state to make it accessible globally
        app.state.redis_store= redis_store

        # Yield control back to FastAPI (it will start handling requests now)
        yield

        # All cleanup during shutdown
        # Close the redis connection
        await RedisManager.close_connection(redis_connection_obj= redis_store)
    
    except Exception as e:
        logger.error(f"Server startup failed with error: {e}.")
        raise Exception(f"Server startup failed with error: {e}. Exiting...")

# FastAPI app initialization with lifespan
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/image_prediction")
async def get_predictions(file: UploadFile = File(...)) -> JSONResponse:
    """
    Get the image from the request, compress and decode it and send it for prediction

    :param file: The image file to send for prediction
    :return: A JSON response with the prediction status
    """
    # Validate the content 
    if file.content_type not in config.PERMISSIBLE_CONTENT_TYPES:
        return JSONResponse(content={"error": "Invalid file type"}, status_code=400)

    try:
        # Read the uploaded image as bytes
        image_bytes = await file.read()

        # Compress the image using zlib
        # compressed_image = zlib.compress(image_bytes)

        # Encode the compressed image to Base64 string
        base64_encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        # Generate unique id for the image
        image_id = await app.state.redis_store.incr("image_id")

        # Create a dictionary with the image and ID
        message = {
            'image_id': image_id,
            'image_data': base64_encoded_image
        }

        # Serialize the dictionary to a JSON string
        serialized_data= json.dumps(message)
    
        # send image for prediction
        logger.info(msg= f"Sending image with id: {image_id} for prediction...")
        await app.state.redis_store.rpush(config.REDIS_SERVER['data_queue'], serialized_data)

        # Return the response
        return JSONResponse(content={"image_prediction_id": 1, "status": "PENDING", "has_dog": None}, status_code= 200)

    except Exception as e:
        return JSONResponse(content={"error": f"Error while trying to read the image as : {str(e)}"}, status_code=500)
    

@app.get("/image_prediction/{image_id}")
async def get_prediction(image_id: int):
    """
    Get the prediction status of the image with the given ID

    :param image_id: The ID of the image to get the prediction status for
    :return: A JSON response with the prediction status
    """
    # Get the prediction status from the Redis store
    try:
        # Get the prediction status from the Redis store
        hash_data = await app.state.redis_store.hgetall(image_id)
        logger.info(msg= f"Getting prediction status for image with id: {image_id}")

        # Check if the prediction status is available
        if hash_data:
            # Return the prediction status
            return JSONResponse(content=hash_data, status_code=200)
        else:
            # Return a 404 response if the prediction status is not available
            return JSONResponse(content={"error": "Prediction status not found"}, status_code=404)
    
    except Exception as e:
        return JSONResponse(content={"error": f"Error while trying to get the prediction status: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host= config.API_SERVER['host'], port= config.API_SERVER['port'])