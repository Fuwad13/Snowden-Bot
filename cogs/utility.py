import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import NoPrivateMessage

from utils.buttons_and_selects import SelfRoles


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage("This command can run only in a guild channel.")
        else:
            return True

    @commands.command(name = 'selfrole', hidden = True, slash_command = False)
    @commands.is_owner()
    async def _selfrole(self, ctx):
        view = SelfRoles(self.bot)
        role_ids = [874745412991479819,875449711685955694,876913032549245008,879370829882871908]
        guild = self.bot.get_guild(874735250842984458)
        role_names = [guild.get_role(r).name for r in role_ids]
        options = []
        x = 0
        for n in role_names:
            options.append(discord.SelectOption(label = str(n), value = role_ids[x]))
            x+=1
        view.children[0].options = options
        await ctx.send("Test", view = view)


def setup(bot):
    bot.add_cog(Utility(bot))
