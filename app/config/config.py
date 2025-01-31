import os

# Application settings
APP_NAME = "Frontera Health Assignment"
VERSION  = "1.0"
DESCRIPTION = "Frontera Health Assignment API Server"

# API Server Details
API_SERVER = {
    "host" : "0.0.0.0",
    "port" : 8000
}

# Redis Service 
REDIS_SERVER = {
    "client": "redis",
    "host"  : os.getenv("REDIS_HOST", "localhost"),
    "port"  : int(os.getenv("REDIS_PORT", 6379)),
    "db_store"    : 0,
    "data_queue"  : "image_queue"
}

# Allowed Content Types
PERMISSIBLE_CONTENT_TYPES = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff"]