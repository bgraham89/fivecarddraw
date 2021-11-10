# fivecarddraw
A five card draw (poker variant) engine 

# How to use
from fivecarddraw import FiveCardDraw, Simulation

FiveCardDraw() begins a 1 player game of five card draw poker vs 4 ai.
Simulation() spectates 5 ai play a game of five card draw poker.

# About the engine

Essentially Table() is a hub of game-related information, including a collection of Player()'s (Human() or BasicAI()) and a Deck() of Card()'s.
Dealer() expands upon the information, and adds the game-related functions. 
The Dealer.EvaluateHands() method is an intepretation of "Cactus Kev's Poker Hand Evaluator".
The evaluator makes use of the binary encoding of Card()'s using Card.MASK. (More details of the formula can be found here: http://suffe.cool/poker/evaluator.html)
The evaluator also makes use Dealer.FLUSH_LOOKUP, Dealer.UNIQUE_FIVE_LOOKUP, and Dealer.DUPE_LOOKUP which are hand rank memos.
The memos are populated from tables stored in the flush_lookup.txt, unique_five_lookup.txt and dupe_lookup.txt files, scraped from here: http://suffe.cool/poker/7462.html.
FiveCardDraw() uses a text-based (console) UI.
The BasicAI() class is the most basic ai possible for a poker engine, making decisions randomly.
