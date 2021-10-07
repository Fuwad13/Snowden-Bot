import discord
from discord.ui import View, Button
import discord.ui
from discord import ui
from discord.ext import menus
from itertools import starmap, chain
import aiohttp

class ConfirmOrCancel(ui.View):


	def __init__(self, ctx ,*,timeout = 60):
		super().__init__(timeout=timeout)
		
		self.value = None
		self.ctx = ctx

	async def on_timeout(self):
		pass

		

	async def interaction_check(self, intr):
		if not self.ctx.author == intr.user:
			await intr.response.send_message("Sorry, you can't interact to these buttons", ephemeral = True)
		return self.ctx.author == intr.user

	@ui.button(label = 'Confirm', style = discord.ButtonStyle.green)
	async def confirm_button(self, button, interaction):
		
		
		self.value = True
		
		
		self.stop()

	@ui.button(label = 'Cancel', style = discord.ButtonStyle.red)
	async def cancel_button(self, button, interaction):
		
		
		self.value = False
		
		self.stop()



class MyMenuPages(ui.View, menus.MenuPages):
	def __init__(self, source, *, delete_message_after=False):
		super().__init__(timeout=120)
		self._source = source
		self.current_page = 0
		self.ctx = None
		self.message = None
		self.delete_message_after = delete_message_after
		

	async def start(self, ctx, *, channel=None, wait=False):
		# We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
		await self._source._prepare_once()
		self.ctx = ctx
		self.message = await self.send_initial_message(ctx, ctx.channel)

	async def _get_kwargs_from_page(self, page):
		"""This method calls ListPageSource.format_page class"""
		value = await super()._get_kwargs_from_page(page)
		if 'view' not in value:
			value.update({'view': self})
		return value

	async def interaction_check(self, interaction):
		"""Only allow the author that invoke the command to be able to use the interaction"""
		return interaction.user == self.ctx.author

	async def on_timeout(self):
		for i in self.children:
			i.disabled = True
		await self.message.edit(view = self)

	
	

	@ui.button(emoji='<:before_fast_check:754948796139569224>', style=discord.ButtonStyle.blurple)
	async def first_page(self, button, interaction):
		await self.show_page(0)

	@ui.button(emoji='<:before_check:754948796487565332>', style=discord.ButtonStyle.blurple)
	async def before_page(self, button, interaction):
		await self.show_checked_page(self.current_page - 1)

	@ui.button(emoji='<:stop_check:754948796365930517>', style=discord.ButtonStyle.blurple)
	async def stop_page(self, button, interaction):
		self.stop()
		if self.delete_message_after:
			await self.message.delete(delay=0)

	@ui.button(emoji='<:next_check:754948796361736213>', style=discord.ButtonStyle.blurple)
	async def next_page(self, button, interaction):
		await self.show_checked_page(self.current_page + 1)

	@ui.button(emoji='<:next_fast_check:754948796391227442>', style=discord.ButtonStyle.blurple)
	async def last_page(self, button, interaction):
		await self.show_page(self._source.get_max_pages() - 1)

	@ui.button(emoji = '<:download:316264057659326464>', style = discord.ButtonStyle.green)
	async def add_emoji(self, button, intr):
		confirm_view = ConfirmOrCancel(self.ctx, timeout = 15)

		if not intr.user.guild_permissions.manage_emojis:
				await intr.response.send_message("Sorry, you don't have enough permissions to add emojis in this server.", ephemeral = True)
		elif intr.user.guild_permissions.manage_emojis:
				await intr.response.send_message("**The selected emoji will be added to your server! Are you sure to add this emoji?**`(you have 15 seconds to choose)`", view = confirm_view)
				await confirm_view.wait()
				if confirm_view.value == True:

						await self.ctx.send("Adding the selected emoji!!")
						confirm_view.clear_items()
						await intr.edit_original_message(view = confirm_view)
						
						

				elif confirm_view.value == False:
						await self.ctx.send("Cancelling.....", delete_after = 5)
						confirm_view.clear_items()
						await intr.edit_original_message(view = confirm_view)
						
						

				elif confirm_view.value == None:
						await self.ctx.send("You took too long to response!! Cancelling...", delete_after = 5)
						confirm_view.clear_items()
						await intr.edit_original_message(view = confirm_view)
						


			



	


class EmojiLinkSource(menus.ListPageSource):
	def __init__(self, data):
		super().__init__(data, per_page=1)
		

	

	async def format_page(self, menu, entries):
		page = menu.current_page
		max_page = self.get_max_pages()
		starting_number = page * self.per_page + 1
		name = entries.split('#')[0]
		url = entries.split('#')[1]
		async with aiohttp.ClientSession() as ss:
		  async with ss.get(url) as ress:
			  r = ress

		n_url = r.url
		
		embed = discord.Embed(
			title=f"Search Results[{page + 1}/{max_page}]",
			description=f"{name}",
			color=0xffcccb
		)
		embed.set_image(url = n_url)
		author = menu.ctx.author
		# author.avatar in 2.0
		embed.set_footer(
			text=f"Requested by {author}", icon_url=author.avatar.url)
		return embed


