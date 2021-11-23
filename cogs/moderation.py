import time
import re
import typing
from discord.ext.commands.core import check
from discord.ext.commands.errors import NoPrivateMessage
import humanize
import discord
from discord.ext import commands
from utils.emojis import EMOJIS

class Moderation(commands.Cog):
    """Cog for moderation"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise NoPrivateMessage("This command can run only in a guild channel.")
        else:
            return True


    @commands.command(name='slowmode', aliases =['sm'], help="Set the slowmode for a TextChannel.")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels = True)
    async def slowmode(self, ctx, seconds : int = 0):
        channel = ctx.channel
        if seconds > 21600:
            return await ctx.send("Maximum amount of slowmode delay is `6 hours` or `21600 seconds`", delete_after=10)
        await channel.edit(slowmode_delay=seconds, reason=f"responsible user - {ctx.author}")
        return await ctx.send(f"{EMOJIS['greentick']} Set the slowmode to **{humanize.precisedelta(seconds)}**")

    @commands.group(name= "purge", aliases = ['cleanup'], help= "Bulk delete messages of a channel, specify the amount of messages to be deleted `(default 5)`", invoke_without_command = True, slash_command = False)
    @commands.has_permissions(manage_messages= True)
    @commands.bot_has_permissions(manage_messages= True)
    async def _purge(self, ctx, amount : int = 5):
        if amount > 1000:
            return await ctx.send("**Can't delete more than 1000 messages at once!**")
        def is_deleteable(message):
            return (time.time() - message.created_at.timestamp()) < 1209600
        deleted = await ctx.channel.purge(limit= amount, before = ctx.message.created_at, check = is_deleteable)
        await ctx.send(f"**Deleted {len(deleted)} message(s)**" , delete_after = 5)

    @_purge.command(name= "links", aliases = ['link', 'url'], help = "Bulk delete messages that contains links/url.", slash_command = False)
    @commands.has_permissions(manage_messages= True)
    @commands.bot_has_permissions(manage_messages = True)
    async def _links(self, ctx, amount : int = 5):
        if amount > 1000:
            return await ctx.send("**Can't delete more than 1000 messages at once!**")

        url_reg = re.compile(r'https?://(?:www\.)?.+')
        def is_link(message):
            if not (time.time() - message.created_at.timestamp()) < 1209600:
                return False
            if len(message.content) == 0:
                return False
            search = re.search(url_reg, message.content)
            if not search:
                return False
            else:
                return True
            
        deleted = await ctx.channel.purge(limit= amount, before = ctx.message.created_at, check = is_link)
        await ctx.send(f"**Deleted {len(deleted)} message(s) containing links/url**" , delete_after = 5)

    @_purge.command(name= "files", aliases = ['file', 'attachments'], help = "Bulk delete messages that contains files/attachments.", slash_command = False)
    @commands.has_permissions(manage_messages= True)
    @commands.bot_has_permissions(manage_messages = True)
    async def _files(self, ctx, amount : int = 5):
        if amount > 1000:
            return await ctx.send("**Can't delete more than 1000 messages at once!**")

        
        def is_file(message):
            if not (time.time() - message.created_at.timestamp()) < 1209600:
                return False
            if len(message.attachments) == 0:
                return False
            else:
                return True

            
        deleted = await ctx.channel.purge(limit= amount, before = ctx.message.created_at, check = is_file)
        await ctx.send(f"**Deleted {len(deleted)} message(s) containing files/attachments**" , delete_after = 5)

    @_purge.command(name= "embeds", aliases = ['embed'], help = "Bulk delete messages that contains embeds.", slash_command = False)
    @commands.has_permissions(manage_messages= True)
    @commands.bot_has_permissions(manage_messages = True)
    async def _embeds(self, ctx, amount : int = 5):
        if amount > 1000:
            return await ctx.send("**Can't delete more than 1000 messages at once!**")

        
        def is_embed(message):
            if not (time.time() - message.created_at.timestamp()) < 1209600:
                return False
            if len(message.embeds) == 0:
                return False
            else: 
                return True
        deleted = await ctx.channel.purge(limit= amount, before = ctx.message.created_at, check = is_embed)
        await ctx.send(f"**Deleted {len(deleted)} message(s) containing embeds**" , delete_after = 5)

    @commands.command(name= 'kick', brief = "Kick a member for breaking rules or being annoying.", help = "Kick a member from your server for breaking rules or being an annoying person.")
    @commands.has_permissions(kick_members = True)
    @commands.bot_has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member, *, reason : str = None):
        if member == ctx.author:
            return await ctx.send(f"{EMOJIS['redtick']}You can't kick yourself.", ephemeral = True)
        if (ctx.me.top_role <= member.top_role) or member.id == ctx.guild.owner_id :
            return await ctx.send(f"{EMOJIS['redtick']}Can't kick that member as they are in a higher role position than me.", ephemeral = True)
        perms = member.guild_permissions
        if perms.administrator or perms.manage_guild or perms.ban_members or perms.kick_members or perms.manage_channels:
            return await ctx.send(f"{EMOJIS['redtick']}Can't kick that member as they have mod/admin perms.", ephemeral = True)
        if not reason:
            reason = "No reason provided"
        reason = reason[:450:] + f"\nResponsible Moderator: {ctx.author} - "
        try:
            await member.send(f"You have been kicked from {ctx.guild.name}\n {reason}")

        except:
            pass
        await member.kick(reason= reason)

        embed = discord.Embed(title= f"{EMOJIS['greentick']} {member} has been kicked || reason : {reason[:180:]}...")
        await ctx.send(embed = embed)
    
    # @commands.command(name= 'ban', brief = "Ban a member/user for breaking rules or being annoying.", help = "Ban a member from your server for breaking rules or being an annoying person.")
    # @commands.has_permissions(ban_members = True)
    # @commands.bot_has_permissions(ban_members = True)
    # async def ban(self, ctx, member : discord.User, *, reason : str = None):
    #     if member == ctx.author:
    #         return await ctx.send(f"{EMOJIS['redtick']}You can't kick yourself.", ephemeral = True)
    #     if (ctx.me.top_role <= member.top_role) or member.id == ctx.guild.owner_id :
    #         return await ctx.send(f"{EMOJIS['redtick']}Can't kick that member as they are in a higher role position than me.", ephemeral = True)
    #     perms = member.guild_permissions
    #     if perms.administrator or perms.manage_guild or perms.ban_members or perms.kick_members or perms.manage_channels:
    #         return await ctx.send(f"{EMOJIS['redtick']}Can't kick that member as they have mod/admin perms.", ephemeral = True)
    #     if not reason:
    #         reason = "No reason provided"
    #     reason = reason[:450:] + f"\nResponsible Moderator: {ctx.author} - "
    #     try:
    #         await member.send(f"You have been kicked from {ctx.guild.name}\n {reason}")

    #     except:
    #         pass
    #     await member.kick(reason= reason)

    #     embed = discord.Embed(title= f"{EMOJIS['greentick']} {member} has been kicked || reason : {reason[:180:]}...")
    #     await ctx.send(embed = embed)

    @commands.group(name= 'lock', aliases = ['lockdown'], brief = "Disable `Send messages` permission for everyone.", help = "Disable `Send messages` permission for everyone for a channel.Specify a time to unlock the channel for everyone.", slash_command = False, invoke_without_command = True)
    @commands.has_permissions(manage_channels = True, manage_permissions = True)
    @commands.bot_has_permissions(manage_channels = True,manage_permissions = True)
    async def lock(self, ctx):
        channel = ctx.channel
        overwrites = channel.overwrites
        ev_ov = overwrites.get(ctx.guild.default_role)
        if not ev_ov:
            await channel.set_permissions(ctx.guild.default_role, send_messages = False)
            return await ctx.send(f"{EMOJIS['greentick']}Locked {channel.mention}")
        if ev_ov.send_messages == False:
            return await ctx.send(f"{channel.mention} is already locked for everyone!", delete_after = 10)
        overwrites[ctx.guild.default_role].send_messages = False  
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrites[ctx.guild.default_role])
        await ctx.send(f"{EMOJIS['greentick']}Locked {channel.mention}")

    @commands.command(name= 'unlock', aliases = ['unlockdown'], brief = "Enable `Send messages` permission for everyone.", help = "Enable `Send messages` permission for everyone for a channel.", slash_command = False)
    @commands.has_permissions(manage_channels = True, manage_permissions = True)
    @commands.bot_has_permissions(manage_channels = True,manage_permissions = True)
    async def unlock(self, ctx):
        channel = ctx.channel
        overwrites = channel.overwrites
        ev_ov = overwrites.get(ctx.guild.default_role)
        if not ev_ov:
            await channel.set_permissions(ctx.guild.default_role, send_messages = True)
            return await ctx.send(f"{EMOJIS['greentick']}Unlocked {channel.mention}")
        if ev_ov.send_messages == True:
            return await ctx.send(f"{channel.mention} is already unlocked for everyone!", delete_after = 10)
        overwrites[ctx.guild.default_role].send_messages = True 
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrites[ctx.guild.default_role])
        await ctx.send(f"{EMOJIS['greentick']}Unlocked {channel.mention}")

def setup(bot):
    bot.add_cog(Moderation(bot))
