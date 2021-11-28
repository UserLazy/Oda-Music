import asyncio

from oda import app
from oda.config import SUDO_USERS
from oda.utils.filters import command
from oda.database.chats import (add_served_chat, add_served_user, blacklisted_chats, get_served_chats)
                                
chat_watcher_group = 10

@app.on_message(group=chat_watcher_group)
async def chat_watcher_func(_, message):
    if message.from_user:
        user_id = message.from_user.id
        await add_served_user(user_id)

    chat_id = message.chat.id
    blacklisted_chats_list = await blacklisted_chats()

    if not chat_id:
        return

    if chat_id in blacklisted_chats_list:
        return await app.leave_chat(chat_id)

    await add_served_chat(chat_id)
    
    
@app.on_message(command("gcast") & filters.user(SUDO_USERS))
async def broadcast_message(_, message):
    if not message.reply_to_message:
        pass
    else :
        x = message.reply_to_message.message_id   
        y = message.chat.id
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                try:
                    await m.pin(disable_notification=False)
                    pin += 1
                except Exception:
                    pass
                await asyncio.sleep(.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(f"**Broadcasted Message In {sent}  Chats with {pin} Pins.**")  
        return
    if len(message.command) < 2:
        await message.reply_text("**Usage**:\n/broadcast [MESSAGE]")
        return  
    text = message.text.split(None, 1)[1]
    sent = 0
    pin = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            try:
                await m.pin(disable_notification=False)
                pin += 1
            except Exception:
                pass
            await asyncio.sleep(.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(f"**Broadcasted Message In {sent} Chats and {pin} Pins.**")
