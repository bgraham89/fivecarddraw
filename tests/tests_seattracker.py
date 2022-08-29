import unittest
from fivecarddraw import SeatTracker

class SeatTrackerTest(unittest.TestCase):
    def setUp(self):
        self.tracker = SeatTracker()

    def testSeatOccupying(self):
        # check number of occupied seats is correct
        self.assertFalse(self.tracker.OccupiedSeats())
        # check number of empty seats is correct
        self.assertEqual(len(self.tracker.AvailableSeats()), len(self.tracker)) 

        # fill all seats
        for i in range(len(self.tracker)):
            name = f"{i}"
            self.tracker.OccupySeat(name, i)
            # check seat is occupied
            self.assertTrue(self.tracker.seats[i])
            # check name is string
            self.assertIsInstance(self.tracker.seats[i], str)
            # check seat is occupied by correct player
            self.assertEqual(self.tracker.seats[i], name)
            # check number of occupied seats is correct
            self.assertEqual(len(self.tracker.OccupiedSeats()), i+1)
            # check number of empty seats is correct
            self.assertEqual(len(self.tracker.AvailableSeats()), len(self.tracker)-i-1)

        # check table has seating limit
        self.assertRaises(IndexError, self.tracker.OccupySeat, name=f"{len(self.tracker)+1}", seat=len(self.tracker)+1)  

        # Empty all seats
        for i in range(len(self.tracker)):
            name = f"{i}"
            self.tracker.EmptySeat(i)
            # check seat is occupied
            self.assertFalse(self.tracker.seats[i])
            # check number of occupied seats is correct
            self.assertEqual(len(self.tracker.OccupiedSeats()), len(self.tracker)-i-1)
            # check number of empty seats is correct
            self.assertEqual(len(self.tracker.AvailableSeats()), i+1)

        # check player can't be double seated
        self.tracker.OccupySeat("1", 1)
        self.assertRaises(Exception, self.tracker.OccupySeat, name="1", seat=2)
        # check seat can't be used if already occupied
        self.assertRaises(Exception, self.tracker.OccupySeat, name="2", seat=1)
        # check seat can't be emptied if already emptied
        self.assertRaises(Exception, self.tracker.EmptySeat, seat=2)
        # check seat can't be emptied if not at table
        self.assertRaises(IndexError, self.tracker.EmptySeat, seat=6)


    def testPlayerTracking(self):
        # untrack all players at a time
        for i in range(len(self.tracker)):
            # different amounts of players to track
            names = [f"{j}" for j in range(i+1)]
            self.tracker.TrackPlayers(names)
            # check correct amount of players tracked
            self.assertEqual(len(self.tracker.TrackedPlayers()), len(names))
            # check correct hash of players tracked
            self.assertEqual(set(names), set(self.tracker.TrackedPlayers()))
            # check all players are forgotten
            self.tracker.UntrackPlayers(names)
            self.assertEqual(len(self.tracker.TrackedPlayers()), 0)

        # untrack one player at a time
        for i in range(len(self.tracker)):
            # different amounts of players to track
            names = [f"{j}" for j in range(i+1)]
            self.tracker.TrackPlayers(names)
            num_tracked = len(self.tracker.TrackedPlayers())
            # individual players
            for name in names:
                # check player is not seated
                self.assertNotIsInstance(self.tracker.players[name], int)
                # untrack player
                self.tracker.UntrackPlayers(name)
                # check player no longer tracked
                self.assertNotIn(name, self.tracker.TrackedPlayers())
                # check only one player is forgotten
                num_tracked -= 1
                self.assertEqual(len(self.tracker.TrackedPlayers()), num_tracked)
            # check all players are forgotten
            self.assertEqual(num_tracked, 0)

    def testPlayerSeating(self):
        # try seating different amount of players
        for _ in range(len(self.tracker)):
            names = [f"{j}" for j in range(len(self.tracker))]
            self.tracker.TrackPlayers(names)
            self.tracker.SeatPlayers()
            # check number of occupied seats is correct
            self.assertEqual(len(self.tracker.OccupiedSeats()), len(names))
            # check number of empty seats is correct
            self.assertEqual(len(self.tracker.AvailableSeats()), len(self.tracker)-len(names))
            # check correct hash of players tracked
            self.assertEqual(set(names), set(self.tracker.TrackedPlayers()))
            # check player tracker
            for name in self.tracker.TrackedPlayers():
                # check player seat is integer
                self.assertIsInstance(self.tracker.players[name], int)
                # check seat and player trackers are in agreement
                self.assertEqual(self.tracker.players[name], self.tracker.seats.index(name))
            self.tracker.KickPlayers(names)
            # check no tracked players
            self.assertFalse(self.tracker.TrackedPlayers())
            # check all seats are available
            self.assertEqual(len(self.tracker.AvailableSeats()), len(self.tracker))

    def testButtonTracking(self):
        # check button seat is integer
        self.assertIsInstance(self.tracker.button["seat"], int)
        # check button player is string
        self.assertIsInstance(self.tracker.button["player"], str)
        # check button is given to players when possible
        names = [f"{j}" for j in range(len(self.tracker)-2)]
        self.tracker.TrackPlayers(names)
        self.tracker.SeatPlayers()
        # try move button 100 times
        next_seat = self.tracker.OccupiedSeats()[0]
        for i in range(100):
            self.tracker.MoveButton()
            # check button seat is integer
            self.assertIsInstance(self.tracker.button["seat"], int)
            # check button player is string
            self.assertIsInstance(self.tracker.button["player"], str)
            # check button player is seated at button seat
            self.assertEqual(self.tracker.button["player"], self.tracker.seats[self.tracker.button["seat"]])
            # check button seat is allocated to button player
            self.assertEqual(self.tracker.players[self.tracker.button["player"]], self.tracker.button["seat"])
            # check button player is tracked
            self.assertIn(self.tracker.button["player"], self.tracker.TrackedPlayers())
            # check button seat is occupied
            self.assertIn(self.tracker.button["seat"], self.tracker.OccupiedSeats())
            # check button was moved to correct seat
            self.assertEqual(self.tracker.button["seat"], next_seat)
            next_seat = self.tracker.OccupiedSeats()[(i + 1) % len(names)]


        self.tracker.KickPlayers(names)
        # try move button 100 more times
        next_seat = self.tracker.AvailableSeats()[(self.tracker.button["seat"] + 1) % len(self.tracker)]
        for _ in range(100):
            self.tracker.MoveButton()
            # check button seat is integer
            self.assertIsInstance(self.tracker.button["seat"], int)
            # check button player is string
            self.assertIsInstance(self.tracker.button["player"], str)
            # check no button player
            self.assertFalse(self.tracker.button["player"])
            # check button seat is avaiable
            self.assertIn(self.tracker.button["seat"], self.tracker.AvailableSeats())
            # check button was moved to correct seat
            self.assertEqual(self.tracker.button["seat"], next_seat)
            next_seat += 1
            next_seat %= len(self.tracker)



if __name__ == "__main__":
    unittest.main()