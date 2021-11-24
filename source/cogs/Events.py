import discord
from discord.ext import commands
import Helper
import asyncio


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
    # on bot ready all guild settings are read from
    # file into a dictionary in the Helper file
    '''

    @commands.Cog.listener()
    async def on_ready(self):
        await Helper.read_all_guild_settings_into_dict()
        print('ready')

    '''
    # sets up default values for guild
    # settings when the bot joins a guild
    '''

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await Helper.guild_setup(guild=guild)

    '''
    # if the bot is removed from the guild it
    # removes the guild settings from dictionary
    # and guildsettings.json file
    '''

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        Helper.delete_guild_settings(guild=guild)

    '''
    # when a message is pinned, checks if the pin limit
    # of the channel was reached and if it has been reached
    # the bot archives it
    '''

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        if Helper.get_guild_archive(channel.guild) and Helper.get_guild_archive(channel.guild) != channel.category:
            pins_list = await channel.pins()
            if len(pins_list) == 50:
                await channel.send("Archive time!")

                for i in range(3, 0, -1):
                    async with channel.typing():
                        await asyncio.sleep(1)
                        await channel.send(f"{i}...")

                async with channel.typing():
                    await Helper.archive_channel(channel)
                    await asyncio.sleep(.5)
                await channel.send("Archived!")

    '''
    # when a channel is deleted, checks whether that channel
    # was the archive category channel and if true,
    # mentions guild owner with warning and updates guild settings
    '''

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        event_audit_log = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
        user_that_deleted_channel = event_audit_log.user

        if channel.id == Helper.get_guild_archive_id(guild=channel.guild) and user_that_deleted_channel != self.client.user:
            channel_to_send_error = channel.guild.text_channels[0]
            await channel_to_send_error.send(
                f"{channel.guild.owner.mention} WARNING: THE ARCHIVE CATEGORY, '{channel.name}' FOR THIS SERVER HAS BEEN DELETED BY {user_that_deleted_channel.mention}!\n"
                f"FOR ME TO CONTINUE WORKING, I HAVE TO BE SET UP AGAIN!\n"
                f"USE {Helper.get_guild_prefix(channel.guild)}help TO SEE HOW TO SET ME UP AGAIN!")
            await Helper.set_guild_archive(channel.guild, None)

    @commands.Cog.listener()
    async def on_message(self, message):
        bot_id = f'<@!{self.client.user.id}>'
        if bot_id in message.content:
            await message.channel.send(f'**My command prefix for this server is: `{Helper.get_guild_prefix(message.guild)}`**')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return


def setup(client):
    client.add_cog(Events(client))
