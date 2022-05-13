#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Jins Mathew | UFS Botz

import os
import asyncio

import pyrogram

from pyrogram import Client
from plugins.help_text import cancel_extract
from plugins.rename_file import force_name, rename_doc

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config, temp
else:
    from config import Config, temp


@Client.on_callback_query()
async def cb_handler(bot, update):
    if "default" in update.data:
        if update.message.reply_to_message:
            asyncio.create_task(rename_doc(bot, update.message, True))
        else:
            print('No media present')
        
    elif "rename_button" in update.data:
        await update.message.delete()
        await force_name(bot, update.message)
        
    elif "cancel_e" in update.data:
        await update.message.delete()
        await cancel_extract(bot, update.message)

    elif update.data.startswith("gUPcancel"):
        cmf = update.data.split("/")
        chat_id, mes_id, from_usr = cmf[1], cmf[2], cmf[3]
        if int(update.from_user.id) == int(from_usr):
            Config.gDict[int(chat_id)].append(int(mes_id))
        return
