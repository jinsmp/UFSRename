#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Jins Mathew

# the logging things
import bot
import logging

from pyrogram import enums, Client
from pyrogram.raw.all import layer

from database.restart_db import clean_restart_stage

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config, temp
else:
    from config import Config, temp

import pyrogram

logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name='UFS_Rename',
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.TG_BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        await super().start()
        self.set_parse_mode(enums.ParseMode.DEFAULT)
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        dispatcher = self.dispatcher
        logging.info(
            f"{me.first_name} with for Pyrogram v{pyrogram.__version__} (Layer {layer}) started on {me.username}.")
        logging.info(f"{me.first_name} Has Started Running...🏃💨💨")

        restart_data = await clean_restart_stage()

        try:
            # print("[INFO]: SENDING ONLINE STATUS")
            if restart_data:
                logging.info(f"[INFO]: RESTARTING PROCESS")
                await bot.Bot.edit_message_text(self,
                                                restart_data["chat_id"],
                                                restart_data["message_id"],
                                                "**Restarted Successfully**",
                                                )
                await bot.Bot.send_message(self, Config.LOG_CHANNEL, "**Bot Updated Successfully**!")

            else:
                await bot.Bot.send_message(self, Config.LOG_CHANNEL, "**Bot Restarted Successfully**!")
        except Exception as e:
            logging.info(f"[ERROR]: {str(e)}")
            pass

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

