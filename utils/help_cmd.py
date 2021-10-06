import discord 
from discord.ext import commands


class SnowdenHelp(commands.MinimalHelpCommand):
	def __init__(self):
		super().__init__(
            command_attrs={
                'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
                'help': 'Shows help about the bot, a command, or a category',
                        'brief': 'run help [command_name/category] to get more information about the command',
                        'aliases': ["commands", "helo", "hel", "hell", "h"],
            }, verify_checks=False, show_hidden=False
        )
	
	async def get_command_signature(self, command):
		return f"{self.context.clean_prefix}{command.qualified_name} {command.signature} "

	


