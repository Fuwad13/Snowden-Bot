import discord
from discord.ext import commands
from typing import Union
from utils import buttons_and_selects as bs




class Information(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'ping', aliases = ['pong'], brief = "Shows bot's websocket latency in ms", help = "Shows bot's websocket latency in ms")
	async def ping(self, ctx):
		await ctx.send(f"PONG!! {round(self.bot.latency*1000)} ms", ephemeral = True)

	@commands.command(name='avatar', aliases=['av', 'pfp'], brief='Shows the avatar of an user(if possible)', help='Shows the avatar of an user(if possible)')
	async def avatar(self, ctx, *, user: Union[discord.Member, discord.User] = None):
		
		embed = discord.Embed()
		user = user or ctx.author
		avatar = user.display_avatar.with_static_format('png')
		embed.set_author(name=str(user), url=avatar)
		embed.set_image(url=avatar)
		await ctx.send(embed=embed)

	@commands.command(name = 'test')
	async def test(self, ctx):
		em = discord.Embed(title = 'Test')
		view = bs.ConfirmOrCancel(ctx,timeout=30)
		view.msg = await ctx.send(embed = em , view = view)
		await view.wait()
		view.clear_items()
		await view.msg.edit(view = view)
		if view.value == True:
			await ctx.send("confirmed")

		elif view.value == False:
			await ctx.send('cancelled')

		elif view.value == None:
			await ctx.send('Timed out')
			


def setup(bot):
	bot.add_cog(Information(bot))
	
