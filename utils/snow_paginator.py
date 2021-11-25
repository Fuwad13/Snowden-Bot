import discord 
from discord import ui 


class BasePaginator(ui.View):

	def __init__(self,*, ctx, data , per_page : int = 5, ):
		...