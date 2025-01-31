from ultralytics import YOLO
from typing import Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import logging
import json
from contextlib import asynccontextmanager
from config import config
import os
from utils.redis_manager import RedisManager
from utils import logging_config
import asyncio
import base64
import numpy as np
import zlib
import cv2
from utils.auto_model_download import Model

# Setup logging
# logging.basicConfig(level= logging.INFO)
logger = logging.getLogger(__name__)

"""
Class to load the ai model into runtime environment and save the model object

Parameters:
    model_path: Model file location wrt to current directory
"""
class AiModel:
    model = None

    def __init__(self, model_path: str):
        """
        Initializes the YOLOv11 model from Ultralytics
        
        Parameters:
            model_path (str): The YOLOv11 classification model variant to load
        """
        logger.info(f"Creating environment to load {config.MODEL['model_name']} using {config.MODEL['library']} backend...")

        # Setup model path, load model and load model object
        self.model_path= model_path
        self._load_model()

    """
    Loads the model and save it as class attribute
    """
    def _load_model(self):
        try:
            # Check if path is a valid path 
            is_valid_path = self._is_valid_file_path(path= self.model_path)

            # Raise exception for incorrect file path
            if not is_valid_path:
                raise FileNotFoundError(f"Path {self.model_path} is not a valid path.")

            # Load the model
            AiModel.model= YOLO(self.model_path)

        
        except FileNotFoundError as e:
            # Handle file not found while loading the AI Model 
            error_response= {"error": "Incorrect model path", "detail": str(e)}
            # logger.error(f"Incorrect model file path: {json.dumps(str(e))}")
            raise(f"Incorrect model file path: {json.dumps(str(e))}")

            # Return error reponse
            # return JSONResponse(status_code= 404, content= error_response)
        

        except Exception as e:
            # Handle any exception while loading the AI Model 
            error_response= {"error": "Error loading the model", "detail": str(e)}
            logger.error(f"Unexpected error while loading model: {json.dumps(str(e))}")

            # Return error response as JSON 
            return JSONResponse(status_code=500, content= error_response)
    
    """
    Get the status of the model
    """
    @staticmethod
    def get_model():
        return AiModel.model


    """
    Check if a path is a valid file path
    Input: Path (str)
    Out: Bool
    """
    def _is_valid_file_path(self, path):
            
            # Check if directory exists
            if_exists = os.path.isfile(path)
            return if_exists



"""
Consume data from redis queue and publish back the results to another queue

Parameters:
    img:
"""
class ProcessImage:
    def __init__(self, redis_storage, ai_model_object, queue_name):
        self.redis_store= redis_storage
        self.ai_model   = ai_model_object
        self.queue_name = queue_name

    async def deserialize_image(self, image_data: str) -> Union[bytes, None]:
        # Deserialize the JSON string to a dictionary
        data = json.loads(image_data)

        # Decode the base64 image data
        image_decoded = base64.b64decode(data['image_data'])

        # Decompress the image using zlib
        # image_bytes = zlib.decompress(image_decoded)
        
        # Convert the image bytes to a NumPy array
        image_array = np.frombuffer(image_decoded, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Get the image ID
        image_id = data['image_id']
        print("Image type: ", type(image))

        return image, image_id
    

    async def fetch_and_process_images(self):

        while True:
                """
                Fetches images from the Redis queue and processes them using the AI model
                """
                try:
                    # Check if the task is cancelled
                    if asyncio.current_task().cancelled():
                        logger.info("Background task was cancelled. Exiting...")
                        return
                    
                    # Blocking pop from the input queue (left pop)
                    logger.info(msg="Waiting for image...")
                    _, image_data= await self.redis_store.blpop(keys= [self.queue_name], timeout=0)

                    # Decode image data
                    image, image_id = await self.deserialize_image(image_data)
                    logger.info(f"Received image with id: {image_id}")
                    
                    # Processing images using AI model
                    predictions = await asyncio.to_thread(self.ai_model.predict, image,
                                                          save=config.MODEL_PARAMETERS['save_result'], 
                                                          imgsz=config.MODEL_PARAMETERS['img_size'], 
                                                          conf=config.MODEL_PARAMETERS['conf_threshold'])
                    
                    # Get the results, type List
                    pred_class_ids  = predictions[0].probs.top5
                    pred_class_conf = predictions[0].probs.top5conf.tolist()

                    # Check if there is atlest 1 prediction output
                    # if len(pred_class_ids) >= 1:

                    # Class id with max conf
                    class_id = pred_class_ids[0]

                    # Get conf score for the class
                    class_conf_score= [pred_class_conf[0]] if class_id in config.DOG_BREEDS else []

                    # Check if the class is a dog
                    has_dog = "true" if class_conf_score else "null"

                    # Save to redis storage
                    logger.info(f"Saving prediction results for image with id: {image_id}")
                    await self.redis_store.hset(image_id, mapping={"image_prediction_id": image_id, 
                                                                   "status": "Done", 
                                                                   "has_dog": has_dog})
        
                except asyncio.CancelledError:
                    logger.info("Backgroud running task failed. Fetch and process images was cancelled.")
                    raise asyncio.CancelledError

                except Exception as e:
                    logger.error(f"Error while processing image: {str(e)}")
                    continue

# This will store any background tasks we need to track
background_tasks = []

# Context manager to handle startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # All setups during startup
    logger.info(f"Starting up Ai Model server for {config.APP_NAME}... ")

    # Donwload the model
    logging.info(msg=f"Checking if model file is present or else it will be downloaded automatically...")
    Model.download_model(model_path= config.MODEL["model_path"], model_url= config.MODEL["model_url"])

    # Initialize redis connection object and store it in app.state to make it accessible globally
    redis_store= await RedisManager.connect(db=config.REDIS_SERVER['db_store'])

    # Initialize model object and process image object if connection to redis is successful
    try:
        if not redis_store:
            raise Exception("Cannot start app server without a valid redis connection.")

        # Initialize Ai Model and store it in app.state to make it accessible globally
        ai_model= AiModel(model_path= config.MODEL['model_path'])

        # Initialize ProcessImage class object
        process_image= ProcessImage(redis_storage= redis_store, ai_model_object= ai_model.get_model(), queue_name= config.REDIS_SERVER['in_queue'])

        # Run process image infinite loop in background
        task= asyncio.create_task(process_image.fetch_and_process_images())

        # Add the task to our list of background tasks
        background_tasks.append(task)

        # Yield control back to FastAPI (it will start handling requests now)
        yield

        # All cleanup during shutdown
        # Cancel background tasks gracefully
        for task in background_tasks:
            task.cancel()
    
        # Await the cancellation to ensure proper cleanup (double check)
        for task in background_tasks:
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Background task {task} was cancelled.")
    

        # Close the redis connection
        await RedisManager.close_connection(redis_storage= redis_store)
        logger.info("Ai Model server is shutting down...")

    except Exception as e:
        logger.error(f"Server startup failed with error: {e}.")
        raise Exception(f"Server startup failed with error: {e}. Exiting...")

# FastAPI app initialization with lifespan
app = FastAPI(lifespan=lifespan)

# Example route that uses the initialized class object
@app.get("/status")
async def get_status():
    # Access the class instance from app.state
    service = app.state.ai_model
    return {"status": service.get_status()}

if __name__ == "__main__":
    uvicorn.run(app, host= config.INFERENCE_SERVER['host'], port= config.INFERENCE_SERVER['port'])