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

class Blacklisted(commands.CheckFailure):
    pass

class ArgumentBaseError(commands.UserInputError):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class UserLocked(ArgumentBaseError):
    pass