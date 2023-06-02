from discord.ext import commands
from app import common


class Component:
    def __init__(self, component):
        # component = "- text (sub)"
        dummy = component.split()
        self.text = ' '.join(dummy[1:-1])
        self.sub = dummy[-1][1]


class Category:
    def __init__(self, components, category):
        # components = [texts]
        self.components = [Component(component) for component in components]
        self.category = category


class Plans:
    def __init__(self, message):
        # message = ["Plans:", "- oaeirsnt", "Kristiana Plans:", "- oaeirsnt"]
        self.dictionary = {'G': "General Plans:", 'C': "Charles Plans:", 'K': "Kristiāna Plans:"}
        self.categories = []
        indexes = [i for i, t in enumerate(message) if "Plans:" in t]
        for a, b in zip(indexes, indexes[1:]):
            self.categories.append(Category(message[a + 1:b], message[a][0]))
        self.categories.append(Category(message[indexes[-1] + 1:], message[indexes[-1]][0]))

    def add(self, text, category):
        index = list(self.dictionary.keys()).index(category.upper())
        self.categories[index].components.append(Component(f"- {text}"))

    def remove(self, number, category):
        index = list(self.dictionary.keys()).index(category.upper())
        self.categories[index].components.pop(number - 1)

    def print(self):
        text = []
        for category in self.categories:
            text.append(self.dictionary[category.category])
            for component in category.components:
                text.append(f"- {component.text} ({component.sub})")
        return '\n'.join(text)


class Kbye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.plans_print = None

    @commands.command(name="add")
    async def add(self, ctx, text, category):
        channel = await self.bot.fetch_channel(common.plans_channel_id)
        messageID = common.database.get([('guildID', ctx.guild.id), ("leaderboardMessageID", '')],
                                        dbTable="memory")[0][0]
        message = await channel.fetch_message(messageID)
        plans = Plans(message.content.split('\n'))
        self.plans_print = plans.print()
        plans.add(text, category)
        await message.edit(content=plans.print())

    @commands.command(name="remove")
    async def remove(self, ctx, number, category):
        channel = await self.bot.fetch_channel(common.plans_channel_id)
        messageID = common.database.get([('guildID', ctx.guild.id), ("leaderboardMessageID", '')],
                                        dbTable="memory")[0][0]
        message = await channel.fetch_message(messageID)
        plans = Plans(message.content.split('\n'))
        self.plans_print = plans.print()
        plans.remove(int(number), category)
        await message.edit(content=plans.print())

    @commands.command(name="undo")
    async def undo(self, ctx):
        if self.plans_print:
            channel = await self.bot.fetch_channel(common.plans_channel_id)
            messageID = common.database.get([('guildID', ctx.guild.id), ("leaderboardMessageID", '')],
                                            dbTable="memory")[0][0]
            message = await channel.fetch_message(messageID)
            plans = Plans(message.content.split('\n'))
            await message.edit(content=self.plans_print)
            self.plans_print = plans
        else:
            await ctx.send("I cannot undo :((")

    # @commands.command(name="test")
    # async def test(self, ctx):
    #     channel = await self.bot.fetch_channel(1093922720082821210)
    #     messageID = common.database.get([('guildID', ctx.guild.id), ("leaderboardMessageID", '')],
    #                                     dbTable="memory")[0][0]
    #     message = await channel.fetch_message(messageID)
    #     content = await channel.fetch_message(1094269955165388931)
    #     await message.edit(content=content.content)


def setup(bot):
    bot.add_cog(Kbye(bot))
