from discord.ext import commands
import sys
import asyncio
from discord_components import DiscordComponents, ComponentsBot, Button, Select, SelectOption

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import discord
import common
import uno_game


def find_player(players, player):
    for i, playerList in enumerate(players):
        if playerList.id == player.id:
            return i, player
    return None


def check_ready(players):
    for player in players:
        if not player.unoReady:
            return False
    return True


def create_instructions():
    embed = discord.Embed(title="Commands:", color=0xee2020)
    embed.add_field(name="uno play color value [color]",
                    value="eg. `uno play rd +2`, `uno play red +2`, `uno play black +4 green`", inline=False)
    embed.add_field(name="uno draw card", value="eg. `uno draw card`", inline=False)
    embed.add_field(name="uno yes [color] | uno no",
                    value="if drawn card is playable: eg. `uno yes`, `uno no`, `uno yes red`", inline=False)
    embed.add_field(name="uno challenge", value="eg. `uno challenge`", inline=False)
    return embed


def create_embed(uno, i):
    def create_player_order(uno):
        playersText = ""
        for i, player in enumerate(uno.players):
            if i != uno.currentPlayerIndex:
                playersText += f"{player.name}"
            else:
                playersText += f"**{player.name}**"

            playersText += f" ({len(player.hand)}) > "
        # delete the last " > "
        playersText = playersText[:-2]
        return playersText

    embed = discord.Embed(title="UNO Game", description=create_player_order(uno), color=0xee2020)
    embed.add_field(name="Discard Pile", value=f"`{uno.discardPile.top_card()}`", inline=False)
    cardsHand = [f"{uno_game.colors[card.color]} {uno_game.values[card.value]}" for card in uno.players[i].hand]
    embed.add_field(name="Your Hand", value=f"`{', '.join(cardsHand)}`", inline=True)
    return embed


def create_options(player, cardPlayable=None):
    options = []
    if not cardPlayable:
        for card in player.hand:
            options.append(SelectOption(label=f"{uno_game.colors[card.color]} {uno_game.values[card.value]}",
                                        value=f"{card.color} {card.value}"))
        options.append(SelectOption(label="Draw Card", value="draw card"))
        options.append(SelectOption(label="Challenge", value="challenge"))
    else:
        if cardPlayable.color == 'bk':
            for color in list(uno_game.colors.values())[:-1]:
                options.append(SelectOption(label=f"Yes {color.capitalize()}", value=f"yes {uno_game.colorsFlipped[color]}"))
        else:
            options.append(SelectOption(label="Yes", value="yes"))
        options.append(SelectOption(label="No", value="no"))
    return options


class Uno(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.uno = None
        self.players = None
        self.unoStart = False

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.content[:3] == "uno":
            content = message.content.split()[1:]
            if content[0] == "yes" and not self.unoStart:
                self.uno.start_game()
                self.unoStart = True
                # for player in self.players:
                #     await player.send(embed=create_instructions())
                for i, player in enumerate(self.players):
                    if i == self.uno.currentPlayerIndex:
                        components = [Select(placeholder="It's your turn!!!", options=create_options(self.uno.players[i]))]
                        await player.send(embed=create_embed(self.uno, i), components=components)
                    else:
                        await player.send(embed=create_embed(self.uno, i))
                interaction = await self.bot.wait_for("select_option")
                turn = self.uno.turn(interaction.values[0])
                if turn is None:
                    for i, player in enumerate(self.players):
                        if i == self.uno.currentPlayerIndex:
                            components = [Select(placeholder="It's your turn!!!", options=create_options(self.uno.players[i]))]
                            await player.send(embed=create_embed(self.uno, i), components=components)
                        else:
                            await player.send(embed=create_embed(self.uno, i))
                else:
                    await self.players[self.uno.currentPlayerIndex].send(turn)

                # await global_send(self.players, self.uno)
            # elif self.unoStart:
            #     i, player = find_player(self.players, message.author)
            #     if i == self.uno.currentPlayerIndex:
            #         turn = self.uno.turn(' '.join(content))
            #         if turn is None:
            #             await global_send(self.players, self.uno)
            #         else:
            #             await self.players[self.uno.currentPlayerIndex].send(turn)
            #     else:
            #         await player.send("It's not your turn yet...")

    @commands.command()
    async def select(self, ctx):
        await ctx.send(
            "Hello, World!",
            components=[
                Select(
                    placeholder="Select something!",
                    options=[
                        SelectOption(label="A", value="A"),
                        SelectOption(label="B", value="B")
                    ]
                ), Button(label="WOW button!", custom_id="button1")
            ]
        )
        interaction = await self.bot.wait_for("select_option")
        interaction = await self.bot.wait_for("button_click", check=lambda i: i.custom_id == "button1")
        await interaction.send(content="Button clicked!")
        await interaction.send(content=f"{interaction.values[0]} selected!")

    @commands.command(name="uno", aliases=['u'])
    async def uno(self, ctx, players, seed):
        if ctx.author.id in common.the_council_id:
            if players != "end":
                self.players = [common.get_member(self.bot, memberID) for memberID in players.split()]
                self.uno = uno_game.UnoGame([player.name for player in self.players], seed)
                for player in self.players:
                    await player.send("Are you ready?\nType `uno yes`")
                await asyncio.sleep(common.minutes_to_seconds(1))
                if not self.unoStart:
                    self.uno = None

    @commands.command(name="uno_end", aliases=['ue'])
    async def uno_end(self, ctx):
        if ctx.author.id in common.the_council_id:
            self.__init__(self.bot)

    @commands.command(name="test", aliases=['t'])
    async def test(self, ctx):
        for emoji in ctx.guild.emojis:
            print(emoji.id)
        emoji = self.bot.get_emoji(893523538173124640)
        await ctx.message.add_reaction("<:Red_0:893523350805168138>")


def setup(bot):
    bot.add_cog(Uno(bot))
