from discord.utils import get
import json

standard_prefix = '>>'
guild_settings = {}

archive_key = "Archive Category"
prefix_key = "Prefix"

'''
# replaces the given channel with a clone 
# while renaming and the channel in the archive naming scheme
# and moving it into the appropriate place
# under the archive category
'''
async def archive_channel(channel):
    global guild_settings

    archive_category = get(channel.guild.categories, id=guild_settings.get(str(channel.guild.id)).get(archive_key))
    archived_channels = archive_category.channels
    same_archived_channels = []

    for archived_channel in archived_channels:
        if channel.name in archived_channel.name:
            same_archived_channels.append(archived_channel)

    '''
    Refactor
    '''
    if same_archived_channels:
        previous_archived_channel = same_archived_channels[-1]
        if previous_archived_channel.name[-1].isdigit():
            archive_number = int(previous_archived_channel.name[-1]) + 1
        else:
            archive_number = 1
        position = previous_archived_channel.position + 1
    else:
        archive_number = 1
        position = len(archived_channels)

    new_channel = await channel.clone()
    channel_original_position = channel.position
    new_name = channel.name + '-archive-' + str(archive_number)
    await new_channel.edit(position=channel_original_position)
    await channel.edit(name=new_name, category=archive_category, position=position)


'''
# moves all archive channels under 
# the archive category to the given category
'''
async def move_archive_channels(new_category):
    archive_category = get_guild_archive(new_category.guild)
    channels = archive_category.channels
    for channel in channels:
        await channel.edit(category=new_category)


'''
# deletes all archived text channels and the archived category
# and calls function to remove the guild from the settings json file
'''
async def delete_all_archived_channels(guild):
    archive_category = get_guild_archive(guild)
    archived_channels = archive_category.channels
    for channel in archived_channels:
        await channel.delete()
    await archive_category.delete()

    await set_guild_archive(guild)
    await save_guild_settings_to_file(guild)


'''
# returns the prefix for the guild in which
# a command was called
'''
def get_prefix(client, message):
    try:
        return get_guild_prefix(message.guild)

    except KeyError:  # if the guild's prefix cannot be found in 'guild_settings.json'
        set_guild_prefix(message.guild)
        return get_guild_prefix(message.guild)

    except:  # I added this when I started getting dm error messages
        return '//'  # This will return "." as a prefix. You can change it to any default prefix.


'''
# returns the archive category as a CategoryChannel object
'''
def get_guild_archive(guild):
    archive_id = guild_settings.get(str(guild.id)).get(archive_key)
    return get(guild.categories, id=archive_id)


'''
# returns the ID of archive category as an integer
'''
def get_guild_archive_id(guild):
    return guild_settings.get(str(guild.id)).get(archive_key)


'''
# returns the guild's command prefix
'''
def get_guild_prefix(guild):
    return guild_settings.get(str(guild.id)).get(prefix_key)


'''
# sets the archive category setting of the given guild 
# to the given Category object. If no such object is passed, 
# the Category is set to None
'''
async def set_guild_archive(guild, archive=None):
    global guild_settings
    if archive is not None:
        guild_settings.get(str(guild.id))[archive_key] = archive.id
    else:
        guild_settings.get(str(guild.id))[archive_key] = None
    await save_guild_settings_to_file(guild)


'''
# sets the prefix setting of the given guild 
# to the given string. If no string is passed, 
# prefix is set to the standard prefix
'''
async def set_guild_prefix(guild, prefix: str = standard_prefix):
    global guild_settings
    guild_settings.get(str(guild.id))[prefix_key] = prefix
    await save_guild_settings_to_file(guild)


'''
# sets initial values for a guilds archive category
# and prefix. To be called on joining of a guild
'''
async def guild_setup(guild):
    guild_settings[str(guild.id)] = {archive_key: None, prefix_key: standard_prefix}
    await save_guild_settings_to_file(guild)


'''
# saves the current settings within the dict
# # guild_settings to guildsettings.json
'''
async def save_guild_settings_to_file(guild):
    with open('guildsettings.json', 'r') as f:
        settings = json.load(f)
        f.close()

    settings[str(guild.id)] = guild_settings[str(guild.id)]

    with open('guildsettings.json', 'w') as f:
        json.dump(settings, f)
        f.close()


'''
# reads from guild_settings file and stores the guild_settings dict
'''
async def read_all_guild_settings_into_dict():
    global guild_settings

    with open("guildsettings.json", 'r') as file:
        guild_settings = json.load(file)
    print(guild_settings)


'''
# deletes the given guild and its settings 
# from guild_settings.json and the guild_settings dict
'''
def delete_guild_settings(guild):
    global guild_settings

    with open('guildsettings.json', 'r') as f:
        settings = json.load(f)
        f.close()

    settings.pop(str(guild.id))
    guild_settings = settings

    with open('guildsettings.json', 'w') as f:
        json.dump(settings, f)
        f.close()


'''
# retrieves bot token from RUN_TOKEN and returns it
'''
def get_token():
    token_file = open("RUN_TOKEN", "r")
    token = token_file.readline()
    return token
