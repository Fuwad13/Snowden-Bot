import typing
import humanize
import discord
from discord.ext import commands
from utils.emojis import EMOJIS

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='slowmode', aliases =['sm'], help="Set the slowmode for a TextChannel.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(admin = True)
    async def slowmode(self, ctx, seconds : int = 0, channel : typing.Optional[discord.TextChannel]=None):
        if not channel:
            channel = ctx.channel
            if seconds > 21600:
                return await ctx.send("Maximum amount of slowmode delay is `6 hours or 21600 seconds`", delete_after=5)
            await channel.edit(slowmode_delay=seconds, reason=f"responsible user - {ctx.author}")
            return await ctx.send(f"{EMOJIS['greentick']} Set the slowmode to **{humanize.precisedelta(seconds)}** for {channel.mention}")
        if seconds > 21600:
            return await ctx.send("Maximum amount of slowmode delay is `6 hours` or `21600 seconds`", delete_after=5)
        await channel.edit(slowmode_delay=seconds, reason=f"responsible user - {ctx.author}")
        return await ctx.send(f"{EMOJIS['greentick']} Set the slowmode to **{humanize.precisedelta(seconds)}** for {channel.mention}")


def setup(bot):
    bot.add_cog(Moderation(bot))