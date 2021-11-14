import discord
import aiohttp
from discord.ext import commands
from discord.ext.commands import BucketType


class Miscellanous(commands.Cog):
	"""Miscellanous cog"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'tounix', aliases = ['2uinx', 'tu'], slash_command = False, help= "Get unix timestamp from datetime. Datetime example = 2020/11/25 12:56:54" )
	@commands.cooldown(1, 5, BucketType.user)
	async def _tounix(self, ctx, *, datetime : str):
		datetime = datetime.replace('-', '/')
		datetime = datetime.replace('.', '/')
		base_url = "https://showcase.api.linx.twenty57.net/UnixTime/tounixtimestamp?datetime="
		url = base_url+datetime
		async with self.bot.session.get(url) as resp:
			try:
				js = await resp.json()
				
			except Exception as e:
				raise commands.BadArgument(f"Invalid datetime given. Please provide a valid datetime, thanks.")
			else:
				err = js.get('Error')
				if err:
					return await ctx.send(f"**Error**: {err}")

				ts = js['UnixTimeStamp']
				await ctx.send(f"Unix timestamp : `{ts}`\n\n`<t:{ts}:t>` -> <t:{ts}:t>\n`<t:{ts}:T>` -> <t:{ts}:T>\n`<t:{ts}>` -> <t:{ts}>\n`<t:{ts}:F>` -> <t:{ts}:F>\n`<t:{ts}:d>` -> <t:{ts}:d>\n`<t:{ts}:D>` -> <t:{ts}:D>\n`<t:{ts}:R>` -> <t:{ts}:R>\n")

	

	


def setup(bot):
	bot.add_cog(Miscellanous(bot))
