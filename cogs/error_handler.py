from discord.ext import commands 
import discord
import sys
import traceback

from discord.ext.commands import errors
from utils.errors import NotStartedPlaying, NotOptedIn, NoWeaponEquipped, NotEnoughAmmo

class ErrorHandler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.Cog.listener('on_command_error')
	async def snowden_error_handler(self, ctx, error):
		
		if hasattr(ctx.command, 'on_error'):
			return
		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return
		error = getattr(error, 'original', error)

		if isinstance(error, commands.CommandNotFound):
			return
		elif isinstance(error, commands.DisabledCommand):
			await ctx.send(f'{ctx.command} has been disabled.')

		elif isinstance(error, commands.NoPrivateMessage):
			await ctx.send(f"This command can only be run in a guild/server.")

		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"You're on cooldown! Please retry after `{error.retry_after:.2}` seconds")

		elif isinstance(error, commands.NotOwner):
			await ctx.send('L')

		elif isinstance(error, NotStartedPlaying):
			await ctx.send(error)

		elif isinstance(error, NotOptedIn):
			await ctx.send(error)

		elif isinstance(error, NoWeaponEquipped):
			await ctx.send(error)

		elif isinstance(error, NotEnoughAmmo):
			await ctx.send(error)
			

			

		


def setup(bot):
	bot.add_cog(ErrorHandler(bot))

