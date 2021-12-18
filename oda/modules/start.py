from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from oda import app
from oda.utils.filters import command
from oda.config import BOT_USERNAME, BOT_NAME, SUPPORT, UPDATE


home_text_pm = (
    f"Hey there! My name is {BOT_NAME}. I can play music on"
    + "group with lots of useful commands, feel free to "
    + "add me to your group."
)

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Help ❓",
                url=f"t.me/{BOT_USERNAME}?start=help",
            ),
            InlineKeyboardButton(
                text="Repo 🛠",
                url="https://github.com/UserLazy/Oda-Music",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Updates 💻",
                url=f"t.me/{UPDATE}",
            ),
            InlineKeyboardButton(text="Support 👨", url=f"t.me/{SUPPORT}"),
        ],
        [
            InlineKeyboardButton(
                text="Add Me To Your Group 🎉",
                url=f"http://t.me/{BOT_USERNAME}?startgroup=new",
            )
        ],
    ]
)


@app.on_message(command(["start"]) & filters.private & ~filters.edited)
async def start(_, message):
    await message.reply(
        home_text_pm,
        reply_markup=home_keyboard_pm,
    )


@app.on_message(command("help") & filters.private & ~filters.edited)
async def help(client: Client, message: Message):
    await message.reply_text(
        f"""<b>Hi {message.from_user.mention()}!
\n/play (song title/link/audio) — To Play the song you requested via YouTube
/song (song title) - To Download songs from YouTube
/search (video title) — To Search Videos on YouTube with details
\n**Admins Only:**
/pause - To Pause Song playback
/resume - To resume playback of the paused song
/skip - To Skip playback of the song to the next Song
/end - To Stop Song playback
/cleandb - To clear all queues
/userbotjoin - To Invite assistant to your chat
/userbotleave - To remove assistant from your chat
</b>""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Support 👨", url=f"https://t.me/{SUPPORT}"),
                    InlineKeyboardButton("Updates", url=f"https://t.me/{UPDATE}"),
                ]
            ]
        ),
    )
