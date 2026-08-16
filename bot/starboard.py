"""Core starboard logic: evaluate a reaction event and post/update pins."""

import discord
from . import db


def _emoji_str(emoji: discord.PartialEmoji | discord.Emoji | str) -> str:
    """Stable string key for an emoji. Custom emoji use their numeric ID."""
    if isinstance(emoji, str):
        return emoji
    if emoji.id:
        return str(emoji.id)
    return emoji.name


def _emoji_display(emoji: discord.PartialEmoji | discord.Emoji | str) -> str:
    """Human-readable emoji string suitable for Discord messages."""
    if isinstance(emoji, str):
        return emoji
    # Custom emoji: format as <:name:id> or <a:name:id>
    if emoji.id:
        animated = getattr(emoji, "animated", False)
        prefix = "a" if animated else ""
        return f"<{prefix}:{emoji.name}:{emoji.id}>"
    return emoji.name


def _pick_winning_emoji(
    message: discord.Message,
    ignored: set[str],
    current_winner: str | None,
) -> tuple[str, int]:
    """
    Return (winning_emoji_display, winning_count).

    Rules:
    - The emoji with the highest reaction count wins. Counts are never summed
      across emoji — each emoji is judged on its own count.
    - On a tie, the current stored winner (i.e. the one that broke the threshold
      first) is preferred — it keeps its position.
    - Ignored emoji are skipped entirely.
    """
    best_display: str | None = None
    best_count: int = 0

    for reaction in message.reactions:
        key = _emoji_str(reaction.emoji)
        if key in ignored:
            continue
        display = _emoji_display(reaction.emoji)
        count = reaction.count

        if count > best_count:
            best_count = count
            best_display = display
        elif count == best_count and display == current_winner:
            # Tie: keep the incumbent (first to break threshold)
            best_display = current_winner

    return (best_display or "⭐", best_count)


def _build_embed(
    message: discord.Message,
    winning_emoji: str,
    winning_count: int,
) -> discord.Embed:
    """
    Build the starboard embed matching the target style:

        **Author name**
        message content

        Message   Channel     Reaction
        [Link]    #channel    💯 (3)
    """
    # Avatar inline with name via set_author; message content as description
    embed = discord.Embed(
        description=message.content or None,
        color=discord.Color.dark_grey(),
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.display_avatar.url,
    )

    embed.add_field(name="Message", value=f"[Link]({message.jump_url})", inline=True)
    embed.add_field(name="Channel", value=f"#{message.channel.name}", inline=True)
    embed.add_field(name="Reaction", value=f"{winning_emoji}({winning_count})", inline=True)

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
    if _emoji_str(payload.emoji) in ignored_reactions:
        return

    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return
    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    threshold = config["threshold"]
    starboard_channel_id = config["starboard_channel_id"]

    starboard_channel = bot.get_channel(starboard_channel_id)
    if starboard_channel is None:
        return

    pin = await db.get_pin(pool, guild_id, message.id)

    if pin is not None:
        # Recalculate winning emoji, preserving the stored winner on ties.
        winning_emoji, winning_count = _pick_winning_emoji(
            message, ignored_reactions, pin["winning_emoji"]
        )
        # Persist if the winner changed (a different emoji now leads).
        if winning_emoji != pin["winning_emoji"]:
            await db.update_pin_winning_emoji(pool, guild_id, message.id, winning_emoji)

        try:
            sb_msg = await starboard_channel.fetch_message(pin["starboard_message_id"])
            await sb_msg.edit(
                embed=_build_embed(message, winning_emoji, winning_count)
            )
        except discord.NotFound:
            pass
        return

    # A message qualifies only when a *single* emoji reaches the threshold on its
    # own. Other reactions may be present, but their counts are not added in.
    # The emoji being added right now is treated as the initial winner so it wins
    # ties against emoji that reached the same count earlier.
    trigger_display = _emoji_display(payload.emoji)
    winning_emoji, winning_count = _pick_winning_emoji(
        message, ignored_reactions, trigger_display
    )

    if winning_count >= threshold:
        embed = _build_embed(message, winning_emoji, winning_count)
        sb_msg = await starboard_channel.send(embed=embed)
        await db.create_pin(
            pool,
            guild_id,
            message.id,
            channel.id,
            sb_msg.id,
            winning_emoji,
        )
