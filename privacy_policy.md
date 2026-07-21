# Privacy Policy for Better Starboard
**Effective Date:** 2026-07-21
**Last Updated:** 2026-07-21

Better Starboard ("the Bot") is a Discord bot that helps server communities highlight popular messages by automatically posting them to a configured starboard channel once they reach a configured reaction threshold. This Privacy Policy explains what data the Bot processes, how it is used, and what choices server administrators and users have.

---

1. What data the Bot processes
The Bot processes information that Discord makes available through its API in order to provide its core features. This may include:

- Server and channel identifiers, such as Discord guild IDs and channel IDs.
- Message identifiers and message metadata needed to link an original message to its starboard post.
- Reaction events and counts, which are used to determine whether a message should be posted or updated on the starboard.
- Configuration data for each server, including the selected starboard channel, reaction threshold, and ignored channels or ignored emoji.
- Message content and author display information when a message is posted to the starboard embed. This is used to create the visible starboard entry in Discord, but it is not stored in the Bot's database as a long-term record.

---

2. What data is stored
The Bot stores limited server-level and message-linking data in a PostgreSQL database configured by the host operator. The stored data includes:

- Server configuration records, such as the starboard channel and threshold.
- Pin records that link an original message to its starboard post, including message IDs and the winning emoji used for the display.
- Lists of ignored channels and ignored reactions for each server.

The Bot does not store full private messages, direct messages, or unrelated user content. It also does not retain reaction data beyond what is needed to evaluate and update the starboard in real time.

---

3. How the data is used
The Bot uses this information to:

- Detect reactions on messages in Discord.
- Apply per-server rules such as ignored channels and ignored reactions.
- Determine whether a message should be posted to the starboard.
- Prevent duplicate postings by tracking which messages have already been pinned.
- Update the starboard entry as reactions change.

---

4. Data storage and security
The Bot's data is stored in the database configured by the person or organization hosting it. The hosting operator controls the database location, access controls, backups, and retention practices. The Bot itself does not transmit server configuration or pin records to third-party services beyond normal Discord API operations.

---

5. Data sharing and disclosure
Better Starboard does not sell or share personal data for advertising or unrelated purposes. The Bot may disclose information only when required by law, legal process, or to protect the security and integrity of the service.

---

6. User and administrator controls
Server administrators can manage the Bot's behavior through server commands, including selecting a starboard channel, changing the threshold, and configuring ignored channels or emoji. If a server administrator removes the Bot from a server, the Bot will stop processing new events for that server. If you want data associated with your server removed, please contact the maintainer or host operator responsible for the deployment.

---

7. Changes to this policy
This Privacy Policy may be updated from time to time to reflect changes in functionality or lawful requirements. The latest version will be reflected in this document.

---

8. Contact
If you have questions about this Privacy Policy or would like to request data-related assistance, please contact the maintainer through the Better Starboard project repository.