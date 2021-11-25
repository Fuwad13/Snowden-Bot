import discord
from discord.ext import commands

class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name = 'logs', aliases = ['logging', 'logger', 'log'], slash_command = False, help = "The logging module. Enable it and set a channel for logging moderation events and more.", invoke_without_command = True, hidden = True)
    @commands.guild_only()
    @commands.check_any(commands.has_permissions(manage_guild = True), commands.is_owner())
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def _logs(self, ctx):
        ...