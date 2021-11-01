import discord
from discord.ext import commands

class NotStartedPlaying(commands.CheckFailure):
    pass

class NotOptedIn(commands.CheckFailure):
    pass

class NoWeaponEquipped(commands.CheckFailure):
    pass

class NotEnoughAmmo(commands.CheckFailure):
    pass