"""
inputs:
play <color> <value> |color|
challenge
draw card
^^ if playable ^^
yes
no
yes |color|
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
values = {"0": "zero",  # 0
          "1": "one",
          "2": "two",
          "3": "three",
          "4": "four",
          "5": "five",
          "6": "six",
          "7": "seven",
          "8": "eight",
          "9": "nine",  # 9
          "r": "reverse",
          "s": "skip",
          "+2": "+two",  # 12
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
    def __init__(self):
        self.deck = []
        self.init_deck()

    def init_deck(self):
        colorList = list(colors.keys())[:4]
        black = list(colors.keys())[-1]
        valuesList = list(values.keys())
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
    def __init__(self, name, hand):
        self.name = name
        self.hand = hand
        self.points = 0
        self.saidUno = False

    def get_card(self, card):
        try:
            i, card = find_card(self.hand, card)
        except TypeError:
            return f"{card} not found"
        if card:
            self.hand.pop(i)
        return card

    def add_card(self, card):
        self.hand.append(card)

    def get_hand_points(self):
        points = 0
        for card in self.hand:
            points += valuePoints[card.value]
        return points

    def full_reset(self, name, hand):
        self.__init__(name, hand)

    def __repr__(self):
        return f"{self.name}: {', '.join([f'{colors[c.color]} {values[c.value]}' for c in self.hand])}"


def find_card(deck, card):
    for i, deckCard in enumerate(deck):
        if (deckCard.color == card.color) and (deckCard.value == card.value):
            return i, card
    return None


def check_players(players):
    numPlayers = len(players)
    if numPlayers < 2 or numPlayers > 10:
        raise ValueError('{numPlayers} player/s exceed the rules of uno'.format(numPlayers=repr(numPlayers)))


def text_to_card(cardList):
    try:
        colorsValues = list(colors.values())
        valuesValues = list(values.values())
        color = cardList[0]
        value = cardList[1]
        if color in colorsValues:
            color = colorsFlipped[color]
        if value in valuesValues:
            value = valuesFlipped[value]
        return Card(color, value)
    except KeyError:
        # if wrong card return 1
        return f"No such card as {' '.join(cardList)}"


class UnoGame:
    def __init__(self, playerNames, seed):
        check_players(playerNames)
        self.playerNames = playerNames
        self.seed = seed
        self.playersList = self.playerNames
        self.players = []
        self.numPlayers = len(playerNames)
        self.startingNumberOfCards = 7
        self.winningPoints = 500

        self.drawPile = DrawPile()
        self.discardPile = DiscardPile()
        self.clockwise = True
        self.toSkip = False  # for skip
        self.currentPlayerIndex = -1
        self.previousPlayerIndex = None
        self.previousTwoPlayerIndex = None
        self.winner = None
        self.finalWinner = None
        self.drawnCard = None

    def start_game(self):
        # gives the players the feel of shuffling the deck
        self.drawPile.shuffle(self.seed)

        # if there are no pre-existing players then create the players
        # seed is used to ensure a different deck is shuffled everytime
        if not self.players:
            # players are initialized
            for player in self.playersList:
                # seven cards are dealt to each player
                playerHand = [self.drawPile.get_card() for i in range(self.startingNumberOfCards)]
                self.players.append(Player(player, playerHand))
        else:
            # shuffle original seed
            rand.shuffle(self.seed)
            rand.seed(self.seed)

            # shuffle players
            rand.shuffle(self.players)
            # new cards are being dealt to players
            for player in self.players:
                player.hand = [self.drawPile.get_card() for i in range(self.startingNumberOfCards)]

        # a card is picked from the draw pile and is played to first player
        self.play(self.drawPile.get_card())
        self.update_turn()

    def turn(self, playerInput):
        playerInput = playerInput.lower().split()
        currentPlayer = self.players[self.currentPlayerIndex]
        if playerInput[0] == "challenge":
            # -1 if unsuccessful and None if correct
            return self.challenge()
        if playerInput[0] in ["yes", "no"] and self.drawnCard:
            # create new if else to parse for yes and no
            if playerInput[0] == "yes":
                colorChosen = None
                if self.drawnCard.color == 'bk' and len(playerInput) > 1:
                    colorChosen = playerInput[1]
                else:
                    return f"Color was not specified"
                card = currentPlayer.get_card(self.drawnCard)
                self.drawnCard = None
                self.play(card, colorChosen)
            elif playerInput[0] == "no":
                self.drawnCard = None
            self.update_turn()
        elif playerInput == ["draw", "card"]:
            # yes and no also pulls a new card
            self.draw(currentPlayer, 1)
            drawnCard = currentPlayer.hand[-1]
            # if drawn card is playable then let the player choose to play it or not
            if self.check_play(drawnCard):
                self.drawnCard = drawnCard
                return f"card playable"
            self.update_turn()
        elif playerInput[0] == "play":
            inputList = playerInput[1:]
            card = text_to_card(inputList[:2])
            if self.check_play(card):
                card = currentPlayer.get_card(card)
                if type(card) == str:
                    if card[-9:] == "not found":
                        return card

                def uno_check(currentPlayer):
                    if len(currentPlayer.hand) == 1:
                        currentPlayer.saidUno = True
                        return True
                    else:
                        return f"{currentPlayer.name} has more than one card."

                colorChosen = None
                if len(inputList) == 4:
                    colorChosen = inputList[2]
                    unoCheck = uno_check(currentPlayer)
                    if unoCheck is not True:
                        return unoCheck
                elif len(inputList) == 3:
                    if inputList[2] == "uno":
                        unoCheck = uno_check(currentPlayer)
                        if unoCheck is not True:
                            return unoCheck
                    else:
                        colorChosen = inputList[2]
                self.play(card, colorChosen=colorChosen)
                self.update_turn()
            else:
                return f"{card} not playable."
        else:
            return f"{playerInput} is an invalid input."

    def reverse(self):
        if self.numPlayers > 2:
            self.players = self.players[::-1]
        else:
            self.skip()
        self.clockwise = not self.clockwise

    def skip(self):
        # checks for this in update next turn
        self.toSkip = True

    def draw(self, player, numberOfCards, challenge=False):
        self.check_deck(numberOfCards)
        for i in range(numberOfCards):
            player.add_card(self.drawPile.get_card())
        if player.saidUno and len(player.hand) > 1:
            player.saidUno = not player.saidUno
        if numberOfCards > 1 and not challenge:
            self.skip()

    def challenge(self):
        previousPlayer = self.players[self.previousPlayerIndex]
        if not previousPlayer.saidUno and len(previousPlayer.hand) == 1:
            previousPlayer.saidUno = True
            self.draw(previousPlayer, 2, challenge=True)

            def ownership(name):
                return '' if name[-1].lower() == 's' else 's'

            return f"{previousPlayer.name} got added 2 cards penalty, for not calling uno."
        return f"Challenge unsuccessful"

    def check_deck(self, numberOfCards):
        # if draw pile is empty(negative) then use discard pile as the new draw pile
        if (len(self.drawPile.deck) - numberOfCards) < 0:
            seedList = list(self.seed)
            rand.shuffle(seedList)
            self.seed = ''.join(seedList)
            self.drawPile.deck = self.discardPile.deck[:-1]
            self.discardPile.reset()
            self.drawPile.shuffle(self.seed)

    def check_play(self, cardPlayed):
        topCard = self.discardPile.top_card()
        # if top card black or card played black then its okay
        # this is done because in "or" logic the first argument is always checked and if it is true it proceeds
        if topCard.color == 'bk' or cardPlayed.color == 'bk':
            return True
        else:
            return topCard.color == cardPlayed.color or topCard.value == cardPlayed.value

    def get_next_player(self):
        currentPlayerIndex = self.currentPlayerIndex
        currentPlayerIndex += 1
        if currentPlayerIndex == self.numPlayers:
            currentPlayerIndex = 0
        return currentPlayerIndex

    def play(self, cardPlayed, colorChosen=None):
        if cardPlayed.value == 'r':
            self.reverse()
        elif cardPlayed.value == 's':
            self.skip()
        elif cardPlayed.value == '+2':
            self.draw(self.players[self.get_next_player()], 2)
        elif cardPlayed.value == '+4':
            self.draw(self.players[self.get_next_player()], 4)
            cardPlayed.color = colorChosen
        elif cardPlayed.value == 'w':
            cardPlayed.color = colorChosen
        self.discardPile.add_card(cardPlayed)
        self.check_winner()

    def check_winner(self):
        # if previous player who placed a card is winner
        if not self.players[self.currentPlayerIndex].hand:
            winnerPlayer = self.players[self.currentPlayerIndex]
            # get total points from current game
            points = 0
            for i in range(self.numPlayers):
                if i != self.currentPlayerIndex:
                    points += self.players[i].get_hand_points()
            winnerPlayer.points += points
            # if winner has greater than 500 points then he has won the game and game stops
            if winnerPlayer.points >= self.winningPoints:
                self.finalWinner = winnerPlayer
            else:
                self.winner = winnerPlayer

    def update_turn(self):
        self.previousTwoPlayerIndex = self.previousPlayerIndex
        self.previousPlayerIndex = self.currentPlayerIndex
        self.currentPlayerIndex = self.get_next_player()
        # if skip then update again
        if self.toSkip:
            self.toSkip = False
            self.currentPlayerIndex = self.get_next_player()
        # if two players ago is in uno but did not callout it will be set to true
        if self.previousTwoPlayerIndex and (len(self.players[self.previousTwoPlayerIndex].hand) == 1):
            self.players[self.previousTwoPlayerIndex].saidUno = True


# uno = UnoGame(["Player1", "Player2"], "1234")
# uno.start_game()
# print(f"Discard Pile: {uno.discardPile.top_card()}")
# while not uno.winner:
#     print(uno.players[uno.currentPlayerIndex])
#     turn = input("Turn: ")
#     turn = uno.turn(turn)
#     if turn is not None:
#         print(turn)
#     print('=' * 119)
#     print(f"Discard Pile: {uno.discardPile.top_card()}")
#
# print(uno.winner)
