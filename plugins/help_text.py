#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Jins Mathew | @UFS_Botz | UFSBotz | @UFSBotz_Support

import os
import sys
import random
import logging
import pyrogram
import subprocess

from script import script
from pyrogram import Client, filters
from database.ufs_db import rename_db
from database.restart_db import start_restart_stage
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(filters.command(["start"]))
async def send_start(bot, update):
    if not await rename_db.is_user_exist(update.from_user.id):
        await rename_db.add_user(update.from_user.id, update.from_user.first_name)
        await bot.send_message(Config.LOG_CHANNEL,
                               script.LOG_TEXT_P.format(update.from_user.id, update.from_user.mention))

    buttons = [[
        InlineKeyboardButton('😇 DEVELOPER', url='https://t.me/UFS_Botz')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.reply_photo(
        photo=random.choice(Config.PICS),
        caption=script.START_TEXT.format(update.from_user.first_name),
        reply_to_message_id=update.id,
        reply_markup=reply_markup
    )


@Client.on_message(filters.command(["help"]))
async def help_user(bot, update):
    if not await rename_db.is_user_exist(update.from_user.id):
        await rename_db.add_user(update.from_user.id, update.from_user.first_name)
        await bot.send_message(Config.LOG_CHANNEL,
                               script.LOG_TEXT_P.format(update.from_user.id, update.from_user.mention))

    buttons = [[
        InlineKeyboardButton('😇 DEVELOPER', url='https://t.me/UFS_Botz')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.reply_photo(
        photo=random.choice(Config.PICS),
        caption=script.HELP_USER,
        reply_to_message_id=update.id,
        reply_markup=reply_markup
    )


@Client.on_message(filters.command(["upgrade", "donate"]))
async def upgrade(bot, update):
    if not await rename_db.is_user_exist(update.from_user.id):
        await rename_db.add_user(update.from_user.id, update.from_user.first_name)
        await bot.send_message(Config.LOG_CHANNEL,
                               script.LOG_TEXT_P.format(update.from_user.id, update.from_user.mention))

    # logger.info(update)

    await bot.send_message(
        chat_id=update.chat.id,
        text=script.UPGRADE_TEXT,
        reply_to_message_id=update.id,
        disable_web_page_preview=True
    )


@Client.on_message(filters.command(["about"]))
async def about(bot, update):
    if not await rename_db.is_user_exist(update.from_user.id):
        await rename_db.add_user(update.from_user.id, update.from_user.first_name)
        await bot.send_message(Config.LOG_CHANNEL,
                               script.LOG_TEXT_P.format(update.from_user.id, update.from_user.mention))

    buttons = [[
        InlineKeyboardButton('😇 DEVELOPER', url='https://t.me/UFS_Botz')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.reply_photo(
        photo=random.choice(Config.PICS),
        caption=script.ABOUT_TEXT,
        reply_to_message_id=update.id,
        reply_markup=reply_markup
    )


@Client.on_message(filters.command("update") & filters.user(Config.ADMINS))
async def update_restart(bot, message):
    try:
        out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
        if "Already up to date." in str(out):
            return await message.reply_text("Its Already Up-To Date!")
        await message.reply_text(f"```{out}```")
    except Exception as e:
        return await message.reply_text(str(e))
    m = await message.reply_text(
        "**Updated With Default Branch, Restarting Now.**")
    await restart(m)


async def restart(message):
    if message:
        await start_restart_stage(message.chat.id, message.id)
    os.execvp(sys.executable, [sys.executable, "main.py"])


@Client.on_message(
    filters.private & (filters.document | filters.video | filters.audio | filters.voice | filters.video_note))
async def rename_cb(bot, update):
    file = update.document or update.video or update.audio or update.voice or update.video_note
    try:
        filename = file.file_name
    except:
        filename = "Not Available"

    buttons = [[
        InlineKeyboardButton('🔖 Default', callback_data="default"),
        InlineKeyboardButton('✒ Rename', callback_data="rename_button")
    ], [
        InlineKeyboardButton('⛔ Cancel', callback_data='cancel_e')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)

    await bot.send_message(
        chat_id=update.chat.id,
        text="<b>File Name</b> : <code>{}</code> \n\nSelect The Desired Option Below 😇".format(filename),
        reply_markup=reply_markup,
        reply_to_message_id=update.id,
        disable_web_page_preview=True
    )


async def cancel_extract(bot, update):
    await update.reply_to_message.reply_text(
        text="**Process Cancelled 🙃**", quote=True
    )
