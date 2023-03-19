from discord.ext import commands

from cogs.core import Core
from function import changeBotState


class Switch(Core):

    @commands.command()
    async def switch(self, ctx):
        if ctx.author.id in [455259347107446794, 808695057930649600, 981720905187205174]:
            re = changeBotState()
            await ctx.reply(f"Now the bot state is {re}")
        else:
            await ctx.reply("U don't have permission to do this.")


async def setup(bot):
    await bot.add_cog(Switch(bot))
