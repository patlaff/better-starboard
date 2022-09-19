# better-starboard

If you're anything like me and my friends, you use reactions extremely unpredictably in your Discord server.  The problem with most (if not, all) starboards available is that they require the user to specify a particular (or in some cases, a small array) of reactions/emojis to use for pinning popular messages to the starboard.  

Better-Starboard takes the opposite approach. This bot will pin any message that gets *any* reaction over a set threshold to the starboard, allowing for what we believe is a more dynamic memory-maker. Configuration, detailed below, also allows users to ignore certain reactions/emojis and channels in their Discord server.

## Installation

[Install Using This Link](https://discord.com/api/oauth2/authorize?client_id=1008147831443427379&permissions=8&scope=bot)

Note that the bot currently requires administrator rights. I will pull in these permissions in a future release.

## Usage

### Discord Permissions
All commands require a user in a discord server to have "Manage Channels" and "Manage Messages" permissions due to the fact that better-starboard works on a blacklist approach, so will have access to all messages in all channels by default, meaning the command user should also have these privileges.

### Command Prefix
This bot uses the pipe character ( | ) as the prefix for all commands. This is not customizable at this time, but please submit an issue if this is a requested feature.

### Commands
The following commands are currently supported, the description for each was pulled from the bot's |help command:
| Command           | Usage                           | Description                                                                                                                                           | Example                          |
|-------------------|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|
| \|set             | \|set <channel_name>            | Use this command to set the starboard channel for the server.                                                                                         | \|set starboard-channel          |
| \|threshold       | \|threshold <int>               | Use this command to set the reaction threshold for posting messages to the starboard. Default is 5.                                                   | \|threshold 10                   |
| \|status          | \|status                        | Use this command to view this server's current configuration status, including starboard channel, threshold, ignored channels, and ignored reactions. | \|status                         |
| \|ignore_reaction | \|ignore_reaction <emoji>       | Use this command to set reaction exceptions.                                                                                                          | \|ignore_reaction ❌              |
| \|add_reaction    | \|add_reaction <emoji>          | Use this command to remove a reaction exception.                                                                                                      | \|add_reaction ✅                 |
| \|ignore_channel  | \|ignore_channel <channel_name> | Use this command to add a channel exception.                                                                                                          | \|ignore_channel private_channel |
| \|add_channel     | \|add_channel <channel_name>    | Use this command to remove a reaction exception.                                                                                                      | \|add_channel public_channel     |


## Contribution

Feel free to submit issues and pull requests here.