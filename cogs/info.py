import discord
from discord.ext import commands


class Information(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'ping', aliases = ['pong'], brief = "Shows bot's websocket latency in ms", help = "Shows bot's websocket latency in ms")
	async def ping(self, ctx):
		await ctx.send(f"PONG!! {round(self.bot.latency*1000)} ms")

	@commands.command()
	async def avatar(self, ctx, *, user: Union[discord.Member, discord.User] = None):
		"""Shows a user's enlarged avatar (if possible)."""
		embed = discord.Embed()
		user = user or ctx.author
		avatar = user.display_avatar.with_static_format('png')
		embed.set_author(name=str(user), url=avatar)
		embed.set_image(url=avatar)
		await ctx.send(embed=embed)

	


def setup(bot):
	bot.add_cog(Information(bot))
