import discord
from discord.ext import commands

class NotStartedPlaying(commands.CheckFailure):
    pass

class NotOptedIn(commands.CheckFailure):
    pass