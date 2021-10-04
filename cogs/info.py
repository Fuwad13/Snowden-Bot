import discord
from discord.ext import commands


class Information(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'ping', aliases = ['pong'], brief = "Shows bot's websocket latency in ms", help = "Shows bot's websocket latency in ms")
	async def ping(self, ctx):
		await ctx.send(f"PONG!! {round(self.bot.latency*1000)} ms")


def setup(bot):
	bot.add_cog(Information(bot))
