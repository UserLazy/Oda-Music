import os
import asyncio

from pyrogram import Client
from pyrogram.types import Message

from oda import app, db_mem
from oda.config import get_queue
from oda.database.queue import is_active_chat
from oda.utils.filters import command


loop = asyncio.get_event_loop()


@app.on_message(command("queue"))
async def activevc(_, message: Message):
    global get_queue
    if await is_active_chat(message.chat.id):
        mystic = await message.reply_text("Please Wait... Getting Queue..")
        dur_left = db_mem[message.chat.id]["left"]
        duration_min = db_mem[message.chat.id]["total"]
        got_queue = get_queue.get(message.chat.id)
        if not got_queue:
            await mystic.edit(f"Nothing in Queue")
        fetched = []
        for get in got_queue:
            fetched.append(get)

        ### Results
        current_playing = fetched[0][0]
        user_name = fetched[0][1]

        msg = "**Queued List**\n\n"
        msg += "**Currently Playing:**"
        msg += "\n▶️" + current_playing[:30]
        msg += f"\n   ╚By:- {user_name}"
        msg += f"\n   ╚Duration:- Remaining `{dur_left}` out of `{duration_min}` Mins."
        fetched.pop(0)
        if fetched:
            msg += "\n\n"
            msg += "**Up Next In Queue:**"
            for song in fetched:
                name = song[0][:30]
                usr = song[1]
                dur = song[2]
                msg += f"\n⏸️{name}"
                msg += f"\n   ╠Duration : {dur}"
                msg += f"\n   ╚Requested by : {usr}\n"
        if len(msg) > 4096:
            await mystic.delete()
            filename = "queue.txt"
            with open(filename, "w+", encoding="utf8") as out_file:
                out_file.write(str(msg.strip()))
            await message.reply_document(
                document=filename,
                caption=f"**OUTPUT:**\n\n`Queued List`",
                quote=False,
            )
            os.remove(filename)
        else:
            await mystic.edit(msg)
    else:
        await message.reply_text(f"Nothing in Queue")
