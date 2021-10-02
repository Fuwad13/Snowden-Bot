import discord
from discord.ext import commands


class Helpful(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'snowflake', aliases = ["sf", "sfl", "sflake"], brief = "Shows the snowflake creation time!", help = "This command gives you the discord snowflake creation time in a timestamp format.")
	async def snow_flake(self, ctx, snowflake_id: discord.abc.Snowflake):
		time = int(discord.utils.snowflake_time(snowflake_id).timestamp())
		await ctx.send(f"<t:{time}:F>")

	


def setup(bot):
	bot.add_cog(Helpful(bot))
