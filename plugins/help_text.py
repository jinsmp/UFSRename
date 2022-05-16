#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Jins Mathew | @UFS_Botz | UFSBotz | @UFSBotz_Support
import asyncio
import datetime
import os
import sys
import random
import logging
import time

import pyrogram
import subprocess

from pyrogram.errors import BadRequest, UserIsBot, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, FloodWait

from helper_funcs.string_handling import get_msg_type, markdown_parser, Types
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


@Client.on_message(filters.command("dbupdate") & filters.user(Config.ADMINS))
async def db_update_all(bot, message):
    args = message.text.split(None, 2)

    if len(args) < 3:
        await message.reply("Invalid Parameter..", quote=True)
        return

    new_field = str(args[1]).lower()

    if str(args[2]).lower() == 'true':
        update = True
    else:
        update = False

    status = await rename_db.update_all(new_field, update)

    try:
        if status:
            await message.reply(f"Successfully Updated New Default Value '{args[1]}'..", quote=True)
            return
        else:
            await message.reply(f"Something Went Wrong..", quote=True)
            return
    except Exception as e:
        await message.reply(f"While Update New Default Value Got An Error {str(e)}..", quote=True)
        return


@Client.on_message(filters.command("settings"))
async def settings(bot, message):
    id = int(message.from_user.id)
    if not await rename_db.is_user_exist(message.from_user.id):
        await rename_db.add_user(message.from_user.id, message.from_user.first_name)
        await bot.send_message(Config.LOG_CHANNEL,
                               script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

    ban_user = await rename_db.get_ban_status(message.from_user.id)

    if ban_user['is_banned']:
        await message.reply_text("You are B A N N E D")
        return

    doc, update = await rename_db.get_user_by_id(message.from_user.id)

    if doc:
        upload_type = "Upload As File 📁"
    else:
        upload_type = "Upload As Video 🎞"

    if update:
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

    await message.reply_text(
        text="<b>Change My Settings As Your Wish ⚙</b>",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        reply_to_message_id=message.id
    )


@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMINS) & filters.reply)
async def broadcast(bot, message):
    all_users = await rename_db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Please Wait, Broadcasting Is Starting Soon...', quote=True
    )
    start_time = time.time()
    total_users = await rename_db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0

    i = 0
    b = 0
    ia = 0
    ub = 0

    success = 0
    text, data_type, content, buttons = get_msg_type(b_msg)
    for user in all_users:
        i += 1
        if user['id'] in Config.ADMINS and user['update']:
            try:
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`")
                success += 1
                await send_broadcast_message(user['id'], text, data_type, content, buttons, bot, message)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`")
                success += 1
                await send_broadcast_message(user['id'], text, data_type, content, buttons, bot, message)
            except UserIsBlocked:
                b += 1
                logging.info(f"{user['id']} - Blocked the bot.")
                blocked += 1
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`")
                pass
            except InputUserDeactivated:
                ia += 1
                await rename_db.delete_user(int(user['id']))
                deleted += 1
                logging.info(f"{user['id']} - Removed from Database, Since Deleted Account.")
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`")
                pass
            except UserIsBot:
                ub += 1
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`")
                pass
            except PeerIdInvalid:
                await rename_db.delete_user(int(user['id']))
                logging.info(f"{user['id']} - PeerIdInvalid")
                pass
            except Exception as err:
                logging.info(f"{str(err)}")
                return
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit_text(
        f"Broadcast Completed:\n"
        f"Completed in {time_taken} seconds.\n\n"
        f"Total Users {total_users}\n"
        f"Completed: {done} / {total_users}\n"
        f"Success: {success}\nBlocked: {blocked}\n"
        f"Deleted: {deleted}")


async def send_broadcast_message(user_id, text, data_type, content, buttons, client, message):
    if message.from_user.id in Config.ADMINS:
        if data_type != Types.TEXT and data_type != Types.BUTTON_TEXT and \
                data_type != Types.PHOTO and data_type != Types.BUTTON_PHOTO:
            if data_type == 2:
                await client.send_sticker(chat_id=user_id, sticker=content)
            elif data_type == 3:
                await client.send_document(chat_id=user_id, document=content)
            elif data_type == 6:
                await client.send_audio(chat_id=user_id, audio=content)
            elif data_type == 7:
                await client.send_voice(chat_id=user_id, voice=content)
            elif data_type == 8:
                await client.send_video(chat_id=user_id, video=content)
            return
        # else, move on

        if data_type != 0:
            # buttons = get_schedule_buttons(job.s_job_name)
            keyb = build_url_keyboard(buttons)
        else:
            keyb = []

        keyboard = InlineKeyboardMarkup(keyb)

        if data_type == Types.BUTTON_PHOTO:
            await client.send_photo(user_id, content, caption=text, reply_markup=keyboard)
        elif data_type == Types.PHOTO:
            await client.send_photo(user_id, content, caption=text)
        else:
            # send(client, job.s_chat_id, msg_text, keyboard, "Hey Dear, how are you?")
            try:
                if len(keyboard.inline_keyboard) > 0:
                    await client.send_message(chat_id=user_id, text=text,
                                              reply_markup=keyboard,
                                              disable_web_page_preview=True)
                else:
                    await client.send_message(chat_id=user_id, text=text,
                                              disable_web_page_preview=True)
            except IndexError:
                await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                         "\nNote: The Current Message Was "
                                                         "Invalid Due To Markdown Issues. Could Be "
                                                         "Due To The User's Name."),
                                         disable_web_page_preview=True)
            except KeyError:
                await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                         "\nNote: The Current Message Is "
                                                         "Invalid Due To An Issue With Some Misplaced "
                                                         "Messages. Please Update"),
                                         disable_web_page_preview=True)
            except UserIsBlocked:
                pass
            except InputUserDeactivated:
                pass
            except UserIsBot:
                pass
            except BadRequest as excp:
                if excp.MESSAGE == "Button_url_invalid":
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: The Current Message Has An Invalid Url "
                                                             "In One Of Its Buttons. Please Update."))
                elif excp.MESSAGE == "Unsupported url protocol":
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: The Current Message Has Buttons Which "
                                                             "Use Url Protocols That Are Unsupported By "
                                                             "Telegram. Please Update."))
                elif excp.MESSAGE == "Wrong url host":
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: The Current Message Has Some Bad Urls. "
                                                             "Please Update."))
                    logging.warning(text)
                    logging.warning(keyboard)
                    logging.exception("Could Not Parse! Got Invalid Url Host Errors")
                else:
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: An Error Occured When Sending The "
                                                             "Custom Message. Please Update."))
                    logging.exception(excp.MESSAGE)
    else:
        await message.reply_text("Who The Hell You Are To Send This Command To Me...😡")
        return


def build_url_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])

    return keyb


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
