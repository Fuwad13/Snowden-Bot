import discord 
from discord import ui 


class BaseView(ui.View):

	def __init__(self, ctx):
		super().__init__()
		self.ctx = ctx
		

class BasePaginator(BaseView):

	def __init__(self, ctx):
		super().__init__(ctx)