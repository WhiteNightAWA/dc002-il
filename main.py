import os
import discord

from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="b.", intents=intents
)





if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
