import unittest
from fivecarddraw import Card

class CardTest(unittest.TestCase):
    def setUp(self):
        # create implicit deck of cards
        self.cards = [Card(i, j) for i in range(13) for j in range(4)]
        

    def testRepresentation(self):
        # create all cards as strings
        strs = [
            "2♠", "2♡", "2♢", "2♣", "3♠", "3♡", "3♢", "3♣", "4♠", "4♡", "4♢", "4♣",
            "5♠", "5♡", "5♢", "5♣", "6♠", "6♡", "6♢", "6♣", "7♠", "7♡", "7♢", "7♣",
            "8♠", "8♡", "8♢", "8♣", "9♠", "9♡", "9♢", "9♣", "10♠", "10♡", "10♢", "10♣",
            "J♠", "J♡", "J♢", "J♣", "Q♠", "Q♡", "Q♢", "Q♣", "K♠", "K♡", "K♢", "K♣",
            "A♠", "A♡", "A♢", "A♣"]
        # check each card has correct string representation
        self.assertEqual(list(map(lambda x : str(x), self.cards)) , strs)


    def testEncoding(self):
        # create all cards as integers
        ints = [
            69634, 73730, 81922, 98306, 135427, 139523, 147715, 164099, 
            266757, 270853, 279045, 295429, 529159, 533255, 541447, 557831, 
            1053707, 1057803, 1065995, 1082379, 2102541, 2106637, 2114829, 2131213, 
            4199953, 4204049, 4212241, 4228625, 8394515, 8398611, 8406803, 8423187, 
            16783383, 16787479, 16795671, 16812055, 33560861, 33564957, 33573149, 33589533, 
            67115551, 67119647, 67127839, 67144223, 134224677, 134228773, 134236965, 134253349, 
            268442665, 268446761, 268454953, 268471337]
        # check each card has correct int representation
        self.assertEqual(list(map(lambda x : int(x), self.cards)) , ints)


    def testEquivalence(self):
        for i in range(13):
            for j in range(4):
                # calculate duplicate
                index = i * 4 + j
                duplicate = Card(i, j)
                # check each card is equal to a duplicate version
                self.assertEqual(self.cards[index], duplicate)

if __name__ == "__main__":
    unittest.main()