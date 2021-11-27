import asyncio
import importlib
from pyrogram import Client
from aiohttp import ClientSession
from oda import config


SUDO_USERS = config.SUDO_USERS
OWNER_ID = config.OWNER_ID
BOT_ID = config.BOT_ID
BOT_NAME = ""
BOT_USERNAME = ""
ASSID = config.ASSID
ASSNAME = ""
ASSUSERNAME = ""

app = Client(
    'odamusic',
    config.API_ID,
    config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

aiohttpsession = ClientSession()

client = Client(config.SESSION_NAME, config.API_ID, config.API_HASH)

app.start()
client.start()
