from backend import DiscordDatabase
from datetime import datetime

check_emoji = '✅'
x_emoji = '❌'
bot_id = 815105045842493442
blue_bird_id = 622655798794911760
kou_id = 498374117561597972
owner_id = 799843363058221076
the_council_id = [owner_id, blue_bird_id, kou_id]
oasis_guild_id = 811395891122012180
skewl_guild_id = 498402270472306689
welcome_channel_id = 811395892338622504
general_channel_id = 811395892338622507  # the council id for now to test
achievements_channel_id = 881400374085443614
the_council_channel_id = 815501027381870603
welcome_message_id = 814157339950841876
nsfw_channel_id = 811395892338622510

admin_role_id = 814154599833272320
based_zeus_role_id = 830787685181554699
mod_role_id = 814153584526098542
member_role_id = 814154234433634316
dj_role_id = 815442370132049931
muted_role_id = 876417233247666187
unknown_role_id = 814155609158713414
all_roles = [admin_role_id, based_zeus_role_id, mod_role_id, dj_role_id, member_role_id]

temporary_duration = 3
counter_count = 6
mute_violation_count = 3
mute_violation_time = 30
kick_violation_count = 8
kick_violation_time = 60
ban_violation_count = 12
ban_violation_time = 90
threshold_count = 20

bot_prefixes = ('!', '~', '-', '_', '.', 'ch!')
normal_message_xp = 100
bot_message_xp = 200
voice_xp = 451  # multiplied with the minutes
passive_xp = 60  # multiplied with hours
leaderboard_controls = ["⏮️",
                        "⏪",
                        "◀️",
                        "🔄",
                        "▶️",
                        "⏩",
                        "⏭️"]

profanity = [r"https://c.tenor.com/7R0cugwI7k0AAAAC/watch-your-mouth-watch-your-profanity.gif",
             r"https://c.tenor.com/9z0inDzGansAAAAC/tone-watch-your-mouth.gif",
             r"https://c.tenor.com/mHAU_JH6eJYAAAAC/your-language-is-offensive-watch-your-mouth.gif"]
spamming = [r"https://c.tenor.com/kRKsQcSUmIYAAAAC/no-spam-spam-go-away.gif",
            r"https://c.tenor.com/pzmfzQWWjLkAAAAC/band-the-muppets.gif",
            r"https://c.tenor.com/ggufgUlr388AAAAd/stop-spamming-no-spamming.gif",
            r"https://c.tenor.com/mZZoOtDcouoAAAAM/stop-it-get-some-help.gif"]
bad_words = ("fck", "fcking")
database = DiscordDatabase()


def member_not_found(m): return f"{m} not found!"


def moderation_message(name, action): return f"{name} has been {action}."


def dj_message(author, member): return f"{member} has been given the role of dj by {author}."


def violation_reason(counts, action): return f"reached {counts} violations and is {action}"


def temp_message(name, duration, action):
    return f"{name} has been {action} for {duration} minute{check_plural(duration)}"


def welcome_message(member):
    return f"**TL;DR Click :white_check_mark: in welcome channel.**\nGreetings {member.name}, I welcome you to the " \
           f"{member.guild.name} server! :gem:\nRead and understand the rules in the welcome channel and react " \
           f":white_check_mark: if you agree.\n\nInvite your friends to the {member.guild.name} server!\nUse the " \
           f"link: https://discord.gg/T2ve5dZ82h :mailbox_with_mail:"


def emoji_convert(emoji_str_int):
    emoji_str_int = emoji_str_int[0] if len(emoji_str_int) > 1 else emoji_str_int
    return ord(emoji_str_int) if type(emoji_str_int) == str else chr(emoji_str_int)


def timestamp_convert(datetime_float_obj):
    return datetime.fromtimestamp(datetime_float_obj) if isinstance(
        datetime_float_obj, float) else datetime_float_obj.timestamp()


def snowflake_to_timestamp(snowflake):
    # right shift snowflake by 22 the same as snowflake / (2**22) but not recommended because it's slower
    # divided by 1000 because this timestamp is in seconds converting it to ms
    return float(((snowflake >> 22) + 1420070400000) / 1000)


def minutes_to_seconds(minutes): return minutes * 60


def round_off(floatNum): return round(floatNum, 3)


def time_delta_to_hours(time_delta):
    hours = time_delta.days * 24
    hours += time_delta.seconds / 3600
    hours += time_delta.microseconds / 3600e6
    return hours


def time_delta_to_minutes(time_delta):
    minutes = time_delta.days * 1440
    minutes += time_delta.seconds / 60
    minutes += time_delta.microseconds / 6e7
    return minutes


def get_member(bot, memberNameID):
    oasis_guild = bot.get_guild(oasis_guild_id)
    if isinstance(memberNameID, int) or memberNameID.isnumeric():
        member = oasis_guild.get_member(int(memberNameID))
    else:
        member = oasis_guild.get_member_named(memberNameID)
    return member


def check_plural(num): return 's' if num > 1 else ''


def number_readability(num):
    if num > 999999:
        num /= 1e6
        num = str(round(num, 1)) + 'M'
    elif num > 9999:
        num /= 1e3
        num = str(round(num, 1)) + 'K'
    elif type(num) == float:
        num = str(round(num, 0))[:-2]
    else:
        num = str(num)
    return num
