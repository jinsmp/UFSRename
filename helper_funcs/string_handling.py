import re
import re
import time
from enum import unique, IntEnum

import emoji
from typing import Dict, List
from pyrogram.types import InlineKeyboardButton, MessageEntity

MATCH_MD = re.compile(r'\*(.*?)\*|'
                      r'_(.*?)_|'
                      r'`(.*?)`|'
                      r'(?<!\\)(\[.*?\])(\(.*?\))|'
                      r'(?P<esc>[*_`\[])')
LINK_REGEX = re.compile(r'(?<!\\)\[.+?\]\((.*?)\)')
BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)


@unique
class Types(IntEnum):
    TEXT = 0
    BUTTON_TEXT = 1
    STICKER = 2
    DOCUMENT = 3
    PHOTO = 4
    BUTTON_PHOTO = 5
    AUDIO = 6
    VOICE = 7
    VIDEO = 8


def get_msg_type(msg):
    data_type = None
    content = None
    text = ""

    if msg.media:
        user_message = "/setmessage"
    else:
        user_message = "/setmessage " + msg.text
    args = user_message.split(None, 1)  # use python's maxsplit to separate cmd and args

    buttons = []
    # determine what the contents of the filter are - text, image, sticker, etc
    if len(args) >= 2:
        offset = len(args[1]) - len(user_message)  # set correct offset relative to command + notename
        # it = iter(msg.entities)
        # res_dct = dict(zip(it, it))
        # lst_dic = []
        # for lst in msg.entities():
        #     lst_dic = lst

        text, buttons = button_markdown_parser(args[1], entities=msg.entities, offset=offset)
        if buttons:
            data_type = Types.BUTTON_TEXT
        else:
            data_type = Types.TEXT

    elif msg and msg.sticker:
        content = msg.sticker.file_id
        text = msg.text
        data_type = Types.STICKER

    elif msg and msg.document:
        content = msg.document.file_id
        text = msg.text
        data_type = Types.DOCUMENT

    elif msg and msg.photo:
        content = msg.photo.file_id  # last elem = best quality
        text = msg.caption     # text
        # data_type = Types.PHOTO

        # offset = len(args[1]) - len(msg.text)  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(msg.caption, entities=msg.entities)
        if buttons:
            data_type = Types.BUTTON_PHOTO
        else:
            data_type = Types.PHOTO

    elif msg and msg.audio:
        content = msg.audio.file_id
        text = msg.text
        data_type = Types.AUDIO

    elif msg and msg.voice:
        content = msg.voice.file_id
        text = msg.text
        data_type = Types.VOICE

    elif msg and msg.video:
        content = msg.video.file_id
        text = msg.text
        data_type = Types.VIDEO

    return text, data_type, content, buttons


def button_markdown_parser(txt: str, entities: Dict[MessageEntity, str] = None, offset: int = 0) -> (str, List):
    markdown_note = markdown_parser(txt, entities, offset)
    prev = 0
    note_data = ""
    buttons = []
    for match in BTN_URL_REGEX.finditer(markdown_note):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            # create a thruple with button label, url, and newline status
            buttons.append((match.group(2), match.group(4), bool(match.group(5))))
            note_data += markdown_note[prev:match.start(1)]
            prev = match.end(1)
        # if odd, escaped -> move along
        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += markdown_note[prev:]

    return note_data, buttons


def markdown_parser(txt: str, entities: Dict[MessageEntity, str] = None, offset: int = 0) -> str:
    """
    Parse a string, escaping all invalid markdown entities.
    Escapes URL's so as to avoid URL mangling.
    Re-adds any telegram code entities obtained from the entities object.
    :param txt: text to parse
    :param entities: dict of message entities in text
    :param offset: message offset - command and notename length
    :return: valid markdown string
    """
    if not entities:
        entities = {}
    if not txt:
        return ""

    prev = 0
    res = ""
    # Loop over all message entities, and:
    # reinsert code
    # escape free-standing urls
    for ent in entities:
        if ent.offset < -offset:
            continue

        start = ent.offset + offset  # start of entity
        end = ent.offset + offset + ent.length - 1  # end of entity

        # we only care about bold, code, url, text links
        if ent.type in ("bold", "code", "url", "text_link"):
            # count emoji to switch counter
            count = _calc_emoji_offset(txt[:start])
            start -= count
            end -= count

            # URL handling -> do not escape if in [](), escape otherwise.
            if ent.type == "url":
                if any(match.start(1) <= start and end <= match.end(1) for match in LINK_REGEX.finditer(txt)):
                    continue
                # else, check the escapes between the prev and last and forcefully escape the url to avoid mangling
                else:
                    # TODO: investigate possible offset bug when lots of emoji are present
                    res += _selective_escape(txt[prev:start] or "") + escape_markdown(txt)

            # code handling
            elif ent.type == "code":
                res += _selective_escape(txt[prev:start]) + '`' + txt + '`'

            # code handling
            elif ent.type == "bold":
                res += _selective_escape(txt[prev:start]) + '`' + txt + '`'

            # handle markdown/html links
            elif ent.type == "text_link":
                res += _selective_escape(txt[prev:start]) + "[{}]({})".format(txt, ent.url)

            end += 1

        # anything else
        else:
            continue

        prev = end

    res += _selective_escape(txt[prev:])  # add the rest of the text
    return res


# This is a fun one.
def _calc_emoji_offset(to_calc) -> int:
    # Get all emoji in text.
    emoticons = emoji.get_emoji_regexp().finditer(to_calc)
    # Check the utf16 length of the emoji to determine the offset it caused.
    # Normal, 1 character emoji don't affect; hence sub 1.
    # special, eg with two emoji characters (eg face, and skin col) will have length 2, so by subbing one we
    # know we'll get one extra offset,
    return sum(len(e.group(0).encode('utf-16-le')) // 2 - 1 for e in emoticons)


def _selective_escape(to_parse: str) -> str:
    """
    Escape all invalid markdown
    :param to_parse: text to escape
    :return: valid markdown string
    """
    offset = 0  # offset to be used as adding a \ character causes the string to shift
    for match in MATCH_MD.finditer(to_parse):
        if match.group('esc'):
            ent_start = match.start()
            to_parse = to_parse[:ent_start + offset] + '\\' + to_parse[ent_start + offset:]
            offset += 1
    return to_parse


def escape_markdown(text):
    """Helper function to escape telegram markup symbols."""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)