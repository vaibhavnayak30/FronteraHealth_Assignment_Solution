import redis
from config import config as cfg
import redis.asyncio as redis
import asyncio
import sys
from utils import logging_config
import logging

# Setup logging
logger = logging.getLogger(__name__)

class RedisManager:

    @staticmethod
    async def connect(db:int):
        try:
            # Connect to redis server
            logger.info(msg= f"Setting up redis server with db: {db}...")
            redis_storage = await redis.from_url(cfg.REDIS_SERVER['client'] + ":" + "//" + cfg.REDIS_SERVER['host'] + ":" + str(cfg.REDIS_SERVER['port']) + "/" + str(db), decode_responses= True)
            logging.info(msg= f"Successfully created redis server object for db: {db}.")

            # Check for redis successful connection 
            logger.info(msg=f"Checking connection status...")
            await redis_storage.ping()
           
            # Return connection object
            logger.info(msg= f"Connection successful. Returning redis connection object...")
            return redis_storage
        
        except Exception as e:
            logging.error(msg=f"Cannot create redis connection object, exiting with error: {e}")
            return None

    @staticmethod
    async def close_connection(redis_connection_obj):
        try:
            # Close connection to redis server
            logger.info(msg="Closing redis connection and freeing up space...")
            await redis_connection_obj.close()
            logger.info(msg="Successfully closed redis connection.")
            # await redis_queue.close()
            # logger.info(msg="Successfully closed redis connection for queue.")

        except Exception as e:
            logger.info(msg=f"Couldn't close redis connection with error: {e}")


# if __name__ == "__main__":
#     asyncio.run(RedisManager.connect())