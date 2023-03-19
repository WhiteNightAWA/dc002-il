import asyncio
import os
import discord

from dotenv import load_dotenv
from discord.ext import commands

from function import checkBotState, Close

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="b.", intents=intents
)


@bot.command()
async def reload(ctx):
    if not checkBotState(): await Close(ctx); return
    await init()
    await ctx.reply("成功!! (ﾉ◕ヮ◕)ﾉ*.✧")

async def init():
    for folder in ["commands", "events"]:
        for file in os.listdir(f"./cogs/{folder}"):
            if file.endswith(".py"):
                try:
                    await bot.unload_extension(f"cogs.{folder}.{file[:-3]}")
                    await bot.load_extension(f"cogs.{folder}.{file[:-3]}")
                except:
                    await bot.load_extension(f"cogs.{folder}.{file[:-3]}")


@bot.event
async def on_ready():
    await init()

if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
