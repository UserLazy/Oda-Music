import aiofiles
import ffmpeg
import asyncio
import os
import shutil
import psutil
import subprocess
import requests
import aiohttp
import yt_dlp

from os import path
from typing import Union
from asyncio import QueueEmpty
from PIL import Image, ImageFont, ImageDraw
from typing import Callable

from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputAudioStream

from youtube_search import YoutubeSearch

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    Voice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant

from oda.tgcalls import calls, queues
from oda.tgcalls.calls import client as ASS_ACC
from oda.database.queue import (
    get_active_chats,
    is_active_chat,
    add_active_chat,
    remove_active_chat,
    music_on,
    is_music_playing,
    music_off,
)
from oda import app
import oda.tgcalls
from oda.tgcalls import youtube
from oda.config import (
    DURATION_LIMIT,
    que,
    SUDO_USERS,
    BOT_ID,
    BOT_NAME,
    ASSNAME,
    ASSUSERNAME,
    ASSID,
    SUPPORT,
    UPDATE,
    BOT_USERNAME,
)
from oda.utils.filters import command
from oda.utils.decorators import errors, sudo_users_only
from oda.utils.administrator import adminsOnly
from oda.utils.errors import DurationLimitError
from oda.utils.gets import get_url, get_file_name
from oda.modules.admins import member_permissions
from tools.chattitle import CHAT_TITLE
from tools.admins import get_administrators
from tools.channelmusic import get_chat_id

# plus
chat_id = None
DISABLED_GROUPS = []
ACTV_CALLS = []
useer = "NaN"
flex = {}


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((190, 550), f"Title: {title}", (255, 255, 255), font=font)
    draw.text((190, 590), f"Duration: {duration}", (255, 255, 255), font=font)
    draw.text((190, 630), f"Views: {views}", (255, 255, 255), font=font)
    draw.text(
        (190, 670),
        f"Added By: {requested_by}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(
    command(["musicplayer", f"musicplayer@{BOT_USERNAME}"])
    & ~filters.edited
    & ~filters.bot
    & ~filters.private
)
async def hfmm(_, message):
    global DISABLED_GROUPS
    if message.sender_chat:
        return await message.reply_text(
            "🔴 __You're an **Anonymous Admin**!__\n│\n╰ Revert back to user account from admin rights."
        )
    permission = "can_delete_messages"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    try:
        user_id = message.from_user.id
    except:
        return
    if len(message.command) != 2:
        await message.reply_text("I only know `/musicplayer on` and `/musicplayer off`")
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status in ["ON", "on", "On"]:
        lel = await message.reply("`Processing...`")
        if message.chat.id not in DISABLED_GROUPS:
            await lel.edit(
                f"🔴 __Music player already activate in **{message.chat.title}**__"
            )
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"✅ __Music player has been turn on successfully in **{message.chat.title}**__"
        )

    elif status in ["OFF", "off", "Off"]:
        lel = await message.reply("__`Processing...`__")

        if message.chat.id in DISABLED_GROUPS:
            await lel.edit(
                f"🔴 __Music player already not active in **{message.chat.title}**__"
            )
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"✅ __Music player has been turn off successfully **{message.chat.title}**__"
        )
    else:
        await message.reply_text("I only know `/musicplayer on` and `/musicplayer off`")


@Client.on_callback_query(filters.regex(pattern=r"^(cls)$"))
async def closed(_, query: CallbackQuery):
    from_user = query.from_user
    permissions = await member_permissions(query.message.chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await query.answer(
            "You don't have enough permissions to perform this action.\n"
            + f"❌ Permission: {permission}",
            show_alert=True,
        )
    await query.message.delete()


# play
@Client.on_message(
    command(["play", f"play@{BOT_USERNAME}"])
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    chat_id = get_chat_id(message.chat)
    bttn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Command Syntax", callback_data="cmdsyntax")
            ],[
                InlineKeyboardButton("🗑 Close", callback_data="close")
            ]
        ]
    )
    
    nofound = "😕 **Couldn't find song you requested**\n\n» **Please provide the correct song name or include the artist's name as well**"
    
    global que
    global useer
    if message.chat.id in DISABLED_GROUPS:
        return
    lel = await message.reply("🔎 **Processing...**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id
    try:
        user = await ASS_ACC.get_me()
    except:
        user.first_name = "Music Assistant"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"💡 **Please add the userbot to your channel first.**",
                    )
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+","https://t.me/joinchat/")
                except:
                    await lel.edit(
                        "💡 **To use me, I need to be an Administrator** with the permissions:\n\n» ❌ __Delete messages__\n» ❌ __Ban users__\n» ❌ __Add users__\n» ❌ __Manage voice chat__\n\n**Then type /reload**",
                    )
                    return
                try:
                    await ASS_ACC.join_chat(invitelink)
                    await lel.edit(
                        f"✅ **Userbot succesfully entered chat**",
                    )
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                    f"❌ __**Assistant failed to join**__\n\n**Reason**:{e}"
                    )
    try:
        await ASS_ACC.get_chat(chid)
    except:
        await lel.edit(
            f"» **Userbot not in this chat or is banned in this group !**\n\n**unban @{ASSISTANT_NAME} and added again to this group manually, or type /reload then try again."
        )
        return
    text_links = None
    if message.reply_to_message:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            pass
        entities = {}
        toxt = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.entities:
            entities = message.reply_to_message.entities + entities
        elif message.reply_to_message.caption_entities:
            entities = message.reply_to_message.entities + entities
        urls = [
            entity for entity in entities if entity.type == "url"
        ]
        text_links = [
            entity for entity in entities if entity.type == "text_link"
        ]
    else:
        urls = None
    if text_links:
        urls = True
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    await message.delete()

    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ Videos longer than {DURATION_LIMIT} minutes aren't allowed to play!"
            )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🚨 Support", url=f"t.me/{SUPPORT}"),
                    InlineKeyboardButton("📡 Updates", url=f"t.me/{UPDATE}"),
                ],
                [InlineKeyboardButton(text="🗑 Close", callback_data="cls")],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/4c39fbb88932761913fff.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        requested_by = message.from_user.first_name
        views = "Locally added"
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await oda.tgcalls.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("🔎 **Processing...**")
        ydl_opts = {"format": "bestaudio/best"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"][:70]
            thumbnail = "https://telegra.ph/file/4c39fbb88932761913fff.png"
            thumb_name = f"{title}.jpg"
            ctitle = message.chat.title
            ctitle = await CHAT_TITLE(ctitle)
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            views = results[0]["views"]
            url_suffix = results[0]["url_suffix"]
        except Exception as e:
            await lel.delete()
            await message.reply_photo(
                photo="https://telegra.ph/file/66518ed54301654f0b126.png",
                caption=nofound,
                reply_markup=bttn,
            )
            print(str(e))
            return
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🚨 Support", url=f"t.me/{SUPPORT}"),
                    InlineKeyboardButton("📡 Updates", url=f"t.me/{UPDATE}"),
                ],
                [InlineKeyboardButton(text="🗑 Close", callback_data="cls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        def my_hook(d):
            if d["status"] == "downloading":
                percentage = d["_percent_str"]
                per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                per = int(per)
                eta = d["eta"]
                speed = d["_speed_str"]
                size = d["_total_bytes_str"]
                bytesx = d["total_bytes"]
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            lel.edit(
                                f"Downloading {title[:50]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                    except Exception as e:
                        pass
                if per > 250:
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**Downloading** {title[:50]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 500:
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**Downloading** {title[:50]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
                if per > 800:
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:
                            lel.edit(
                                f"**Downloading** {title[:50]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                            )
                        print(
                            f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                        )
            if d["status"] == "finished":
                try:
                    taken = d["_elapsed_str"]
                except Exception as e:
                    taken = "00:00"
                size = d["_total_bytes_str"]
                lel.edit(
                    f"**Downloaded** {title[:50]}.....\n\n**FileSize:** {size}\n**Time Taken:** {taken} sec\n\n**Converting File**[__FFmpeg processing__]"
                )
                print(f"[{url_suffix}] Downloaded| Elapsed: {taken} seconds")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, youtube.download, url, my_hook)
        file_path = await oda.tgcalls.convert(x)
    else:
        query = ""
        for i in message.command[1:]:
            query += " " + str(i)
        print(query)
        ydl_opts = {"format": "bestaudio/best"}

        try:
            results = YoutubeSearch(query, max_results=5).to_dict()
        except:
            await lel.edit(
                "😕 **Song name not detected**\n\n» **please provide the name of the song you want to play**"
            )
        try:
            toxxt = "\n"
            j = 0
            user = user_name
            emojilist = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
            while j < 5:
                toxxt += f"{emojilist[j]} [{results[j]['title'][:25]}...](https://youtube.com{results[j]['url_suffix']})\n"
                toxxt += f" └ 🕒 **Duration** - `{results[j]['duration']}`\n\n"
                j += 1
            toxxt += f" ⚡ __Powered by {BOT_NAME}__"
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "1️⃣", callback_data=f"plll 0|{query}|{user_id}"
                        ),
                        InlineKeyboardButton(
                            "2️⃣", callback_data=f"plll 1|{query}|{user_id}"
                        ),
                        InlineKeyboardButton(
                            "3️⃣", callback_data=f"plll 2|{query}|{user_id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "4️⃣", callback_data=f"plll 3|{query}|{user_id}"
                        ),
                        InlineKeyboardButton(
                            "5️⃣", callback_data=f"plll 4|{query}|{user_id}"
                        ),
                    ],
                    [InlineKeyboardButton(text="🗑 Close", callback_data="cls")],
                ]
            )
            await message.reply_photo(
                photo="https://telegra.ph/file/4c39fbb88932761913fff.png",
                caption=toxxt,
                reply_markup=keyboard,
            )
            await lel.delete()
            
            return
        
        except:
            pass

            try:
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:70]
                thumbnail = "https://telegra.ph/file/a7adee6cf365d74734c5d.png"
                thumb_name = f"{title}.jpg"
                ctitle = message.chat.title
                ctitle = await CHAT_TITLE(ctitle)
                thumb = requests.get(thumbnail, allow_redirects=True)
                open(thumb_name, "wb").write(thumb.content)
                duration = results[0]["duration"]
                results[0]["url_suffix"]
            except Exception as e:
                await lel.delete()
                await message.reply_photo(
                    photo="https://telegra.ph/file/66518ed54301654f0b126.png",
                    caption=nofound,
                    reply_markup=bttn,
                )
                print(str(e))
                return
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🚨 Support", url=f"t.me/{SUPPORT}"),
                        InlineKeyboardButton("📡 Updates", url=f"t.me/{UPDATE}"),
                    ],
                    [InlineKeyboardButton(text="🗑 Close", callback_data="cls")],
                ]
            )
            message.from_user.first_name
            await generate_cover(title, thumbnail, ctitle)
            file_path = await oda.tgcalls.convert(youtube.download(url))
    for x in calls.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(chat_id) in ACTV_CALLS:
        position = await queues.put(chat_id, file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await lel.delete()
        await message.reply_photo(
            photo="final.png",
            caption=f"💡 **Track added to queue »** `{position}`\n\n**🎵 Song:** [{title[:35]}...]({url})\n⏱ **Duration:** `{duration}`\n**👤 Added By:** {message.from_user.mention}",
            reply_markup=keyboard,
        )
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            await calls.pytgcalls.join_group_call(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
        except Exception as e:
            await lel.edit(
                "😕 **Voice chat not found**\n\n» please turn on the voice chat first"
            )
            return
        await lel.delete()
        await message.reply_photo(
            photo="final.png",
            caption=f"**🎵 Song:** [{title[:70]}]({url})\n**🕒 Duration:** `{duration}`\n**👤 Added By:** {message.from_user.mention}\n\n**▶️ Now Playing at `{message.chat.title}`...**\n",
            reply_markup=keyboard,
        )
        os.remove("final.png")


@Client.on_callback_query(filters.regex(pattern=r"plll"))
async def lol_cb(b, cb):
    
    bttn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Command Syntax", callback_data="cmdsyntax")
            ],[
                InlineKeyboardButton("🗑 Close", callback_data="close")
            ]
        ]
    )
    
    nofound = "😕 **Couldn't find song you requested**\n\n» **please provide the correct song name or include the artist's name as well**"
    
    global que
    cbd = cb.data.strip()
    chat_id = cb.message.chat.id
    typed_ = cbd.split(None, 1)[1]
    try:
        x, query, useer_id = typed_.split("|")
    except:
        await cb.message.reply_photo(
            photo="https://telegra.ph/file/66518ed54301654f0b126.png",
            caption=nofound,
            reply_markup=bttn,
        )
        return
    useer_id = int(useer_id)
    if cb.from_user.id != useer_id:
        await cb.answer("💡 Sorry this is not for you !", show_alert=True)
        return
    await cb.answer("💡 Downloading song you requested...", show_alert=True)
    x = int(x)
    try:
        requested_by = cb.message.reply_to_message.from_user.first_name
    except:
        requested_by = cb.message.from_user.first_name
    results = YoutubeSearch(query, max_results=5).to_dict()
    resultss = results[x]["url_suffix"]
    title = results[x]["title"][:70]
    thumbnail = results[x]["thumbnails"][0]
    duration = results[x]["duration"]
    views = results[x]["views"]
    url = f"https://youtube.com{resultss}"
    url_suffix = results[x]["url_suffix"]
    try:
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
            await cb.message.edit(
                f"❌ Videos longer than {DURATION_LIMIT} minutes aren't allowed to play!"
            )
            return
    except:
        pass
    try:
        thumb_name = f"{title}.jpg"
        ctitle = cb.message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
    except Exception as e:
        print(e)
        return
    lel = await cb.message.reply(
        f"Downloading {title[:50]}\n\n**FileSize:** NaN\n**Downloaded:** NaN\n**Speed:** NaN\n**ETA:** NaN sec"
    )
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🚨 Support", url=f"t.me/{SUPPORT}"),
                    InlineKeyboardButton("📡 Updates", url=f"t.me/{UPDATE}"),
                ],
                [InlineKeyboardButton(text="🗑 Close", callback_data="cls")],
            ]
        )
    await generate_cover(requested_by, title, views, duration, thumbnail)
    def my_hook(d):
        if d["status"] == "downloading":
            percentage = d["_percent_str"]
            per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
            per = int(per)
            eta = d["eta"]
            speed = d["_speed_str"]
            size = d["_total_bytes_str"]
            bytesx = d["total_bytes"]
            if str(bytesx) in flex:
                pass
            else:
                flex[str(bytesx)] = 1
            if flex[str(bytesx)] == 1:
                flex[str(bytesx)] += 1
                try:
                    if eta > 2:
                        lel.edit(
                            f"Downloading {title[:50]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                except Exception as e:
                    pass
            if per > 250:
                if flex[str(bytesx)] == 2:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        lel.edit(
                            f"**Downloading** {title[:50]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
            if per > 500:
                if flex[str(bytesx)] == 3:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        lel.edit(
                            f"**Downloading** {title[:50]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
            if per > 800:
                if flex[str(bytesx)] == 4:
                    flex[str(bytesx)] += 1
                    if eta > 2:
                        lel.edit(
                            f"**Downloading** {title[:50]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec"
                        )
                    print(
                        f"[{url_suffix}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                    )
        if d["status"] == "finished":
            try:
                taken = d["_elapsed_str"]
            except Exception as e:
                taken = "00:00"
            size = d["_total_bytes_str"]
            lel.edit(
                f"**Downloaded** {title[:50]}.....\n\n**FileSize:** {size}\n**Time Taken:** {taken} sec\n\n**Converting File**[__FFmpeg processing__]"
            )
            print(f"[{url_suffix}] Downloaded| Elapsed: {taken} seconds")

    loop = asyncio.get_event_loop()
    x = await loop.run_in_executor(None, youtube.download, url, my_hook)
    file_path = await oda.tgcalls.convert(x)
    if await is_active_chat(chat_id):
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await cb.message.delete()
        await b.send_photo(
            chat_id,
            photo="final.png",
            caption=f"**🎵 Song:** [{title[:35]}...]({url})\n⏱ **Duration:** `{duration}`\n**👤 Added By:** {cb.from_user.mention}\n\n**#⃣ Queued Position:** {position}",
            reply_markup=keyboard,
        )
    else:
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            await calls.pytgcalls.join_group_call(
                chat_id,
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
        except Exception:
            return await lel.edit(
            "Error Joining Voice Chat. Make sure Voice Chat is Enabled."
        )

        await music_on(chat_id)
        await add_active_chat(chat_id)
        await cb.message.delete()
        await b.send_photo(
            chat_id,
            photo="final.png",
            caption=f"**🎵 Song:** [{title[:70]}]({url})\n⏱ **Duration:** `{duration}`\n**👤 Added By:** {cb.from_user.mention}\n\n**▶️ Now Playing at `{cb.message.chat.title}`...**",
            reply_markup=keyboard
        )

    os.remove("final.png")
    return await lel.delete()