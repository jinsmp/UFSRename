import pymongo
from sample_config import Config
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(Config.DB_URI)
mydb = myclient['UFSBOTZ']
restart_stagedb = mydb['Restart']


async def start_restart_stage(chat_id: int, message_id: int):
    restart_stagedb.update_one(
        {"something": "something"},
        {
            "$set": {
                "chat_id": chat_id,
                "message_id": message_id,
            }
        },
        upsert=True,
    )


async def clean_restart_stage() -> dict:
    data = restart_stagedb.find_one({"something": "something"})
    # data = restart_stagedb.find_one({"something": "something"})
    if not data:
        return {}
    restart_stagedb.delete_one({"something": "something"})
    return {
        "chat_id": data["chat_id"],
        "message_id": data["message_id"],
    }
