import asyncio
import discord
from discord.ext import commands
from typing import Union
from utils import buttons_and_selects as bs




class Information(commands.Cog):
	"""Information cog"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'ping', aliases = ['pong'], brief = "Shows bot's websocket latency in ms", help = "Shows bot's websocket latency in ms", slash_command = False)
	async def ping(self, ctx):
		await ctx.send(f"`PONG!!` {round(self.bot.latency*1000)} ms", ephemeral = True)

	@commands.command(name= 'invite', help = "Invite me to your servers, Thanks!", slash_command = False)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def _invite_cmd(self, ctx):
		await ctx.send("https://discord.com/api/oauth2/authorize?client_id=862771284014530561&permissions=2134207679&scope=bot%20applications.commands")

	@commands.command(name='avatar', aliases=['av', 'pfp'], brief='Shows the avatar of an user(if possible)', help='Shows the avatar of an user(if possible)')
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def avatar(self, ctx , *, user: Union[discord.Member, discord.User] = None):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		
		embed = discord.Embed()
		user = user or ctx.author
		avatar = user.display_avatar.with_static_format('png')
		embed.set_author(name=str(user), url=avatar)
		embed.set_image(url=avatar)
		await ctx.send(embed=embed)

	


async def setup(bot):
	await bot.add_cog(Information(bot))
	
