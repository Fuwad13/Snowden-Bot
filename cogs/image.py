import discord
from discord.ext import commands


class Image(commands.Cog):
	"""Image manipulation cog"""
	def __init__(self, bot):
		self.bot = bot


async def setup(bot):
	await bot.add_cog(Image(bot))
