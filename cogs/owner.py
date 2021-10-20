import discord
from discord.ext import commands


class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.group(name = 'db',aliases = ['psql'], hidden = True, invoke_without_command = True)
	@commands.is_owner()
	async def db(self, ctx):
		await ctx.send("Ok")

	
	@db.command(name = 'fetchval', aliases = ['getval'], hidden = True)
	@commands.is_owner()
	async def _fetchval(self, ctx, query: str, *args):
		val = await self.bot.db.fetchval(query, args)
		await ctx.send(val)


	

	


def setup(bot):
	bot.add_cog(Owner(bot))