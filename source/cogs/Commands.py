import discord
from discord.ext import commands
import Helper
import asyncio


class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    '''
    # SET_PREFIX()
    # changes the guild specific prefix
    # to the given user input
    '''

    @commands.command()
    @commands.guild_only()
    async def set_prefix(self, ctx, *, prefix=None):
        if not ctx.message.author.bot:
            if ctx.message.author.guild_permissions.administrator:
                if prefix:
                    await Helper.set_guild_prefix(ctx.guild, prefix=prefix)
                    await ctx.channel.send(f"This server's command prefix has been changed to '{prefix}'")
                else:
                    await ctx.channel.send("You must enter the characters that you want me to change this server's command prefix to.\n"
                                           f"Eg) {Helper.get_guild_prefix(ctx.guild)}set_prefix ::")
            else:
                await ctx.channel.send('You do not have permissions to do that, only admins can change the command prefix')

    '''    
    # SET_ARCHIVE
    # changes the guild's archive category
    # to the user input if possible
    '''

    @commands.command()
    @commands.guild_only()
    async def set_archive(self, ctx, *, args=None):
        if not ctx.message.author.bot:
            if ctx.message.author.guild_permissions.administrator:
                if args:
                    archive_category = discord.utils.get(ctx.guild.categories, name=args)

                    if archive_category is not None:
                        if Helper.get_guild_archive(guild=ctx.guild) is None:
                            await Helper.set_guild_archive(guild=ctx.guild, archive=archive_category)
                            await ctx.channel.send(
                                f"The archive category has been set to '{archive_category.name}'.\n"
                                f"If this is not the category you intended, run \'{Helper.get_guild_prefix(ctx.guild)}change_archive command\' and enter the correct category")

                        else:
                            async with ctx.channel.typing():
                                await asyncio.sleep(1)
                                await Helper.move_archive_channels(archive_category)
                                await Helper.set_guild_archive(ctx.guild, archive_category)

                            await ctx.channel.send(f"Archive category has been set to '{archive_category.name}' and all archived channels have been moved there")

                    else:
                        await ctx.channel.send(f"The category: '{args}' doesnt seem to exist.\n"
                                               f"If you would like to me to make one for you, please run the {Helper.get_guild_prefix(ctx.guild)}create_archive command.\n"
                                               f"If you made a mistake, please run this command again and enter the right category")
                else:
                    await ctx.channel.send("You must enter the name of the category that you want me to change this server's archive to.\n"
                                           f"Eg){Helper.get_guild_prefix(ctx.guild)}set_archive The Archives")
            else:
                await ctx.channel.send("You do not have permissions to do that, only admins can setup the archive channel")

    '''
    # CREATE_ARCHIVE()
    # creates a category and sets it as
    # the guilds archive category
    '''

    @commands.command()
    @commands.guild_only()
    async def create_archive(self, ctx, *, args=None):
        if not ctx.message.author.bot:
            if ctx.message.author.guild_permissions.administrator:
                if args:
                    new_archive_category = await ctx.guild.create_category(name=args)

                    if Helper.get_guild_archive(guild=ctx.guild) is not None:

                        already_archived_category = Helper.get_guild_archive(guild=ctx.guild)
                        await ctx.channel.send(f"This server already has an archive category: '{already_archived_category.name}'\n"
                                               f"I have created an archive with the name '{new_archive_category.name}', and moved all archived channels from '{already_archived_category.name}'"
                                               f" there.")
                        await Helper.move_archive_channels(new_archive_category)
                        await Helper.set_guild_archive(ctx.guild, new_archive_category)

                    else:
                        await ctx.channel.send(f"Created an archive! The name is: '{args}'")
                        await Helper.set_guild_archive(ctx.guild, new_archive_category)
                else:
                    await ctx.channel.send("You must enter the name of the archive category that you want me to make.\n"
                                           f"Eg){Helper.get_guild_prefix(ctx.guild)}create_archive Archives")

            else:
                await ctx.channel.send("You do not have permissions to do that, only admins can create an archive category")

    '''
    # RENAME_ARCHIVE()
    # renames the archive category to user input
    '''

    @commands.command()
    @commands.guild_only()
    async def rename_archive(self, ctx, *, args):
        if Helper.get_guild_archive(guild=ctx.guild) is not None:
            if ctx.message.author.guild_permissions.administrator:
                if args:
                    archive_category = Helper.get_guild_archive(guild=ctx.guild)
                    archive_category_name = archive_category.name
                    await archive_category.edit(name=args)
                    await ctx.channel.send(f"The archive category name has been changed from '{archive_category_name}' to '{args}'")
                else:
                    await ctx.channel.send(
                        f"You must enter the new name you want to rename the archive category, '{Helper.get_guild_archive(ctx.guild).name}' to.\nEg){Helper.get_guild_prefix(ctx.guild)}rename_archive Archives")

        else:
            await ctx.channel.send(
                f"This server does not have an archive category to rename.\nPlease make an archive category with the command: '{Helper.get_guild_prefix(ctx.guild)}create_archive'"
                f"or set an already existing category as the archive category with the {Helper.get_guild_prefix(ctx.guild)}set_archive command")

    '''  
    # DELETE_ARCHIVE()
    # deletes the guild's archive category 
    # and all text channels under it
    '''

    @commands.command()
    @commands.guild_only()
    async def delete_archive(self, ctx):

        # method that takes the authors second message and compares it to a rewritten phrase to ensure that they want to delete the archive
        # returns true if the author's message passes the check, indicating they want to delete the archive
        # returns false otherwise
        def delete_archives_check(message):
            if message.author is message.guild.owner and message.content == "Yes, I want to delete all the archives of this server and understand that doing so is irreversible":
                return True
            else:
                return False

        if ctx.message.author is ctx.guild.owner:
            if Helper.get_guild_archive(ctx.guild) is not None:

                await ctx.channel.send("THIS ACTION IS CANNOT BE UNDONE!!! TO MAKE SURE YOU REALLY WANT TO DO THIS TYPE IN THE FOLLOWING PHRASE EXACTLY: "
                                       "Yes, I want to delete all the archives of this server and understand that doing so is irreversible")

                confirmed = await self.client.wait_for('message', check=delete_archives_check)

                if confirmed:
                    async with ctx.channel.typing():
                        await ctx.channel.send("...deleting... :(")
                        await Helper.delete_all_archived_channels(ctx.guild)
                        await asyncio.sleep(1)

                    try:
                        await ctx.channel.send("Archives have been deleted")
                    except discord.errors.NotFound:  # 404 Not Found (error code: 10003): Unknown Channel
                        await ctx.guild.text_channels[0].send("Archives have been deleted")

            else:
                await ctx.channel.send("There are no archives in this server")

        else:
            await ctx.channel.send("Only the server owner can activate this command.")

    '''
    # RETURN_ARCHIVE()
    # gives back the name of 
    # the guilds archive category
    '''

    @commands.command()
    @commands.guild_only()
    async def return_archive(self, ctx):
        if not ctx.message.author.bot:
            if Helper.get_guild_archive(ctx.guild) is not None:
                await ctx.channel.send(f"This servers archive category is '{Helper.get_guild_archive(ctx.guild).name}'")
            else:
                await ctx.channel.send("This server does not have an archive category")

    '''
    # ARCHIVE()
    # archives the channel 
    # in which the command is called
    '''

    @commands.command()
    @commands.guild_only()
    async def archive(self, ctx):
        if not ctx.message.author.bot:
            if ctx.message.author.guild_permissions.administrator:
                if Helper.get_guild_archive(ctx.guild):
                    try:
                        async with ctx.channel.typing():
                            await ctx.channel.send('Archiving...')
                            await Helper.archive_channel(ctx.channel)
                        await ctx.channel.send("Archived!")
                    except discord.errors.Forbidden:
                        await ctx.channel.send("I do not have permissions to archive this channel.")
                else:
                    await ctx.channel.send(f"There is no archive category for this server. Use {Helper.get_guild_prefix(ctx.guild)}help to see how to set one up.")

    @commands.command()
    @commands.guild_only()
    async def pins(self, ctx):
        '''
        Sends the number of pins in the channel the command was called in
        :param ctx:
        :return:
        '''
        if not ctx.message.author.bot:
            if ctx.message.author.guild_permissions.administrator:
                if Helper.get_guild_archive(ctx.guild):
                    num_pins = len(await ctx.channel.pins())
                    if num_pins == 1:
                        await ctx.channel.send(f'This channel has {num_pins} pin in it. There are {50 - num_pins} pins remaining until I archive this channel')
                    else:
                        await ctx.channel.send(f'This channel has {num_pins} pins in it. There are {50 - num_pins} pins remaining until I archive this channel')

    @commands.command()
    async def help(self, ctx):
        description = "Hey, I'm Clementine, your friendly server archiver.\n" \
                      "Whenever a text channel reaches its pin limit I will move into an archive category where it can live the rest of its days. Here are my commands!"
        title = 'Archive Bot Help'
        color = 0x372743

        embed = discord.Embed(
            colour=color,
            title=title,
            description=description
        )

        try:
            prefix = Helper.get_guild_prefix(ctx.guild)
        except AttributeError:
            prefix = '>>'

        embed.add_field(inline=False, name=f"{prefix}set_archive <category name>",
                        value="Creates a category with the given name where I will archive all channels\nOnly admins can use this")
        embed.add_field(inline=False, name=f"{prefix}create_archive <archive name>",
                        value="Creates a category with the given name where I will archive all channels\nOnly admins can use this")
        embed.add_field(inline=False, name=f"{prefix}rename_archive <new name>",
                        value="Renames the archive category to the given name\nOnly admins can use this")
        embed.add_field(inline=False, name=f"{prefix}return_archive",
                        value="Gives back the name of the archive category")
        embed.add_field(inline=False, name=f"{prefix}archive",
                        value="Archives the channel in which this command is called\nOnly admins can use this")
        embed.add_field(inline=False, name=f"{prefix}delete_archive",
                        value="Deletes all archived channels and the archive category\nOnly the server owner can use this\nTHIS IS NOT REVERSIBLE")
        embed.add_field(inline=False, name=f"{prefix}set_prefix <prefix>",
                        value="Change command prefix to whatever is inputted\nOnly admins can use this")
        embed.add_field(inline=False, name=f"{prefix}help",
                        value="Brings up this embed")
        embed.add_field(inline=False, name=f"{prefix}pins",
                        value="Returns the number of pinned messages in the channel")

        await ctx.channel.send(embed=embed)
        await ctx.channel.send(Helper.get_guild_archive(ctx.guild))

def setup(client):
    client.add_cog(Commands(client))
