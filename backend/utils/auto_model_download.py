import os
import requests
from utils import logging_config
import logging
from config import config

# Setup logging
logger = logging.getLogger(__name__)

class Model:
    """
    Class to download the model file
    """
    @staticmethod
    def download_model(model_path, model_url):
        """
        Download the model file
        """
        # Check if file exists
        if not os.path.exists(model_path):
            logging.info(msg=f"Downloading model file from {config.MODEL['model_url']} to {config.MODEL['model_path']}...")

            # Download the file
            response = requests.get(model_url, stream=True)
            if response.status_code == 200:
                with open(model_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                logging.info(msg=f"Download complete: {model_path}")
            else:
                logging.info(msg=f"Failed to download file. Status code: {response.status_code}")
        else:
            logging.info(f"{model_path} already exists at {model_path}.")


    # # Define filename and URL
    # filename = "yolo11x-cls.pt"
    # url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-cls.pt"  # Replace with the actual URL
