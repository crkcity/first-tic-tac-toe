# we need to import json for json.dumps
 import json
 from django.shortcuts import render
 from django.http import HttpResponse
 # we were getting 403 when requesting this view so we're trying to make it csrf exempt
 from django.views.decorators.csrf import csrf_exempt
 from django.views.decorators.csrf import ensure_csrf_cookie

 # on PythonAnywhere (not on localhost) our csrf-token was null
 # so we had to force our main view to set the cookie via this decorator
 @ensure_csrf_cookie
 def play_game(request):
     """ a view-function initiating the main page """
     return render(request, 'tic_tac_AI/play_game.html', {})

 def AI_moves(request):
     """ a view-function grabbing and sending ajax/json board states"""
     if request.method == 'POST':

         # grab all the ajax/json data from script.js
         # we have to use getlist instead of get with arrays->lists,
         # otherwise it just grabbed one element (last one) from the array
         received_board = request.POST.getlist('board[]')
         ai_token = request.POST.get('AI_TOKEN')
         # have to explicitly convert the string we got from ajax/json to a Python integer
         depth_now = int(request.POST.get('DEPTH_NOW'))
         game_over = request.POST.get('GAME OVER')

         # initiate a dictionary holding the json response
         response_data = {}

         # plug in AI backend
         ###############################################
         ###############################################

         # tic_tac_1.5.py (Django View version)
         # by Mjure
         # 2016 09 22

         # plays a perfect game of tic tac toe against a human opponent
         # inspired by http://neverstopbuilding.com/minimax (salutations to them!)

         # the AI uses a strategy called "minimax algorithm" and bears in
         # mind the number of turns left, preferring to win quick and lose late

         # define the global, recursive minimax algorithm
         def minimax(player, game):
             """ This is the minimax calculation which will be called
             by the AI player object's move() method """

             # if the game is over, return the score from AI's perspective,
             # taking number of turns already taken (aka depth) into consideration
             # end condition of the recursion
             if game.is_over():
                 # we need to pass an empty string here because minimax is expected
                 # to return the Ai-considered board state
                 empty_string = ""
                 return game.minimax_score(player), empty_string

             # create lists holding possible moves and their scores
             scores = []
             moves = []

             # consider each possible game state within each next
             # legal move and run minimax on it
             for move in game.legal_moves():

                 # create a new, potential board as a copy of the current game's board
                 # the [:] is important - otherwise we won't use a copy
                 # of the original game's board but the actual board
                 potential_board = game.board[:]
                 # add the token (X or O) of the current player onto that tile
                 potential_board[move] = game.active_player.token
                 # create a new game, passing it that potential board and incrementing
                 # the depth by 10 to show that a turn has passed
                 potential_game = Game(
                     game.player_one, game.player_two,
                     potential_board, game.depth + 10)

                 # switch potential game's active player attribute to be the opposite
                 # of the current game's active player (since we already took his turn for him/her)
                 if game.active_player == game.player_one:
                     potential_game.active_player = potential_game.player_two
                 elif game.active_player == game.player_two:
                     potential_game.active_player = potential_game.player_one
                 else:
                     print("\nError while switching potential game's active player\n")
                 # recursion
                 # add the minimax value of that game to the scores list
                 # and grab the easy to read string representation
                 # of the board that will be returned by minimax
                 score_to_append, readable_board = minimax(player, potential_game)
                 scores.append(score_to_append)
                 # add the currently considered move to the moves list,
                 # at the same index as the corresponding score
                 moves.append(move)

             # depending on whether it's the human or the AI making the current choice
             # of move, return the lowest or highest score from the scores list
             # store the chosen move in AI player's AI_chosen_move attribute

             # if the active player is human, choose the worst scoring move and return its score
             if game.active_player != player:
                 # for the human the best option is the one with the lowest
                 # score (worst choice from the perspective of the AI)
                 worst_choice = min(scores)
                 # find the index of that item
                 worst_choice_index = scores.index(worst_choice)
                 # find the corresponding move by the index
                 # and assign it to the choice that AI will assume a human would make
                 player.AI_chosen_move = moves[worst_choice_index]
                 # create a version of the currently considered
                 # board showing the scores for each untaken tile
                 considered_board = game.board[:]
                 for idx, move in enumerate(moves):
                     considered_board[move] = scores[idx]
                 # return the lowest score
                 return scores[worst_choice_index], considered_board

             # if the active player is the computer
             # choose the highest scoring move and return its score
             elif game.active_player == player:
                 # for the AI the best option is the one with the highest score
                 best_choice = max(scores)
                 # find the index of the highest score
                 best_choice_index = scores.index(best_choice)
                 # find the highest-scoring move and assign it
                 # to the AI player's AI_chosen_move attribute
                 player.AI_chosen_move = moves[best_choice_index]
                 # board showing the scores for each untaken tile
                 considered_board = game.board[:]
                 for idx, move in enumerate(moves):
                     considered_board[move] = scores[idx]
                 # return the lowest score
                 return scores[best_choice_index], considered_board

         # initialize global, constant variables:
         # for tile values
         X = "X"
         O = "O"
         EMPTY = " "

         # for board size
         NUM_SQUARES = 9

         # for ways to win
         WAYS_TO_WIN = (
             (0, 1, 2),
             (3, 4, 5),
             (6, 7, 8),
             (0, 3, 6),
             (1, 4, 7),
             (2, 5, 8),
             (0, 4, 8),
             (2, 4, 6))

         # initialize an empty board
         EMPTY_BOARD = []
         for i in range(NUM_SQUARES):
             EMPTY_BOARD.append(EMPTY)

         # define player object classes
         class HumanPlayer(object):
             """ deprecated human player class"""
             def __init__(self, token):
                 self.token = token

         class ComputerPlayer(object):
             """ an AI player in a game of tic-tac-toe """
             def __init__(self, token):
                 self.token = token
                 # in this property we'll be storing the move (0-8) aka tile number,
                 # which the AI will chose via the minimax function
                 self.AI_chosen_move = None

             # define the minimax calculation defining the AI's next move
             def move(self, game):
                 """ use minimax function to return AI's next move (chosen tile) """
                 # run the minimax calculation passing the player object and the current game
                 # we no longer use the returned move separately,
                 # we just change the self.AI_chosen_move within minimax
                 # and for the what-ai-thought feature we change the game's
                 # considered_board property
                 the_move, game.considered_board = minimax(self, game)
                 # return the global variable AI_chosen_move,
                 # whose value will be changed by the minimax() function
                 return self.AI_chosen_move

         # define game object class
         class Game(object):
             """ a game of tic tac toe, with 2 players and a board """
             def __init__(self, player_one, player_two, board, depth):
                 self.player_one = player_one
                 self.player_two = player_two
                 self.board = board
                 # we need to be able to define the number of turns already taken (depth)
                 # here because in the minimax algorithm we create potential games
                 # with some moves already taken
                 self.depth = depth
                 # added a game property of "considered_board"
                 # which will hold a visualisation of the board
                 # from AI's perspective (filled with z's for debugging)
                 self.considered_board = ['z','z','z']

                 # since we only play the AI turn, the computer is always the active player
                 # which is always going to be player 1
                 if player_one.token == X:
                     self.active_player = player_one
                 elif player_two.token == X:
                     self.active_player = player_two
                 else:
                     print("\nError while setting active player, when initializing the game\n")

             # define a method to check if a given player has won the game
             def has_won(self, player):
                 """ Find out if the player passed as argument is the winner, return Boolean value"""
+                # optimized version of this key runtime swallowing function (after cProfile with pstats analysis)
                 checked_token = player.token
                 for sequence in WAYS_TO_WIN:
                     if checked_token == self.board[sequence[0]] == self.board[sequence[1]] == \
                                         self.board[sequence[2]]:
                         return True
                 return False

             # define a method for checking if the game is over
             # (either player wins or it's a tie)
             def is_over(self):
                 """ Find out if the game is over, return True or False"""
                 if self.has_won(self.player_one):
                     return True
                 elif self.has_won(self.player_two):
                     return True
                 elif EMPTY not in self.board:
                     return True
                 else:
                     return False

             # define a method that returns a list of all available moves left
             def legal_moves(self):
                 """Create a list of legal moves."""
