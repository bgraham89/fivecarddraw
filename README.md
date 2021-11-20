# fivecarddraw
A five card draw (poker variant) game engine.

# How to use
```from fivecarddraw import FiveCardDraw, Simulation```

```FiveCardDraw()``` This begins a game of five card draw for 1-player and 4 different ai.

```Simulation()``` This spectates 5 different ai play a game of five card draw poker.

# About the Classes

Essentially Table() is a hub of game-related information, including a collection of Player()'s (Human() or BasicAI()) and a Deck() of Card()'s.

Dealer() expands upon the information, and adds the game-related functions. More information can be found in the notebooks.

# About the Hand Evaluator

The Dealer.EvaluateHands() method is an intepretation of "Cactus Kev's Poker Hand Evaluator".

The evaluator makes use of the binary encoding of Card()'s using Card.MASK. (More details of the formula can be found here: http://suffe.cool/poker/evaluator.html)

The evaluator also makes use Dealer.FLUSH_LOOKUP, Dealer.UNIQUE_FIVE_LOOKUP, and Dealer.DUPE_LOOKUP which are hand rank memos.

The memos are populated from tables stored in the flush_lookup.txt, unique_five_lookup.txt and dupe_lookup.txt files, scraped from here: http://suffe.cool/poker/7462.html.

# About the UI

FiveCardDraw() uses a text-based (console) UI.

# About the AI

The BasicAI() class is the most basic ai possible for a poker engine, making decisions randomly.

# License

This project is licensed under the MIT License - see the LICENSE.md file for details
