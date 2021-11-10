import discord 
from discord.ext import commands


class SnowdenHelp(commands.MinimalHelpCommand):
	def __init__(self):
		super().__init__(
			command_attrs={
				'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
				'help': 'Shows help about the bot, a command, or a category',
						'brief': 'run help [command_name/category] to get more information about the command',
						'aliases': ["commands", "helo", "hel", "hell"],
			}, verify_checks=False, show_hidden=False
		)

	# def get_command_signature(self, command : commands.Command):
	# 	sig = command.usage or f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"
	# 	return sig

	# async def send_bot_help(self, mapping):
	# 	ignored_cogs = ['jishaku', 'owner', 'errorhanlder']
	# 	all_cogs = []

	# 	for cog, commands in mapping.items():
	# 		if cog is None or cog.qualified_name.lower() in ignored_cogs:
	# 			continue
	# 		if not len(commands) == 0:
	# 			continue
	# 		all_cogs.append(cog.qualified_name)
		