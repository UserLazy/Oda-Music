import os
import sys
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from oda import app
from oda.config import OWNER_ID
from oda.database.chats import blacklist_chat, blacklisted_chats, whitelist_chat
from oda.utils.decorators import sudo_users_only
from oda.utils.filters import command
from oda.modules import check_heroku


@app.on_message(command(["rebootmusic", "restart"]) & filters.user(OWNER_ID))
@check_heroku
async def gib_restart(client, message, hap):
    msg_ = await message.reply_text("[Oda Music] - Restarting...")
    hap.restart()


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(command(["exec"]) & ~filters.edited)
@sudo_users_only
async def executor(client, message):
    if len(message.command) < 2:
        return await edit_or_reply(
            message, text="__please give me some command to execute.__"
        )
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()
    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"**OUTPUT**:\n\n```{evaluation.strip()}```"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation.strip()))
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="⏳", callback_data=f"runtime {t2-t1} Seconds")]]
        )
        await message.reply_document(
            document=filename,
            caption=f"**INPUT:**\n`{cmd[0:980]}`\n\n**OUTPUT:**\n`Attached Document`",
            quote=False,
            reply_markup=keyboard,
        )
        await message.delete()
        os.remove(filename)
    else:
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳",
                        callback_data=f"runtime {round(t2-t1, 3)} Seconds",
                    )
                ]
            ]
        )
        await edit_or_reply(message, text=final_output, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"runtime"))
async def runtime_func_cq(_, cq):
    runtime = cq.data.split(None, 1)[1]
    await cq.answer(runtime, show_alert=True)


@app.on_message(command("bchat") & filters.edited)
@sudo_users_only
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("**Usage:**\n/bchat <chat_id>")
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text("Chat is already blacklisted.")
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text("Chat has been successfully blacklisted")
    await message.reply_text("Something wrong happened, check logs.")


@app.on_message(command("wchat") & filters.edited)
@sudo_users_only
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("**Usage:**\n/wchat <chat_id>")
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text("Chat is already whitelisted.")
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text("Chat has been successfully whitelisted")
    await message.reply_text("Something wrong happened, check logs.")


@app.on_message(command("blacklisted") & filters.edited)
@sudo_users_only
async def blacklisted_chats_func(_, message: Message):
    text = ""
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "Private"
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    await message.reply_text(text)
