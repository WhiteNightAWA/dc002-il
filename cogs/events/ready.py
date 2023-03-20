import os

from discord.ext import commands

from cogs.core import Core

class Ready(Core):

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")


async def setup(bot):
    await bot.add_cog(Ready(bot))
