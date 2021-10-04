import discord
from discord.ext import commands
import re

class WebSearch(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'screesshot', aliases = ['ss', 'scr'], brief = 'Takes a screenshot of a website')
	@commands.guild_only()
	@commands.cooldown(1,10, commands.BucketType.user)
	async def screenshot(self, ctx, link):
		URL_REGEX = re.compile(
			r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

		if not re.fullmatch(URL_REGEX, link):
			return await ctx.send("Invalid URL! Make sure you put `https://` infront of it.")

		else:
			embed = discord.Embed(title=f"{link}")
			embed.set_image(
				url=f"https://api.popcat.xyz/screenshot?url={link}")
			await ctx.send(embed=embed)

	


def setup(bot):
	bot.add_cog(WebSearch(bot))
