import os
import asyncio
import io
import sys
import traceback
from eugeo import tbot
from eugeo import CMD_HELP, VIRUS_API_KEY
from telethon import events
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import MessageMediaDocument, DocumentAttributeFilename
from eugeo.events import register
from eugeo.function import is_register_admin
import cloudmersive_virus_api_client


configuration = cloudmersive_virus_api_client.Configuration()
configuration.api_key["Apikey"] = VIRUS_API_KEY
api_instance = cloudmersive_virus_api_client.ScanApi(
    cloudmersive_virus_api_client.ApiClient(configuration)
)
allow_executables = True
allow_invalid_files = True
allow_scripts = True
allow_password_protected_files = True


@register(pattern="^/scanit$")
async def virusscan(event):
    if event.is_group:
        if not await is_register_admin(event.input_chat, event.message.sender_id):
            await event.reply("Please use this command in PM!")
            return
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.reply("Reply to a file to scan it.")
        return

    c = await event.get_reply_message()
    try:
        c.media.document
    except Exception:
        await event.reply("Thats not a file.")
        return
    h = c.media
    try:
        k = h.document.attributes
    except Exception:
        await event.reply("Thats not a file.")
        return
    if not isinstance(h, MessageMediaDocument):
        await event.reply("Thats not a file.")
        return
    if not isinstance(k[0], DocumentAttributeFilename):
        await event.reply("Thats not a file.")
        return
    try:
        virus = c.file.name
        await event.client.download_file(c, virus)
        gg = await event.reply("Scanning the file ...")
        fsize = c.file.size
        if not fsize <= 3145700:  # MAX = 3MB
            await gg.edit("File size exceeds 3MB")
            return
        api_response = api_instance.scan_file_advanced(
            c.file.name,
            allow_executables=allow_executables,
            allow_invalid_files=allow_invalid_files,
            allow_scripts=allow_scripts,
            allow_password_protected_files=allow_password_protected_files,
        )
        if api_response.clean_result is True:
            await gg.edit("This file is safe ✔️\nNo virus detected 🐞")
        else:
            await gg.edit("This file is Dangerous ☠️️\nVirus detected 🐞")
        os.remove(virus)
    except Exception as e:
        print(e)
        os.remove(virus)
        await gg.edit("Some error occurred..")
        return



file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /scanit: Scan a file for virus (MAX SIZE = 3MB)
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
