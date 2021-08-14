from backend import DiscordDatabase
from datetime import datetime

check_emoji = '✅'
x_emoji = '❌'
blue_bird_id = 622655798794911760
kou_id = 498374117561597972
owner_id = 799843363058221076
the_council_id = [owner_id, blue_bird_id]
oasis_guild_id = 811395891122012180
welcome_channel_id = 811395892338622504
welcome_message_id = 814157339950841876
audit_log = 'Because of bot'

admin_role_id = 814154599833272320
mod_role_id = 814153584526098542
unknown_role_id = 814155609158713414
dj_role_id = 815442370132049931
muted_role_id = 814155609158713414
dj_roles = [555926027839471626]
database = DiscordDatabase()


def welcome_message(member):
    return f"Greetings {member.name}, I welcome you to {member.guild.name} server! :reminder_ribbon:\n A start of a " \
           f"splendid epoch. :gem: To begin your journey;\n:one: Kindly use the `~verify 'put your real name here'` command and input " \
           f"your real name. First and/or last name, this is to help the server owner identify who you are.\n:two: Read " \
           f"and understand the rules in the welcome channel and react :white_check_mark: if you agree.\n\n**TL;DR Type " \
           f"`~verify 'put your real name here'` then click check in welcome.**\n\nInvite your friends to the " \
           f"{member.guild.name} server!\nUse the link: https://discord.gg/XgATq33NGp :mailbox_with_mail:\n" \
           f"*You may contact the server owner <@799843363058221076>, if you do not wish to share your personal information.*" \
           f"\n*The server owner will not, in any circumstances, share your personal information with other individuals " \
           f"or organizations.*"


def emoji_convert(emoji_str_int):
    emoji_str_int = emoji_str_int[0] if len(emoji_str_int) > 1 else emoji_str_int
    return ord(emoji_str_int) if type(emoji_str_int) == str else chr(emoji_str_int)


def timestamp_convert(datetime_float_obj):
    return datetime.fromtimestamp(datetime_float_obj) if type(datetime_float_obj) == float else datetime_float_obj.timestamp()


def snowflake_to_timestamp(snowflake):
    # right shift snowflake by 22 the same as snowflake / (2**22) but not recommended because it's slower
    # divided by 1000 because this timestamp is in seconds converting it to ms
    return float(((snowflake >> 22) + 1420070400000) / 1000)


def member_upgrade(member, memberName):
    database = DiscordDatabase()
    member.memberName = memberName
    member.dateJoined = database.get([('memberID', member.id), ('dateJoined', None)])
    return member
