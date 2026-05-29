"""Prefix commands for server admins to configure the starboard."""

import discord
from discord.ext import commands
from . import db


def _admin_check():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            return False
        perms = ctx.author.guild_permissions
        return perms.manage_channels and perms.manage_messages

    return commands.check(predicate)


class StarboardConfig(commands.Cog):
    def __init__(self, bot: commands.Bot, pool):
        self.bot = bot
        self.pool = pool

    @commands.command(name="set")
    @_admin_check()
    async def set_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the starboard channel. Pass a channel mention or ID."""
        await db.set_starboard_channel(self.pool, ctx.guild.id, channel.id)
        await ctx.send(f"Starboard channel set to {channel.mention}.")

    @commands.command(name="threshold")
    @_admin_check()
    async def set_threshold(self, ctx: commands.Context, number: int):
        """Set the minimum reaction count for a message to be pinned."""
        config = await db.get_config(self.pool, ctx.guild.id)
        if config is None:
            await ctx.send("No starboard configured yet. Run `|set #channel` first.")
            return
        if number < 1:
            await ctx.send("Threshold must be at least 1.")
            return
        await db.set_threshold(self.pool, ctx.guild.id, number)
        await ctx.send(f"Reaction threshold set to **{number}**.")

    @commands.command(name="ignore_channel")
    @_admin_check()
    async def ignore_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Prevent messages in a channel from ever being pinned. Pass a channel mention or ID."""
        await db.add_ignored_channel(self.pool, ctx.guild.id, channel.id)
        await ctx.send(f"{channel.mention} will now be ignored by the starboard.")

    @commands.command(name="add_channel")
    @_admin_check()
    async def add_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Re-enable starboard eligibility for a previously ignored channel. Pass a channel mention or ID."""
        await db.remove_ignored_channel(self.pool, ctx.guild.id, channel.id)
        await ctx.send(f"{channel.mention} is no longer ignored.")

    @commands.command(name="ignore_reaction")
    @_admin_check()
    async def ignore_reaction(self, ctx: commands.Context, emoji: str):
        """Prevent a specific emoji from counting toward the reaction threshold."""
        await db.add_ignored_reaction(self.pool, ctx.guild.id, emoji)
        await ctx.send(f"{emoji} will no longer count toward the starboard threshold.")

    @commands.command(name="add_reaction")
    @_admin_check()
    async def add_reaction(self, ctx: commands.Context, emoji: str):
        """Re-enable an emoji as a qualifying reaction."""
        await db.remove_ignored_reaction(self.pool, ctx.guild.id, emoji)
        await ctx.send(f"{emoji} will now count toward the starboard threshold.")

    @commands.command(name="status")
    @_admin_check()
    async def status(self, ctx: commands.Context):
        """Display the current starboard configuration for this server."""
        config = await db.get_config(self.pool, ctx.guild.id)
        if config is None:
            await ctx.send("No starboard configured yet. Run `|set #channel` to get started.")
            return

        starboard_ch = ctx.guild.get_channel(config["starboard_channel_id"])
        starboard_name = starboard_ch.mention if starboard_ch else f"<deleted channel {config['starboard_channel_id']}>"

        ignored_ch_ids = await db.get_ignored_channels(self.pool, ctx.guild.id)
        if ignored_ch_ids:
            ignored_ch_names = []
            for cid in ignored_ch_ids:
                ch = ctx.guild.get_channel(cid)
                ignored_ch_names.append(ch.mention if ch else f"<{cid}>")
            ch_value = ", ".join(ignored_ch_names)
        else:
            ch_value = "None"

        ignored_rxns = await db.get_ignored_reactions(self.pool, ctx.guild.id)
        rxn_value = ", ".join(ignored_rxns) if ignored_rxns else "None"

        embed = discord.Embed(title="Starboard Configuration", color=discord.Color.blurple())
        embed.add_field(name="Starboard Channel", value=starboard_name, inline=False)
        embed.add_field(name="Reaction Threshold", value=str(config["threshold"]), inline=False)
        embed.add_field(name="Ignored Channels", value=ch_value, inline=False)
        embed.add_field(name="Ignored Reactions", value=rxn_value, inline=False)
        await ctx.send(embed=embed)

    @set_channel.error
    @set_threshold.error
    @ignore_channel.error
    @add_channel.error
    @ignore_reaction.error
    @add_reaction.error
    @status.error
    async def command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You need Manage Channels and Manage Messages permissions to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: `{error.param.name}`.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Invalid argument: {error}")
        else:
            raise error
