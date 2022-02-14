from uno_game import UnoGame, PlayerInstruction
# winning_moves = ["p yw 9", "p yw 0", "d", "p yw 4", "d", 'n', "p yw 5", "d", "p yw 9", "d", "p gn 9",
#                  "p gn 1", "p be 1", "p be 2", "p be 5"]  # seed is 1234
winning_moves = ["p yw 9", "p yw 0", "d", "p yw 4", "d", 'n', "p yw 5", "d", "p yw 9", "d", "p gn 9",
                 "p gn 1"]  # seed is 1234
# stacking_moves = ["p rd r", 'd', "p rd 3", "p bk w yw", "p yw +2"]  # seed is '' or None
uno = UnoGame(["Player 1", "Player 2"], "1234")
uno.start_game()
for move in winning_moves:
    uno.turn(PlayerInstruction(move))
while not uno.finalWinner:
    while not uno.winner:
        print('=' * 119)
        print(f"Discard Pile: {uno.discardPile.top_card()}\t\t\tStacks: {uno.stacks}")
        print(uno.players[uno.currentPlayerIndex])
        turn = PlayerInstruction(input("Turn: "))
        turn = uno.turn(turn)
        if turn is not None:
            print(turn)
    print(f"Winner is {uno.winner.name}")
    for player in uno.players:
        print(f"{player.name} Points: {player.points}")
    uno.new_game()
