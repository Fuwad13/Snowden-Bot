from discord.ext import commands 
import discord
import sys 
import traceback

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
			

		


def setup(bot):
	bot.add_cog(ErrorHandler(bot))

