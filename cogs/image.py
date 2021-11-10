import discord
from discord.ext import commands


class Image(commands.Cog):
	"""Image manipulation cog"""
	def __init__(self, bot):
		self.bot = bot


def setup(bot):
	bot.add_cog(Image(bot))
