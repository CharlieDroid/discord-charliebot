"""
# UNO GAME LOGIC #
Play UNO through a command prompt. It can also be used as backend for UNO games.
      ___           ___           ___           ___                       ___
     /\  \         /\  \         /\  \         /\__\          ___        /\  \
    /::\  \       /::\  \       /::\  \       /:/  /         /\  \      /::\  \
   /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/  /          \:\  \    /:/\:\  \
  /:/  \:\  \   /:/  \:\  \   /::\~\:\  \   /:/__/  ___      /::\__\  /:/  \:\__\
 /:/__/ \:\__\ /:/__/ \:\__\ /:/\:\ \:\__\  |:|  | /\__\  __/:/\/__/ /:/__/ \:|__|
 \:\  \  \/__/ \:\  \ /:/  / \/_|::\/:/  /  |:|  |/:/  / /\/:/  /    \:\  \ /:/  /
  \:\  \        \:\  /:/  /     |:|::/  /   |:|__/:/  /  \::/__/      \:\  /:/  /
   \:\  \        \:\/:/  /      |:|\/__/     \::::/__/    \:\__\       \:\/:/  /
    \:\__\        \::/  /       |:|  |        ~~~~         \/__/        \::/__/
     \/__/         \/__/         \|__|                                   ~~
© Charles A. Sosmeña, https://github.com/CharlieDroid

 _______   ________   ______   _______         __       __  ________
|       \ |        \ /      \ |       \       |  \     /  \|        \
| $$$$$$$\| $$$$$$$$|  $$$$$$\| $$$$$$$\      | $$\   /  $$| $$$$$$$$
| $$__| $$| $$__    | $$__| $$| $$  | $$      | $$$\ /  $$$| $$__
| $$    $$| $$  \   | $$    $$| $$  | $$      | $$$$\  $$$$| $$  \
| $$$$$$$\| $$$$$   | $$$$$$$$| $$  | $$      | $$\$$ $$ $$| $$$$$
| $$  | $$| $$_____ | $$  | $$| $$__/ $$      | $$ \$$$| $$| $$_____
| $$  | $$| $$     \| $$  | $$| $$    $$      | $$  \$ | $$| $$     \
 \$$   \$$ \$$$$$$$$ \$$   \$$ \$$$$$$$        \$$      \$$ \$$$$$$$$
Character Dictionary:
p = Play
c = Challenge
d = Draw Card
y = Yes
n = No
u = Uno
e = Error
cr = color (dictionary named colors below)
ve = value (dictionary named values below)
ne = Not Eligible (for uno)
cp = Card Playable (if drawn card is playable)
ie = Instruction Error (instruction/input received is unclear)
ut = Unknown Type (instruction type not known)
np = Not Playable (card not playable)
cs = Challenge Successful (previous player got 2 cards for penalty)
cu = Challenge Unsuccessful (challenge unsuccessful)
| = Logic OR
enclosed in `()` = Optional
enclosed in `<>` = Input/Instruction

Player Instructions/Input:
1. Playing a card (cannot play other cards except draw cards if there are stacks)
`p <cr> <ve> (cr|u) (u)`
examples: `p yw 9`, `p be 1 u`, `p bk +4 rd`, `p bk w gn u`

2. Challenge previous player
`c`

3. Draw a card (draw all stacks if you choose not to stack a draw card)
`d`

4. If drawn card is playable
`y (cr|u) (u)` or `n`

Notes:
When playing a card or `y` when card is playable, color must be specified if card to be played is black.
Make sure that the cards to be played is inside the hand of the player.
No protection when emptying all cards from discard and draw pile.
Card stacking is set to true as default
"""
import random as rand

# colors of a card
# red, yellow, blue, green, black
colors = {"rd": "red",
          "yw": "yellow",
          "be": "blue",
          "gn": "green",
          "bk": "black"}
# values of a card
# 0 to 9, +2, +4, reverse, skip, wild
values = {"0": "zero",
          "1": "one",
          "2": "two",
          "3": "three",
          "4": "four",
          "5": "five",
          "6": "six",
          "7": "seven",
          "8": "eight",
          "9": "nine",
          "r": "reverse",
          "s": "skip",
          "+2": "+two",
          "w": "wild",
          "+4": "+four"}

# colors dictionary but flipping the values and keys
colorsFlipped = {y: x for x, y in colors.items()}

# values dictionary but flipping the values and keys
valuesFlipped = {y: x for x, y in values.items()}

# points of each value according to uno rules
valuePoints = {"0": 0,
               "1": 1,
               "2": 2,
               "3": 3,
               "4": 4,
               "5": 5,
               "6": 6,
               "7": 7,
               "8": 8,
               "9": 9,
               "r": 20,
               "s": 20,
               "+2": 20,
               "w": 50,
               "+4": 50}


class Card:
    def __init__(self, color, value):
        # must be in rd, yw, ...
        self.color = color
        # must be in 0, 1, +2, w, +4, ...
        self.value = value

    def __repr__(self):
        return f"{colors[self.color]} {values[self.value]}"


class DrawPile:
    def __init__(self, decks=1):
        self.deck = []
        [self.init_deck() for _ in range(decks)]

    def init_deck(self):
        colorList = list(colors)[:4]
        black = list(colors)[-1]
        valuesList = list(values)
        numberValues = valuesList[1:10]
        actionCards = valuesList[10:13]
        wildCards = valuesList[-2:]

        # initialize zero cards
        for color in colorList:
            self.deck.append(Card(color, valuesList[0]))

        # initialize number cards
        for i in range(2):
            for color in colorList:
                for value in numberValues:
                    self.deck.append(Card(color, value))

        # initialize action cards that are colored
        for i in range(2):
            for color in colorList:
                for value in actionCards:
                    self.deck.append(Card(color, value))

        # initialize wild cards
        for i in range(4):
            for value in wildCards:
                self.deck.append(Card(black, value))

    def shuffle(self, seed):
        rand.seed(seed)
        rand.shuffle(self.deck)

    def get_card(self):
        card = self.deck[-1]
        self.deck.pop(-1)
        return card

    def add_card(self, card):
        self.deck.append(card)

    def reset(self):
        self.__init__()


class DiscardPile:
    def __init__(self):
        self.deck = []

    def top_card(self):
        return self.deck[-1]

    def add_card(self, card):
        self.deck.append(card)

    def reset(self):
        topCard = self.top_card()
        self.deck = []
        self.deck.append(topCard)


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.points = 0
        self.saidUno = False

    def get_card(self, card):
        for i, deckCard in enumerate(self.hand):
            if (deckCard.color == card.color) and (deckCard.value == card.value):
                self.hand.pop(i)
                return card
        return None

    def add_card(self, card):
        self.hand.append(card)
        self.sort_hand()

    def sort_hand(self):
        def get_first(card_tuple):
            return card_tuple[0]
        # sorts the cards by colors and value
        colorOrder, valueOrder = list(colors), list(valuePoints)
        valueList = sorted([(valueOrder.index(card.value), card) for card in self.hand], key=get_first)
        self.hand = [card_tuple[1] for card_tuple in valueList]
        colorList = sorted([(colorOrder.index(card.color), card) for card in self.hand], key=get_first)
        self.hand = [card_tuple[1] for card_tuple in colorList]

    def get_hand_points(self):
        points = 0
        for card in self.hand:
            points += valuePoints[card.value]
        return points

    def __len__(self):
        return len(self.hand)

    def __repr__(self):
        return f"{self.name}{' UNO' if self.saidUno else ''}: " \
               f"{', '.join([f'{colors[c.color]} {values[c.value]}' for c in self.hand])}"


class PlayerInstruction:
    def __init__(self, instruction):
        # Type:
        # p = Play, c = Challenge, d = Draw card, y = Yes, n = No, e = Error
        self.types = {'p': "play", 'y': "yes", 'n': "no", 'c': "challenge", 'd': "draw card", 'e': "error", 'u': "uno"}
        if not instruction or (instruction[0] not in list(self.types)):
            self.type = list(self.types)[-1]
        else:
            self.instruction = instruction.lower().split()
            self.type = self.instruction[0]
        self.colorChosen = None
        self.uno = False
        self.playCard = None
        if self.type == list(self.types)[0]:
            self.check_card()
            self.playCard = Card(self.instruction[1], self.instruction[2])
            self.check_color_uno(self.instruction[3:])
        elif self.type == list(self.types)[1]:
            self.check_color_uno(self.instruction[1:])

    def check_card(self):
        if (not (self.instruction[1] in colors.keys())) or (not (self.instruction[2] in values.keys())):
            self.type = list(self.types)[-1]

    def check_color_uno(self, instruction):
        if instruction:
            if instruction[0] == 'u':
                self.uno = True
            else:
                self.colorChosen = instruction[0]
                if len(instruction) > 1:
                    self.uno = True

    def translate(self):
        translation = []
        if self.type == list(self.types)[0]:
            translation.append(self.types[self.type])
            translation.append(colors[self.playCard.color])
            translation.append(values[self.playCard.value])
            if self.colorChosen:
                translation.append(colors[self.colorChosen])
            if self.uno:
                translation.append("uno")
        elif self.type == list(self.types)[1]:
            translation.append(self.types[self.type])
            if self.colorChosen:
                translation.append(colors[self.colorChosen])
            if self.uno:
                translation.append("uno")
        else:
            translation.append(self.types[self.type])
        return ' '.join(translation)


class UnoGame:
    def __init__(self, playerNames, seed, decks=1, winningPoints=None, players=None):
        if players is None:
            players = []
        self.seed = seed
        self.playerNames = playerNames
        self.players = players
        self.numPlayers = len(self.playerNames)
        self.check_players()

        self.startNumCards = 7
        self.decks = decks
        self.winningPoints = winningPoints
        if winningPoints is None:
            self.winningPoints = self.numPlayers * 150 - 100
        self.drawPile = DrawPile(decks=self.decks)
        self.discardPile = DiscardPile()
        self.clockwise = True
        self.toSkip = False  # for skip
        self.currentPlayerIndex = -1
        self.previousPlayerIndex = None
        self.previousTwoPlayerIndex = None
        self.winner = None
        self.finalWinner = None
        self.drawnCard = None

        self.cardStacking = True
        self.stacks = 0
        self.stackingValue = None  # what card value is being stacked

    def check_players(self):
        if self.numPlayers < 2 or self.numPlayers > 10:
            raise ValueError('{numPlayers} player/s are not within the rules of uno'.format(numPlayers=repr(self.numPlayers)))

    def reverse(self):
        if self.numPlayers > 2:
            self.players = self.players[::-1]
            self.clockwise = not self.clockwise
        else:
            self.skip()

    def skip(self):
        # checks for this in update next turn
        self.toSkip = True

    def check_deck(self, numberOfCards):
        # if draw pile is empty(negative) then use discard pile as the new draw pile
        if (len(self.drawPile.deck) - numberOfCards) < 0:
            # all of discard pile except the top card
            self.drawPile.deck = self.discardPile.deck[:-1]
            self.discardPile.reset()
            self.drawPile.shuffle(self.seed)

    def draw(self, player, numberOfCards, skip=True):
        self.check_deck(numberOfCards)
        drawnCards = []
        for i in range(numberOfCards):
            drawnCard = self.drawPile.get_card()
            drawnCards.append(drawnCard)
            player.add_card(drawnCard)
        if player.saidUno and len(player) > 1:
            player.saidUno = not player.saidUno
        # if draw more than 1 card and is not a challenge then skip
        if numberOfCards > 1 and skip:
            self.skip()
        return drawnCards

    def check_winner(self):
        # if previous player who placed a card is winner
        if not self.players[self.currentPlayerIndex].hand:
            winnerPlayer = self.players[self.currentPlayerIndex]
            # get total points from current game
            for i in range(self.numPlayers):
                if i != self.currentPlayerIndex:
                    winnerPlayer.points += self.players[i].get_hand_points()
            # if winner has greater than 500 points then he has won the game and game stops
            self.winner = winnerPlayer
            if winnerPlayer.points >= self.winningPoints:
                self.finalWinner = winnerPlayer

    def check_stack(self, value):
        if self.cardStacking:
            nextPlayer = self.players[self.get_next_player()]
            for card in nextPlayer.hand:
                if card.value == value:
                    return True
        return False

    def play(self, cardPlayed, colorChosen=None):
        def draw_card(value):
            self.stacks += int(value[-1])
            if not self.check_stack(value):
                self.draw(self.players[self.get_next_player()], self.stacks)
                self.stacks = 0
                self.stackingValue = None
            else:
                self.stackingValue = value
        if cardPlayed.value == 'r':
            self.reverse()
        elif cardPlayed.value == 's':
            self.skip()
        elif cardPlayed.value == '+2':
            draw_card('+2')
        elif cardPlayed.value == '+4':
            draw_card('+4')
            cardPlayed.color = colorChosen
        elif cardPlayed.value == 'w':
            if not self.discardPile.deck:
                cardPlayed.color = 'bk'
            else:
                cardPlayed.color = colorChosen
        self.discardPile.add_card(cardPlayed)
        self.check_winner()

    def challenge(self):
        previousPlayer = self.players[self.previousPlayerIndex]
        if not previousPlayer.saidUno and len(previousPlayer) == 1:
            previousPlayer.saidUno = True
            self.draw(previousPlayer, 2, skip=False)
            return "cs"
        return "cu"

    def get_next_player(self):
        nextPlayerIndex = self.currentPlayerIndex + 1
        if nextPlayerIndex == self.numPlayers:
            nextPlayerIndex = 0
        return nextPlayerIndex

    def check_play(self, cardPlayed):
        topCard = self.discardPile.top_card()
        # if top card black or card played black then its okay
        # first argument is always checked and if it is true it proceeds
        if topCard.color == 'bk' or cardPlayed.color == 'bk':
            return True
        elif self.stacks:
            return self.stackingValue == cardPlayed.value
        return topCard.color == cardPlayed.color or topCard.value == cardPlayed.value

    def update_turn(self):
        self.previousTwoPlayerIndex = self.previousPlayerIndex
        self.previousPlayerIndex = self.currentPlayerIndex
        self.currentPlayerIndex = self.get_next_player()
        # if skip then update again
        if self.toSkip:
            self.toSkip = False
            self.currentPlayerIndex = self.get_next_player()
        # if two players ago is in uno but did not callout it will be set to true
        if self.previousTwoPlayerIndex:
            check = self.previousTwoPlayerIndex != self.previousPlayerIndex
            if check and len(self.players[self.previousTwoPlayerIndex]) == 1:
                self.players[self.previousTwoPlayerIndex].saidUno = True

    def start_game(self):
        # gives the players the feel of shuffling the deck
        self.drawPile.shuffle(self.seed)
        # seed is used to ensure a different deck is shuffled everytime
        # players are initialized seven cards are dealt to each player
        if not self.players:
            for playerName in self.playerNames:
                self.players.append(Player(playerName))
                [self.players[-1].add_card(self.drawPile.get_card()) for i in range(self.startNumCards)]
        else:
            for player in self.players:
                player.hand = [self.drawPile.get_card() for i in range(self.startNumCards)]
                player.saidUno = False
                player.sort_hand()

        # a card is picked from the draw pile and is played to first player
        # if card is +4 then shuffle the deck again
        card = self.drawPile.get_card()
        if card.value == '+4':
            self.drawPile.add_card(card)
            self.start_game()
        else:
            self.play(card)
            self.update_turn()

    def turn(self, instruction):
        # ne = Not Eligible for Uno, cp = Card Playable, ie = Error Instruction, ut = Unknown Type of instruction
        # cs = Challenge Successful, cu = Challenge Unsuccessful, np = Not Playable
        currentPlayer = self.players[self.currentPlayerIndex]
        if instruction.type == 'c':
            # "cs" or "cu"
            return self.challenge()

        if instruction.type == 'y' and self.drawnCard:
            card = currentPlayer.get_card(self.drawnCard)
            self.drawnCard = None
            self.play(card, instruction.colorChosen)
        elif instruction.type == 'n' and self.drawnCard:
            self.drawnCard = None
        elif instruction.type == 'd':
            if not self.stacks:
                drawnCard = self.draw(currentPlayer, 1)[0]
                if self.check_play(drawnCard):
                    self.drawnCard = drawnCard
                    return "cp"
            else:
                self.draw(currentPlayer, self.stacks, skip=False)
                self.stacks = 0
                self.stackingValue = None
        elif instruction.type == 'p':
            card = instruction.playCard
            if self.check_play(card):
                card = currentPlayer.get_card(card)
                self.play(card, instruction.colorChosen)
            else:
                return "np"
        elif instruction.type == 'e':
            return "ie"
        else:
            return "ut"

        if instruction.uno and len(currentPlayer) == 1:
            currentPlayer.saidUno = True
        elif instruction.uno:
            return "ne"
        self.update_turn()

    def new_game(self):
        # shuffle original seed and players
        seedList = list(self.seed)
        rand.seed(self.seed)
        rand.shuffle(seedList)
        self.seed = ''.join(seedList)
        rand.seed(self.seed)
        rand.shuffle(self.players)
        self.__init__(self.playerNames, self.seed, players=self.players, winningPoints=self.winningPoints,
                      decks=self.decks)
        self.start_game()
