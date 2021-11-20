import discord
from discord import mentions
from discord.ext import commands
from utils.emojis import EMOJIS

class Events(commands.Cog):
    """Events Listeners cog"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def on_bot_mention(self, message):
        if (message.guild is None) or (message.author.bot ):
            return

        if message.content.lower() == "<@862771284014530561>" or message.content.lower() == "<@!862771284014530561>":
            return await message.reply(f"My prefixes are : `s/`, `S/`\n`sd`, `Sd`, `SD`\n{self.bot.user.mention} ", mention_author = False)

    @commands.Cog.listener('on_guild_join')
    async def on_server_joins(self, guild):
        embed=  discord.Embed(title= f"{EMOJIS['greentick']}Joined a guild", color = discord.Color.blurple())
        embed.description = f"`Name :` {guild.name}\n`ID :` {guild.id}\n`Owner :` {guild.owner} - {guild.owner_id}\n`Members ` : {guild.member_count}\n`Icon url :` {str(guild.icon)}"
        embed.timestamp = guild.created_at
        embed.set_footer(text="Guild created ->")
        embed.set_image(url= str(guild.icon) or "https://cdn.discordapp.com/banners/336642139381301249/9b615fb84dbe8e5f4dd7b6ab167762cc.png?size=1024")
        channel = self.bot.get_channel(911675333927907348)
        await channel.send(f"{guild.id}", embed = embed)

    @commands.Cog.listener('on_guild_remove')
    async def on_server_removals(self, guild):
        embed=  discord.Embed(title= f"{EMOJIS['redtick']}Left a guild", color = discord.Color.red())
        embed.description = f"`Name :` {guild.name}\n`ID :` {guild.id}\n`Owner :` {guild.owner} - {guild.owner_id}\n`Members ` : {guild.member_count}\n`Icon url :` {str(guild.icon)}"
        embed.timestamp = guild.created_at
        embed.set_footer(text="Guild created ->")
        embed.set_image(url= str(guild.icon) or "https://cdn.discordapp.com/banners/336642139381301249/9b615fb84dbe8e5f4dd7b6ab167762cc.png?size=1024")
        channel = self.bot.get_channel(911675333927907348)
        await channel.send(f"{guild.id}", embed = embed)

        

def setup(bot):
    bot.add_cog(Events(bot))