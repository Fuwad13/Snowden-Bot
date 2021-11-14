import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import NoPrivateMessage


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage("This command can run only in a guild channel.")
        else:
            return True

    @commands.group(name= 'selfroles', aliases = ['selfrole', 'selectroles', 'selectrole'], help = "Make a dropdown or button menu for members to select their roles!", invoke_without_command = True, hidden = True)
    @commands.has_permissions(manage_guild = True)
    @commands.bot_has_permissions(manage_roles = True, manage_server = True)
    @commands.max_concurrency(1, BucketType.guild)
    async def selfroles(self, ctx):
        await ctx.send(f"Please use the subcommands to set/edit/delete selfrole menus!")

def setup(bot):
    bot.add_cog(Utility(bot))