import os
import asyncio

from pyrogram import Client
from pyrogram.errors import UserIsBot

from oda.config import API_ID, API_HASH


async def genStrSession() -> None:
    async with Client(
        "Music",
        API_ID or input("Enter Telegram APP ID: "),
        API_HASH or input("Enter Telegram API HASH: "),
    ) as music:
        print("\nprocessing...")
        doneStr = "sent to saved messages!"
        try:
            await music.send_message(
                "me",
                f"#ODA #PYROGRAM_STRING_SESSION\n\n```{await music.export_session_string()}```",
            )
        except UserIsBot:
            doneStr = "successfully printed!"
            print(await music.export_session_string())
        print(f"Done !, session string has been {doneStr}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(genStrSession())
