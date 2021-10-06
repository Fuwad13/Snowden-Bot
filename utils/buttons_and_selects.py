import discord
from discord import ui

class ConfirmOrCancel(ui.View):


	def __init__(self,*,timeout = 60):
		super().__init__(timeout=timeout)
		
		self.value = None
		

	async def interaction_check(self, intr):
		if not self.ctx.author == intr.user:
			await intr.response.send_message("Sorry, you can't interact to these buttons", ephemeral = True)

	@ui.button(label = 'Confirm', style = discord.ButtonStyle.green)
	async def confirm_button(self, button, interaction):
		
		await interaction.response.send_message("Confirming....", ephemeral = True)
		self.value = True
		self.stop()

	@ui.button(label = 'Cancel', style = discord.ButtonStyle.red)
	async def cancel_button(self, button, interaction):
		
		await interaction.response.send_message("Cancelling....", ephemeral = True)
		self.value = False
		self.stop()





