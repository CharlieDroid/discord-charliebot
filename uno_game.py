"""
Unimplemented:
-Cannot play wild cards anytime
-Play the color chosen for a wild card
-Reset deck if draw pile is empty
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
        # full name is rd0, yw1, ...
        self.fullName = color + value
        # readable name is red zero, yellow one
        self.readableName = colors[color] + ' ' + values[value]

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

        # initialize zero cards
        for color in colorList:
            self.deck.append(Card(color, valuesList[0]))

        # initialize number cards
        for i in range(2):
            for color in colorList:
                for value in valuesList[1:10]:
                    self.deck.append(Card(color, value))

        # initialize action cards that are non-black
        for i in range(2):
            for color in colorList:
                for value in valuesList[10:13]:
                    self.deck.append(Card(color, value))

        # initialize wild cards
        for i in range(4):
            for value in valuesList[-2:]:
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
        self.topCard = None

    def top_card(self):
        self.topCard = self.deck[-1]
        return self.topCard

    def add_card(self, card):
        self.deck.append(card)

    def reset(self):
        self.__init__()


class Player:
    def __init__(self, name, hand):
        self.name = name
        self.hand = hand
        self.points = 0
        self.unoCallOut = False

    # for __repr__ for readability when printing
    def get_readable_hand(self):
        return [card.readableName for card in self.hand]

    def get_card(self, card):
        # find index of card and get the element from the list of cards
        try:
            card = self.hand[index_card(self.hand, card)]
            self.hand.remove(card)
            return card
        except (TypeError, AttributeError):
            return -1

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
        return f"{self.name}: {', '.join(self.get_readable_hand())}"


def index_card(listCards, card):
    for i in range(len(listCards)):
        if listCards[i].fullName == card.fullName:
            return i
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
        return -1


class UnoGame:
    def __init__(self, playerNames, seed, resetGame=True):
        self.toSkip = False  # for skip
        self.clockwise = True  # for reverse card
        self.winner = False
        self.previousTwoPlayerIndex = None
        self.previousPlayerIndex = None
        self.currentPlayerIndex = -1
        if resetGame:
            self.playerNames = playerNames
            self.finalWinner = False
            self.drawPile = DrawPile()
            self.discardPile = DiscardPile()
            self.startingNumberOfCards = 7
            check_players(playerNames)
            self.playersList = playerNames
            self.seed = seed
            self.players = []
            self.numPlayers = len(playerNames)

    def reverse(self):
        if self.numPlayers > 2:
            self.clockwise = not self.clockwise
        else:
            self.skip()

    def skip(self):
        # skip one turn
        self.toSkip = True

    def draw(self, player, numberOfCards, challenge=False):
        for i in range(numberOfCards):
            player.add_card(self.drawPile.get_card())
        if numberOfCards > 1 and not challenge:
            self.skip()

    def challenge(self):
        previousPlayer = self.players[self.previousPlayerIndex]
        if not previousPlayer.unoCallOut:
            previousPlayer.unoCallOut = True
            return self.draw(previousPlayer, 2)
        return -1

    def check_play(self, cardPlayed):
        topCard = self.discardPile.top_card()
        # if top card black or card played black then any color
        if topCard.color != "bk" or cardPlayed.color != "bk":
            return topCard.color == cardPlayed.color or topCard.value == cardPlayed.value
        return True

    def get_next_player(self):
        currentPlayerIndex = self.currentPlayerIndex
        if self.clockwise:
            currentPlayerIndex += 1
        else:
            currentPlayerIndex -= 1

        if currentPlayerIndex >= self.numPlayers:
            currentPlayerIndex = 0
        elif currentPlayerIndex < 0:
            currentPlayerIndex = self.numPlayers - 1
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
            if winnerPlayer.points >= 500:
                self.finalWinner = True
                return winnerPlayer
            self.winner = winnerPlayer

    def update_next_turn(self):
        self.previousTwoPlayerIndex = self.previousPlayerIndex
        self.previousPlayerIndex = self.currentPlayerIndex
        self.currentPlayerIndex = self.get_next_player()
        # if two players ago is in uno but did not callout it will be set to true
        if self.previousTwoPlayerIndex and (len(self.players[self.previousTwoPlayerIndex].hand) == 1):
            self.players[self.previousTwoPlayerIndex].unoCallOut = True
        # if skip then update again
        if self.toSkip:
            self.toSkip = False
            self.update_next_turn()

    def input_parser(self, playerInput):
        # returns the drawn card, if challenge was not successful then -1, or playerInput
        playerInput = playerInput.lower()
        currentPlayer = self.players[self.currentPlayerIndex]
        if playerInput == "draw card":
            self.draw(currentPlayer, 1)
            return ['dc', currentPlayer.hand[-1]]
        elif playerInput == "challenge":
            return ['ch', self.challenge()]
        else:
            # turn player input in to a list
            playerInputList = playerInput.split()
            try:
                if playerInputList[2] == "uno" and len(currentPlayer.hand) == 2:
                    currentPlayer.unoCallOut = True
                else:
                    return -1
            except IndexError:
                pass
            return ['pc', currentPlayer.get_card(text_to_card(playerInputList[:2]))]

    def start_game(self):
        # if there are no preexisting players then create the players
        if not self.players:
            # seed is used to ensure a different deck is shuffled everytime
            # it also gives the players the feel of shuffling the deck
            self.drawPile.shuffle(self.seed)
            # players are initialized
            for player in self.playersList:
                # seven cards are dealt to each player
                playerHand = [self.drawPile.get_card() for i in range(self.startingNumberOfCards)]
                self.players.append(Player(player, playerHand))
        else:
            # shuffle original seed
            rand.shuffle(self.seed)
            rand.seed(self.seed)

            # shuffle deck and/or player orders
            self.drawPile.shuffle(self.seed)
            # rand.shuffle(self.players)
            # new cards are being dealt to players
            for player in self.players:
                player.hand = [self.drawPile.get_card() for i in range(self.startingNumberOfCards)]

        # a card is picked from the draw pile and is played to first player
        self.play(self.drawPile.get_card(), "bk")
        self.update_next_turn()

    def turn(self, playerInput):
        parsedInput = self.input_parser(playerInput)
        # ['dc', drawnCard], ['ch', -1(not successful) or None(successful)], ['pc', play card]
        if parsedInput[0] == 'ch':
            if not parsedInput:
                return "Challenge Successful"
            return "Challenge Unsuccessful"

        elif parsedInput[0] == 'dc':
            # if drawn card is playable then let the player choose to play it or not
            if self.check_play(parsedInput[1]):
                currentPlayer = self.players[self.currentPlayerIndex]
                card = currentPlayer.get_card(currentPlayer.hand[-1])
                if input(f"Play {card}? ").lower() == "yes":
                    self.play(card)
            self.update_next_turn()

        elif parsedInput[0] == 'pc' and parsedInput[1] != -1:
            card = parsedInput[1]
            if self.check_play(card):
                self.play(card)
                self.update_next_turn()

        # -1 is returned if something is wrong
        return -1

    def reset(self, resetAll=False):
        if resetAll:
            self.__init__(self.playerNames, self.seed, resetGame=True)
        else:
            self.drawPile.reset()
            self.discardPile.reset()
            self.__init__(self.playerNames, self.seed, resetGame=False)


uno = UnoGame(["Danica", "Charles", "Xavier", "Julian"], "1234")
# danica_win_turns = ['yw 9', 'gn 9', 'gn 1', 'draw card', 'gn 3', 'be 3', 'be s', 'be s', 'draw card',
#                     'be 5', 'draw card', 'yw 5', 'yw r', 'rd r', 'rd +2', 'rd +2']
uno.start_game()
# for turn in danica_win_turns:
#     uno.turn(turn)
print(f"Discard Pile: {uno.discardPile.top_card()}")
while not uno.winner:
    print(uno.players[uno.currentPlayerIndex])
    turn = input("Turn: ")
    uno.turn(turn)
    print('=' * 119)
    print(f"Discard Pile: {uno.discardPile.top_card()}")

print(uno.winner.points)
