import time
import typing
from discord.ext.commands.core import check
from discord.ext.commands.errors import NoPrivateMessage
import humanize
import discord
from discord.ext import commands
from utils.emojis import EMOJIS

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage("This command can run only in a guild channel.")
        else:
            return True


    @commands.command(name='slowmode', aliases =['sm'], help="Set the slowmode for a TextChannel.")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels = True)
    async def slowmode(self, ctx, seconds : int = 0):
        channel = ctx.channel
        if seconds > 21600:
            return await ctx.send("Maximum amount of slowmode delay is `6 hours` or `21600 seconds`", delete_after=10)
        await channel.edit(slowmode_delay=seconds, reason=f"responsible user - {ctx.author}")
        return await ctx.send(f"{EMOJIS['greentick']} Set the slowmode to **{humanize.precisedelta(seconds)}**")

    @commands.group(name= "purge", aliases = ['cleanup'], help= "Bulk delete messages of a channel, specify the amount of messages to be deleted `(default 5)`", invoke_without_command = True)
    @commands.has_permissions(manage_messages= True)
    @commands.bot_has_permissions(manage_messages= True)
    async def _purge(self, ctx, amount : int = 5):
        if amount > 2000:
            return await ctx.send("**Can't delete more than 2000 messages at once!**")
        def is_deleteable(message):
            return (time.time() - message.created_at.timestamp()) < 1209600
        deleted = await ctx.channel.purge(limit= amount, before = ctx.message.created_at, check = is_deleteable)
        await ctx.send(f"**Deleted {len(deleted)} message(s)**" , delete_after = 5)

    @_purge.command(name= "links", aliases = ['link', 'url'], help = "Bulk delete messages that contains links/url.")
    @commands.has_permissions(manage_messages= True)
    @commands.bot_has_permissions(manage_messages = True)
    async def links(self, ctx, amount : int = 5):
        if amount > 2000:
            return await ctx.send("**Can't delete more than 2000 messages at once!**")
        def is_link(message):
            ...
        k = "kdk"
    


def setup(bot):
    bot.add_cog(Moderation(bot))
