from discord.ext import commands
import asyncio
import discord
from src.app import common
from src.app.uno_game import UnoGame, PlayerInstruction, colors, values
from pickle import dump, load


async def disable_components(interaction, content="Your turn has ended"):
    for row in interaction.message.components:
        for component in row:
            component.disabled = True
    await interaction.send(content=content)
    await interaction.message.edit(components=interaction.message.components)


def num_to_emoji(number):
    value = {0: ":zero:",
             1: ":one:",
             2: ":two:",
             3: ":three:",
             4: ":four:",
             5: ":five:",
             6: ":six:",
             7: ":seven:",
             8: ":eight:",
             9: ":nine:"}
    digits = [value[int(num)] for num in list(str(number))]
    return "**+**" + ''.join(digits)


def convert_emoji(card):
    color = {'rd': ":red_circle:",
             'yw': ":yellow_circle:",
             'be': ":blue_circle:",
             'gn': ":green_circle:",
             'bk': ":black_circle:"}
    value = {"0": ":zero:",
             "1": ":one:",
             "2": ":two:",
             "3": ":three:",
             "4": ":four:",
             "5": ":five:",
             "6": ":six:",
             "7": ":seven:",
             "8": ":eight:",
             "9": ":nine:",
             "r": ":arrows_counterclockwise:",
             "s": ":track_next:",
             "+2": "**+**:two:",
             "w": ":regional_indicator_w:",
             "+4": "**+**:four:"}
    return f"{color[card.color]}{value[card.value]}"


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


def create_embed(description, title="UNO Game", color=0xee2020):
    return discord.Embed(title=title, description=description, color=color)


def create_win_embed(uno, color=0xee2020, finalWin=False):
    if not finalWin:
        embed = discord.Embed(title="Round Summary",
                              description=f"**First to reach {uno.winningPoints} points wins!**:confetti_ball:",
                              color=color)
    else:
        embed = discord.Embed(title="Finished UNO Game",
                              description=f"**The winner is {uno.finalWinner}!**:partying_face:", color=color)
    for player in uno.players:
        embed.add_field(name=f"{player.name} Points", value=str(player.points), inline=False)
    return embed


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
        self.moves = []

    async def game(self):
        while True:
            while True:
                if self.uno.winner:
                    print("there is a winner")
                    break
                current = self.uno.currentPlayerIndex
                # currentPlayer = self.players[current]
                for i, player in enumerate(self.players):
                    if i != current:
                        await self.challenge_message(index=i)
                instruction, interaction = await self.turn_message(index=current)
                while not await self.check_instruction(instruction, interaction, index=current):
                    instruction, interaction = await self.turn_message(index=current)
                self.moves.append(instruction.translate())
                await self.check_turn(self.uno.turn(instruction))
                await self.uno_save()
                if self.uno.clockwise != self.clockwise:
                    self.clockwise = not self.clockwise
                    self.players = self.players[::-1]
            if not self.uno.finalWinner:
                for player in self.players:
                    await player.send(embed=create_win_embed(self.uno))
                self.uno.new_game()
                self.player_reorder()
            else:
                break
        for player in self.players:
            await player.send(embed=create_win_embed(self.uno, finalWin=True))
        self.__init__(self.bot)

    async def uno_save(self):
        with open("./uno_game.pkl", 'wb') as f:
            memberIDs = [player.id for player in self.players]
            save_dict = {"uno": self.uno, "clockwise": self.clockwise, "players": memberIDs, "seed": self.seed,
                         "unoStart": self.unoStart, "moves": self.moves}
            dump(save_dict, f)

    async def check_turn(self, turn):
        current = self.uno.currentPlayerIndex
        currentPlayer = self.players[current]
        if turn == "cp":
            instruction, interaction = await self.playable_message(index=current)
            while not await self.check_instruction(instruction, interaction, index=current, insType='y'):
                instruction, interaction = await self.playable_message(index=current)
            self.moves.append(instruction.translate())
            await self.check_turn(self.uno.turn(instruction))
        elif turn:
            await currentPlayer.send(embed=create_embed(description=interpret(turn)))

    async def check_instruction(self, instruction, interaction, index, insType='p'):
        if instruction and insType == 'p':
            card = instruction.playCard
        elif instruction and insType == 'y':
            card = self.uno.drawnCard
        else:
            return False

        if instruction.type == 'e':
            await disable_components(interaction, content="Instructions unclear")
            return False
        elif instruction.type == insType and card.color == 'bk' and not instruction.colorChosen:
            await disable_components(interaction, content="Please select the card and specify the color")
            return False
        else:
            await disable_components(interaction)
            return True

    def player_reorder(self):
        players = self.players
        self.players = []
        for unoPlayer in self.uno.players:
            for playerObj in players:
                if playerObj.name == unoPlayer.name:
                    self.players.append(playerObj)

    @commands.command(name="uno", aliases=['u'])
    async def uno(self, ctx, players):
        if ctx.author.id in common.the_council_id and self.seed:
            self.players = [common.get_member(self.bot, memberID) for memberID in players.split()]
            self.uno = UnoGame([player.name for player in self.players], self.seed)
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

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.custom_id.startswith('y') and not self.unoStart:
            if interaction.custom_id in self.waitList:
                self.waitList.remove(interaction.custom_id)
                await disable_components(interaction, content="Answer confirmed!")
                if not self.waitList:
                    self.unoStart = True
                    self.uno.start_game()
                    await self.game()
        elif interaction.custom_id == "cs":
            instruction = PlayerInstruction(interaction.custom_id[0])
            self.moves.append(instruction.translate())
            turn = self.uno.turn(instruction)
            await disable_components(interaction, content=interpret(turn))
            if turn == "cs":
                for player in self.players:
                    await player.send(content=interpret(turn))

    # @commands.command()
    # async def test(self, ctx):
    #     guild = self.bot.get_guild(common.oasis_guild_id)
    #     member = guild.get_member(799843363058221076)
    #     member = guild.get_member(319032492059525130)
    #     member = guild.get_member(498374117561597972)
    #     print(member)
    #     print(dir(member))
    #     try:
    #         message = await member.send("Ohayo!")
    #         print(message)
    #         print("Message Sent!")
    #     except discord.Forbidden:
    #         print("Forbidden")
        # self.players = [ctx.author, ctx.author]
        # self.uno = UnoGame(["Player 1", "Player 2"], "")
        # self.unoStart = True
        # self.uno.start_game()
        # stacking_moves = ["p rd r", 'd', "p rd 3", "p bk w yw", "p yw +2"]
        # for move in stacking_moves:
        #     self.uno.turn(PlayerInstruction(move))
        # await ctx.send(embed=self.uno_ui(self.uno.currentPlayerIndex))
        # # while not self.uno.winner:
        # #     i = self.uno.currentPlayerIndex
        # #     nextIndex = not i
        # #     await self.challenge_message(index=nextIndex)
        # #     instruction, interaction = await self.turn_message(index=i)
        # #     while not await self.check_instruction(instruction, interaction, index=i):
        # #         instruction, interaction = await self.turn_message(index=i)
        # #     await self.check_turn(self.uno.turn(instruction))
        # # for player in self.players:
        # #     await player.send(embed=create_win_embed(self.uno))
        # # self.__init__(self.bot)

    @commands.command()
    async def uno_seed(self, ctx, seed):
        if not self.seed:
            self.seed = seed
        else:
            self.seed += seed
        await ctx.send(f"The new seed is `{self.seed}`")

    @commands.command()
    async def uno_load(self, ctx):
        with open("./uno_game.pkl", 'rb') as f:
            save_dict = load(f)
            self.__init__(self.bot)
            self.uno = save_dict["uno"]
            self.clockwise = save_dict["clockwise"]
            players = save_dict["players"]
            self.players = [common.get_member(self.bot, memberID) for memberID in players]
            self.seed = save_dict["seed"]
            self.unoStart = save_dict["unoStart"]
            self.moves = save_dict["moves"]
            await self.game()

    async def challenge_message(self, index):
        components = [Button(label="challenge", style=ButtonStyle.red, custom_id="cs")]
        message = await self.players[index].send(embed=self.uno_ui(index), components=components)

    async def turn_message(self, index):
        components = [
            Select(placeholder="Select which card to play",
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
            interaction = await self.bot.wait_for("interaction", check=lambda inter: inter.message.id == message.id)

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
            await interaction.send(content=f"Turn: `{instruction.translate()}`")
        return instruction, interaction

    async def playable_message(self, index):
        components = [Select(placeholder="Specify color if card is black",
                             options=create_color_options()),
                      [Button(label="yes", style=ButtonStyle.green, custom_id='y'),
                       Button(label="no", style=ButtonStyle.red, custom_id='n'),
                       Button(label="uno", style=ButtonStyle.gray, custom_id='u'),
                       Button(label="end turn", style=ButtonStyle.blue, custom_id="end")]]
        message = await self.players[index].send(embed=create_embed(
            description=f"Play {convert_emoji(self.uno.drawnCard)}?"),
            components=components)
        firstInput, secondInput, thirdInput, instruction = None, None, None, None
        while True:
            interaction = await self.bot.wait_for("interaction", check=lambda inter: inter.message.id == message.id)
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
            await interaction.send(content=f"Turn: `{instruction.translate()}`")
        return instruction, interaction

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
        playerOrder = ' :arrow_right: '.join(playerOrder)
        embed = discord.Embed(title="UNO Game", description=playerOrder, color=0xee2020)
        if self.uno.stacks:
            embed.add_field(name="Stacks", value=f"{num_to_emoji(self.uno.stacks)}")
        embed.add_field(name="Discard Pile", value=f"{convert_emoji(self.uno.discardPile.top_card())}", inline=False)
        cardsHand = [convert_emoji(card) for card in self.uno.players[index].hand]
        embed.add_field(name="Your Hand", value=f"{', '.join(cardsHand)}", inline=True)
        return embed


def setup(bot):
    bot.add_cog(Uno(bot))
