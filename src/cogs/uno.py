from discord.ext import commands
import sys
import asyncio
from discord_components import Button, Select, SelectOption, ButtonStyle

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import discord
import common
from uno_game import UnoGame, PlayerInstruction, colors, values


async def disable_components(interaction, content="Your turn has ended"):
    for row in interaction.message.components:
        for component in row:
            component.disabled = True
    await interaction.send(content=content)
    await interaction.message.edit(components=interaction.message.components)


def combine_inputs(first, second, third):
    instruction = first
    if second and third:
        instruction = f"{first} {second} {third}"
    elif second:
        instruction = f"{first} {second}"
    elif third:
        instruction = f"{first} {third}"
    if not instruction:
        return None
    return instruction


def create_embed(title, color=0xee2020): return discord.Embed(title=title, color=color)


def create_options(player):
    options = []
    for i, card in enumerate(player.hand):
        value = f"{card.color} {card.value}"
        options.append(SelectOption(label=f"{colors[card.color]} {values[card.value]}",
                                    value=value + '|' + str(i)))
    return options


def create_color_options():
    return [SelectOption(label=color[1], value=color[0]) for color in list(colors.items())[:-1]]


def interpret(turn):
    try:
        turnDict = {"np": "Card not playable",
                    "ne": "Your hand is not eligible for UNO",
                    "cs": "Challenge successful, previous player received 2 cards as penalty",
                    "cu": "Challenge unsuccessful",
                    "ie": "Instruction received is wrong",
                    "ut": "Unknown instruction type"}
        return turnDict[turn]
    except KeyError:
        return "Error: Unknown output"


class Uno(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.uno = None
        self.clockwise = True
        self.players = None
        self.waitList = []
        self.seed = None
        self.unoStart = False

    async def game(self):
        self.uno.start_game()
        while not self.uno.finalWinner:
            while not self.uno.winner:
                current = self.uno.currentPlayerIndex
                currentPlayer = self.players[current]
                for i, player in enumerate(self.players):
                    if i != current:
                        await self.challenge_message(index=i)
                turn = self.uno.turn(await self.turn_message(index=current))
                await self.check_turn(turn)
                if self.uno.clockwise != self.clockwise:
                    self.clockwise = not self.clockwise
                    self.players = self.players[::-1]
            for currentPlayer in self.players:
                await currentPlayer.send(embed=create_embed(f"The winner is {self.uno.winner.name}"))
            self.uno.new_game()
            self.player_reorder()

    async def check_turn(self, turn):
        current = self.uno.currentPlayerIndex
        currentPlayer = self.players[current]
        if turn == "cp":
            turn = self.uno.turn(await self.playable_message(index=current))
            await self.check_turn(turn)
        elif turn:
            await currentPlayer.send(embed=create_embed(title=interpret(turn)))

    def player_reorder(self):
        players = self.players
        self.players = []
        for unoPlayer in self.uno.players:
            for playerObj in players:
                if playerObj.name == unoPlayer.name:
                    self.players.append(playerObj)

    @commands.command(name="uno", aliases=['u'])
    async def uno(self, ctx, players, seed):
        if ctx.author.id in common.the_council_id:
            self.seed = seed
            self.players = [common.get_member(self.bot, memberID) for memberID in players.split()]
            self.uno = UnoGame([player.name for player in self.players], seed)
            messages = []
            for player in self.players:
                custom_id = 'y' + str(player.id)
                self.waitList.append(custom_id)
                components = [Button(label="yes", style=ButtonStyle.green, custom_id=custom_id)]
                players = [player.name for player in self.players]
                content = f"Are you ready to play UNO?\n`Players: {', '.join(players)}`\n`Seed: {self.seed}`"
                messages.append(await player.send(content=content, components=components))
            await asyncio.sleep(common.minutes_to_seconds(1))
            if not self.unoStart:
                for message in messages:
                    for row in message.components:
                        for component in row:
                            component.disabled = True
                    await message.edit(content="Timed Out!", components=message.components)
                self.__init__(self.bot)

    def uno_ui(self, index):
        playerOrder = []
        for i, player in enumerate(self.uno.players):
            if i != self.uno.currentPlayerIndex:
                text = f"{player.name} ({len(player.hand)})"
                if player.saidUno:
                    text += f" ***UNO***"
            else:
                text = f"**{player.name} ({len(player.hand)})**"
                if player.saidUno:
                    text += f" ***UNO***"
            playerOrder.append(text)
        playerOrder = (' > ' if self.uno.clockwise else ' < ').join(playerOrder)
        playerOrder += f"\n`Stacks: {self.uno.stacks}`"
        embed = discord.Embed(title="UNO Game", description=playerOrder, color=0xee2020)

        embed.add_field(name="Discard Pile", value=f"`{self.uno.discardPile.top_card()}`", inline=False)
        cardsHand = [f"{colors[card.color]} {values[card.value]}" for card in self.uno.players[index].hand]
        embed.add_field(name="Your Hand", value=f"`{', '.join(cardsHand)}`", inline=True)
        return embed

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.custom_id.startswith('y') and not self.unoStart:
            if interaction.custom_id in self.waitList:
                self.waitList.remove(interaction.custom_id)
                await disable_components(interaction, content="Answer confirmed!")
                if not self.waitList:
                    self.unoStart = True
                    await self.game()
        elif interaction.custom_id == "cs":
            turn = self.uno.turn(PlayerInstruction(interaction.custom_id[0]))
            await disable_components(interaction, content=interpret(turn))
            # possibly tell other the players too

    @commands.command()
    async def test(self, ctx):
        self.players = [ctx.author, ctx.author]
        self.uno = UnoGame(["Player 1", "Player 2"], "1234")
        self.unoStart = True
        self.uno.start_game()
        while not self.uno.winner:
            i = self.uno.currentPlayerIndex
            nextIndex = not i
            await self.challenge_message(index=nextIndex)
            turn = self.uno.turn(await self.turn_message(index=i))
            await self.check_turn(turn)

    @commands.command()
    async def uno_seed(self, seed):
        if not self.seed:
            self.seed = seed
        else:
            self.seed += seed

    async def challenge_message(self, index):
        components = [Button(label="challenge", style=ButtonStyle.red, custom_id="cs")]
        await self.players[index].send(embed=self.uno_ui(index), components=components)

    async def turn_message(self, index):
        components = [Select(placeholder="Select which card to play",
                             options=create_options(self.uno.players[index]),
                             custom_id='p'),
                      Select(placeholder="Specify color if card chosen is black",
                             options=create_color_options()),
                      [Button(label="draw card", style=ButtonStyle.green, custom_id='d'),
                       Button(label="uno", style=ButtonStyle.gray, custom_id='u'),
                       Button(label="challenge", style=ButtonStyle.red, custom_id='c'),
                       Button(label="end turn", style=ButtonStyle.blue, custom_id="end")]]
        message = await self.players[index].send(embed=self.uno_ui(index), components=components)

        firstInput, secondInput, thirdInput, instruction = None, None, None, None
        while True:
            interaction = await self.bot.wait_for("interaction", check=lambda i: i.message.id == message.id)
            if isinstance(interaction.component, Select):
                if interaction.custom_id == 'p':
                    card = interaction.values[0]
                    firstInput = "p " + card[:card.index('|')]
                else:
                    secondInput = interaction.values[0]
            elif interaction.custom_id == "end":
                break
            elif interaction.custom_id == 'u':
                thirdInput = interaction.custom_id
            else:
                secondInput = None
                thirdInput = None
                firstInput = interaction.custom_id

            instruction = PlayerInstruction(combine_inputs(firstInput, secondInput, thirdInput))
            await interaction.send(content=f"Turn: {instruction.translate()}")

        if instruction.type == 'e':
            await disable_components(interaction, content="Instructions unclear")
            await self.turn_message(index)
        elif instruction.type == 'p' and instruction.playCard.color == 'bk' and not instruction.colorChosen:
            await disable_components(interaction, content="Please select the card and specify the color")
            await self.turn_message(index)
        else:
            await disable_components(interaction)
            return instruction

    async def playable_message(self, index):
        components = [[Button(label="yes", style=ButtonStyle.green, custom_id='y'),
                       Button(label="no", style=ButtonStyle.red, custom_id='n'),
                       Button(label="uno", style=ButtonStyle.gray, custom_id='u'),
                       Button(label="end turn", style=ButtonStyle.blue, custom_id="end")],
                      Select(placeholder="Specify color if card is black",
                             options=create_color_options())]
        card = self.uno.drawnCard
        message = await self.players[index].send(embed=create_embed(
            title=f"Play {colors[card.color]} {values[card.value]}?"), components=components)
        firstInput, secondInput, thirdInput, instruction = None, None, None, None
        while True:
            interaction = await self.bot.wait_for("interaction", check=lambda i: i.message.id == message.id)
            if interaction.custom_id == "end":
                break
            # colors to choose
            elif isinstance(interaction.component, Select):
                secondInput = interaction.values[0]
            # uno
            elif interaction.custom_id == 'u':
                thirdInput = interaction.custom_id
            # yes or no
            else:
                firstInput = interaction.custom_id

            instruction = PlayerInstruction(combine_inputs(firstInput, secondInput, thirdInput))
            await interaction.send(content=f"Turn: {instruction.translate()}")

        if instruction.type == 'e':
            await disable_components(interaction, content="Instructions unclear")
            await self.playable_message(index)
        elif instruction.type == 'y' and card.color == 'bk' and not instruction.colorChosen:
            await disable_components(interaction, content="Please select the card and specify the color")
            await self.playable_message(index)
        else:
            await disable_components(interaction)
            return instruction


def setup(bot):
    bot.add_cog(Uno(bot))
