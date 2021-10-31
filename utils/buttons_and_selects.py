import discord
from discord import ui

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


class HeadsOrTails(ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.value = None
		super().__init__(timeout = 15)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can choose from these buttons!", ephemeral = True)

		return intr.user == self.ctx.author

	@ui.button(emoji = '\U0001f1ed', label = 'Heads', style = discord.ButtonStyle.green)
	async def heads_button(self, button, intr):
		self.clear_items()
		self.value = True
		self.stop()

	@ui.button(emoji = '\U0001f1f9',label = 'Tails', style = discord.ButtonStyle.blurple)
	async def tails_buttton(self, button, intr):
		self.clear_items()
		self.value = False
		self.stop()

class InventoryEmbeds(ui.View):
	"""View buttons for inventory embeds"""
	def __init__(self, ctx, embed1, embed2):
		self.ctx = ctx
		self.embed1 = embed1
		self.embed2 = embed2
		super().__init__(timeout=120)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can use these buttons!", ephemeral = True)

		return intr.user == self.ctx.author

	@ui.button(emoji = '<:previous:904438065420959784>', style = discord.ButtonStyle.gray)
	async def _previous(self, button, intr):
		self._next.disabled = False
		button.disabled = True
		await intr.message.edit(embed= self.embed1, view = self)

	@ui.button(emoji = '<:next:904437983988563988>', style = discord.ButtonStyle.gray)
	async def _next(self, button, intr):
		self._previous.disabled = False
		button.disabled = True
		await intr.message.edit(embed= self.embed2, view = self)

	@ui.button(emoji = '<:stop:904438127530225724>', style = discord.ButtonStyle.gray)
	async def _stop(self, button, intr):
		self.stop()
		await intr.message.delete(silent = True)


	async def on_timeout(self):
		c = 0
		for item in self.children:
			self.remove_item(item)
			c+=1
			if c == 3:
				break
		await self.message.edit(view = self)
			
	




