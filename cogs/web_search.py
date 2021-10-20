import discord
from discord.ext import commands
import re

class WebSearch(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


def setup(bot):
	bot.add_cog(WebSearch(bot))
