import discord
from discord.ext import commands


class Miscellanous(commands.Cog):
	"""Miscellanous cog"""
	def __init__(self, bot):
		self.bot = bot

	

	


def setup(bot):
	bot.add_cog(Miscellanous(bot))
