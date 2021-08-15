from backend import DiscordDatabase
from datetime import datetime

check_emoji = '✅'
x_emoji = '❌'
bot_id = 815105045842493442
blue_bird_id = 622655798794911760
kou_id = 498374117561597972
owner_id = 799843363058221076
the_council_id = [owner_id, blue_bird_id]
oasis_guild_id = 811395891122012180
welcome_channel_id = 811395892338622504
welcome_message_id = 814157339950841876

admin_role_id = 814154599833272320
based_zeus_role_id = 830787685181554699
mod_role_id = 814153584526098542
member_role_id = 814154234433634316
dj_role_id = 815442370132049931
unknown_role_id = 814155609158713414
all_roles = [admin_role_id, based_zeus_role_id, mod_role_id, dj_role_id, member_role_id]
database = DiscordDatabase()


def welcome_message(member):
    return f"**TL;DR Click :white_check_mark: in welcome channel.**\nGreetings {member.name}, I welcome you to the " \
           f"{member.guild.name} server! :gem:\nRead and understand the rules in the welcome channel and react " \
           f":white_check_mark: if you agree.\n\nInvite your friends to the {member.guild.name} server!\nUse the " \
           f"link: https://discord.gg/XgATq33NGp :mailbox_with_mail:"


def emoji_convert(emoji_str_int):
    emoji_str_int = emoji_str_int[0] if len(emoji_str_int) > 1 else emoji_str_int
    return ord(emoji_str_int) if type(emoji_str_int) == str else chr(emoji_str_int)


def timestamp_convert(datetime_float_obj):
    return datetime.fromtimestamp(datetime_float_obj) if type(datetime_float_obj) == float else datetime_float_obj.timestamp()


def snowflake_to_timestamp(snowflake):
    # right shift snowflake by 22 the same as snowflake / (2**22) but not recommended because it's slower
    # divided by 1000 because this timestamp is in seconds converting it to ms
    return float(((snowflake >> 22) + 1420070400000) / 1000)


def get_member(bot, memberNameID):
    oasis_guild = bot.get_guild(oasis_guild_id)
    try:
        member = oasis_guild.get_member(int(memberNameID))
    except ValueError:
        member = oasis_guild.get_member_named(memberNameID)
    if not member:
        return False
    return member


# def member_upgrade(member, memberName):
#     database = DiscordDatabase()
#     member.memberName = memberName
#     member.dateJoined = database.get([('memberID', member.id), ('dateJoined', None)])
#     return member
