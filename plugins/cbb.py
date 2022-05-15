#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Jins Mathew | UFS Botz

import os
import asyncio

import pyrogram

from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from script import script
from database.ufs_db import rename_db
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

    elif update.data.startswith('upload'):
        doc, bot_up = await rename_db.get_user_by_id(update.from_user.id)

        if doc:
            await rename_db.update_by_id(update.from_user.id, 'doc', False)
            upload_type = "Upload As Video 🎞"
        else:
            await rename_db.update_by_id(update.from_user.id, 'doc', True)
            upload_type = "Upload As File 📁"

        if bot_up:
            update_type = "Bot Updates: ON 🤖"
        else:
            update_type = "Bot Updates: OFF 🤖"

        buttons = [
            [
                InlineKeyboardButton(upload_type, callback_data="upload"),
                InlineKeyboardButton(update_type, callback_data="update")
            ],
            [
                InlineKeyboardButton("Show Thumbnail 🌌", callback_data="thumbnail"),
                InlineKeyboardButton('Home ⚡', callback_data="start")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.edit_text(
            text="<b>Change My Settings As Your Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

    elif update.data.startswith("update"):
        doc, bot_up = await rename_db.get_user_by_id(update.from_user.id)

        if doc:
            upload_type = "Upload As File 📁"
        else:
            upload_type = "Upload As Video 🎞"

        if bot_up:
            await rename_db.update_by_id(update.from_user.id, 'update', False)
            update_type = "Bot Updates: OFF 🤖"
        else:
            await rename_db.update_by_id(update.from_user.id, 'update', True)
            update_type = "Bot Updates: ON 🤖"

        buttons = [
            [
                InlineKeyboardButton(upload_type, callback_data="upload"),
                InlineKeyboardButton(update_type, callback_data="update")
            ],
            [
                InlineKeyboardButton("Show Thumbnail 🌌", callback_data="thumbnail"),
                InlineKeyboardButton('Home ⚡', callback_data="start")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.edit_text(
            text="<b>Change My Settings As Your Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    elif update.data.startswith("thumbnail"):
        BANNED_USERS = await rename_db.get_banned()

        if update.from_user.id in BANNED_USERS:
            await bot.delete_messages(
                chat_id=update.chat.id,
                message_ids=update.id,
                revoke=True
            )
            return

        if update.message is not None:
            d_thumb = await rename_db.get_thumb(update.from_user.id)

            if d_thumb is not None:
                await update.message.send_photo(
                    chat_id=update.message.chat.id,
                    photo=d_thumb,
                    reply_to_message_id=update.message.id
                )
            else:
                await update.message.send_message(
                    chat_id=update.message.chat.id,
                    text="You Are Not To Set Your Default Thumbnail...",
                    reply_to_message_id=update.message.id
                )

    elif update.data.startswith('start'):
        if not await rename_db.is_user_exist(update.from_user.id):
            await rename_db.add_user(update.from_user.id, update.from_user.first_name)
            await update.send_message(Config.LOG_CHANNEL,
                                      script.LOG_TEXT_P.format(update.from_user.id, update.from_user.mention))

        buttons = [[
            InlineKeyboardButton('😇 DEVELOPER', url='https://t.me/UFS_Botz')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.edit_text(
            text=script.START_TEXT.format(update.from_user.first_name),
            reply_to_message_id=update.id,
            reply_markup=reply_markup
        )
