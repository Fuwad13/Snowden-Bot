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

	
		




