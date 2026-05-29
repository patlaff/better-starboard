"""Core starboard logic: evaluate a reaction event and post/update pins."""

import discord
from . import db


def _emoji_str(emoji: discord.PartialEmoji | discord.Emoji | str) -> str:
    if isinstance(emoji, str):
        return emoji
    if emoji.id:
        return str(emoji.id)
    return emoji.name


def _count_reactions(message: discord.Message, ignored: set[str]) -> int:
    total = 0
    for reaction in message.reactions:
        key = _emoji_str(reaction.emoji)
        if key not in ignored:
            total += reaction.count
    return total


def _build_embed(message: discord.Message, reaction_count: int) -> discord.Embed:
    embed = discord.Embed(
        description=message.content or None,
        color=discord.Color.gold(),
        timestamp=message.created_at,
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.display_avatar.url,
    )
    embed.add_field(name="Source", value=f"[Jump to message]({message.jump_url})", inline=False)
    embed.set_footer(text=f"{reaction_count} reactions · #{message.channel.name}")

    if message.attachments:
        first = message.attachments[0]
        if first.content_type and first.content_type.startswith("image/"):
            embed.set_image(url=first.url)

    return embed


async def handle_reaction(
    pool,
    payload: discord.RawReactionActionEvent,
    bot: discord.Client,
):
    guild_id = payload.guild_id
    if guild_id is None:
        return

    config = await db.get_config(pool, guild_id)
    if config is None:
        return

    ignored_channels = set(await db.get_ignored_channels(pool, guild_id))
    if payload.channel_id in ignored_channels:
        return

    ignored_reactions = set(await db.get_ignored_reactions(pool, guild_id))
    added_emoji_key = _emoji_str(payload.emoji)
    if added_emoji_key in ignored_reactions:
        return

    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return
    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    reaction_count = _count_reactions(message, ignored_reactions)
    threshold = config["threshold"]
    starboard_channel_id = config["starboard_channel_id"]

    starboard_channel = bot.get_channel(starboard_channel_id)
    if starboard_channel is None:
        return

    pin = await db.get_pin(pool, guild_id, message.id)

    if pin is not None:
        try:
            sb_msg = await starboard_channel.fetch_message(pin["starboard_message_id"])
            await sb_msg.edit(embed=_build_embed(message, reaction_count))
        except discord.NotFound:
            pass
        return

    if reaction_count >= threshold:
        embed = _build_embed(message, reaction_count)
        sb_msg = await starboard_channel.send(embed=embed)
        await db.create_pin(pool, guild_id, message.id, channel.id, sb_msg.id)
