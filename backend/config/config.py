import os 

# Application settings
APP_NAME = "Frontera Health Assignment"
VERSION  = "1.0"

# AI Model Details
MODEL = {
    "model_path": "./model/yolo11x-cls.pt",    # Path to model, model name to be provided as environment variable
    "model_url" : "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-cls.pt",
    "model_name": "YOLO_v11",
    "library"   : "ultralytics"
}

# Model parametera
MODEL_PARAMETERS = {
    "save_result"    : False,
    "conf_threshold" : 0.5,
    "iou"            : 0.7,
    "half"           : False,
    "img_size"       : 320 
}

# Inference Server Details
INFERENCE_SERVER = {
    "host" : "0.0.0.0",
    "port" : 8080
}

# Redis Service 
REDIS_SERVER = {
    "client": "redis",
    "host"  : os.getenv("REDIS_HOST", "localhost"),
    "port"  : int(os.getenv("REDIS_PORT", 6379)),
    "db_store"    : 0,
    "in_queue"    : "image_queue"
}

# List of dog breeds class ids model is trained on 
DOG_BREEDS = [
    151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 259
    ]
