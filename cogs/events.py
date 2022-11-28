import discord
import aiohttp
from discord import mentions
from discord import channel
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

    @commands.Cog.listener('on_member_join')
    async def on_emote_island_join(self, member):
        if not member.guild.id == 874735250842984458:
            return
        channel = self.bot.get_channel(874737401807917117)
        await channel.send(f"{member.mention}, Welcome to **Emoji Tools** Support Server.")
    
    @commands.Cog.listener('on_command')
    async def on_command_runs_log(self, ctx):
        message = f"**Command Used**\ncommand -> {ctx.command.qualified_name}\nby -> {ctx.author} - {ctx.author.mention} - {ctx.author.id}\nin -> {ctx.channel.mention} - {ctx.channel.id}\nserver -> {ctx.guild.name} - {ctx.guild.id}\nserver owner -> {ctx.guild.owner_id}"
        channel = self.bot.get_channel(911925727140655134)
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url= "https://discord.com/api/webhooks/911927283932082206/KWoFRcttqpkOKAvR7RuCtziMekjR3b-pvSeFnODPRWUdy8MjvFsQUKd4m1Fl5_QWNJ2d", session = session)
            await webhook.send(message, allowed_mentions= discord.AllowedMentions.none())
            
    @commands.Cog.listener('on_member_ban')
    async def on_dpy_member_ban(self, guild : discord.Guild,member):
        if not guild.id == 336642139381301249:
            return
        embed = discord.Embed(color = discord.Color.red(), title = "A member has been banned.")
        embed.description = f"Banned user : {member} | {member.mention}\nID : {member.id}"
        channel = guild.get_channel(381963689470984203)
        msg = await channel.send(embed= embed)
        async for e in guild.audit_logs(limit=3,action=discord.AuditLogAction.ban):
            if e.target.id == member.id:
                embed.description+=f"\nModerator: {e.user.mention}\nReason: {e.reason}"
                await msg.edit(embed = embed)
                await msg.add_reaction("\U0001f1eb")
                break




        

async def setup(bot):
    await bot.add_cog(Events(bot))