import asyncio
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
        await ctx.send(f"Please use the subcommands to setup/edit/delete selfrole menus!")


    @selfroles.command(name= 'setup', aliases = ['set'], slash_commands = False, help = "Setup a selfrole menu interactively.", hidden = True)
    @commands.has_permissions(manage_guild = True)
    @commands.bot_has_permissions(manage_roles = True, manage_server = True)
    @commands.max_concurrency(1, BucketType.guild)
    async def setup(self, ctx):
        m1 = await ctx.send(f"{ctx.author.mention}, Type the message you want to set for the `selfrole menus's` message......")
        def check(m):
            return m.author == ctx.author
        try:
            msg = self.bot.wait_for('message', check = check, timeout = 60)
        except asyncio.TimeoutError:
            await m1.edit("Timed out")
        else:
            m2 = await ctx.send(f"Alright, cool. Type in the roles and ")

    @commands.command(name= 'selfroletest')
    @commands.is_owner()
    async def selfroletest(self, ctx):
        ...

def setup(bot):
    bot.add_cog(Utility(bot))


774289238748692492
874878092252942397
778705953683275796
778702304718880768
