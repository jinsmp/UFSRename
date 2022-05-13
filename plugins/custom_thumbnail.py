#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Jins Mathew

import os
import pyrogram
import logging

from script import script
from database.ufs_db import rename_db
from pyrogram import Client, filters

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config, temp
else:
    from config import Config, temp

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(filters.photo)
async def save_photo(bot, update):
    BANNED_USERS = await rename_db.get_banned()

    if update.from_user.id in BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.id,
            revoke=True
        )
        return

    if update.media_group_id is not None:
        # album is sent
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/" + str(update.media_group_id) + "/"
        # create download directory, if not exist
        if not os.path.isdir(download_location):
            os.makedirs(download_location)
        status = await rename_db.update_thumb(update.from_user.id, update.from_user.first_name, update.photo.file_id)
        await bot.download_media(
            message=update,
            file_name=download_location
        )
    else:
        # received single photo
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
        status = await rename_db.update_thumb(update.from_user.id, update.from_user.first_name, update.photo.file_id)
        await bot.download_media(
            message=update,
            file_name=download_location
        )
        if status:
            await bot.send_message(
                chat_id=update.chat.id,
                text=script.SAVED_THUMB,
                reply_to_message_id=update.id
            )
        else:
            await bot.send_message(
                chat_id=update.chat.id,
                text=script.FAILED_THUMB,
                reply_to_message_id=update.id
            )


@Client.on_message(filters.command(["clearthumbnail"]))
async def delete_thumbnail(bot, update):
    BANNED_USERS = await rename_db.get_banned()

    if update.from_user.id in BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.id,
            revoke=True
        )
        return

    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    
    try:
        status = await rename_db.update_thumb(update.from_user.id, update.from_user.first_name, '')
    except:
        pass
    try:
        os.remove(thumb_image_path)
    except:
        pass

    await bot.send_message(
        chat_id=update.chat.id,
        text=script.DEL_THUMB,
        reply_to_message_id=update.id
    )


@Client.on_message(filters.command(["showthumbnail"]))
async def show_thumb(bot, update):
    BANNED_USERS = await rename_db.get_banned()

    if update.from_user.id in BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.id,
            revoke=True
        )
        return

    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    if not os.path.exists(thumb_image_path):
        mes = await rename_db.get_thumb(update.from_user.id)
        if mes is not None:
            # m = await bot.get_messages(update.chat.id, mes.msg_id)
            await bot.download_media(message=mes, file_name=thumb_image_path)
            # await m.download(file_name=thumb_image_path)
            thumb_image_path = thumb_image_path
        else:
            thumb_image_path = None    
    
    if thumb_image_path is not None:
        try:
            await bot.send_photo(
                chat_id=update.chat.id,
                photo=thumb_image_path,
                reply_to_message_id=update.id
            )
        except:
            pass
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=script.NO_THUMB,
            reply_to_message_id=update.id
        )
