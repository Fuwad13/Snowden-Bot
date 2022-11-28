from discord import emoji
from discord.ext import commands 
import discord
import sys
import traceback

from discord.ext.commands import errors
from discord.ui import view
from utils.errors import NotStartedPlaying, NotOptedIn, NoWeaponEquipped, NotEnoughAmmo
from utils.emojis import EMOJIS
from utils.buttons_and_selects import Guide
class ErrorHandler(commands.Cog):
	"""Cog for error handling"""
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
			await ctx.send(f"This command can only run in a guild/server.")

		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"You're on cooldown! Please retry after `{error.retry_after:.2f}` seconds")
		elif isinstance(error, commands.MaxConcurrencyReached):
			await ctx.send(f"{error}")

		elif isinstance(error, commands.NotOwner):
			await ctx.send('L')

		elif isinstance(error, NotStartedPlaying):
			await ctx.send(error, view= Guide(ctx))

		elif isinstance(error, NotOptedIn):
			await ctx.send(error, view= Guide(ctx))

		elif isinstance(error, NoWeaponEquipped):
			await ctx.send(error, view= Guide(ctx))

		elif isinstance(error, NotEnoughAmmo):
			await ctx.send(error)
		elif isinstance(error, commands.MissingPermissions):
			needed_perms = '\n'.join(error.missing_permissions)
			await ctx.send(f"{EMOJIS['redtick']} **You need the following permission(s) to execute this command**\n**{needed_perms}**")

		elif isinstance(error, commands.BotMissingPermissions):
			needed_perms = '\n'.join(error.missing_permissions)
			await ctx.send(f"**I need the following permission(s) to execute this command**\n**{needed_perms}**")
		elif isinstance(error, commands.MemberNotFound):
			await ctx.send(f"Member not found....", delete_after = 10)
		else:
			await ctx.send(error)
			
			

			

		


async def setup(bot):
	await bot.add_cog(ErrorHandler(bot))

