import unittest
from fivecarddraw import ChipTracker

class ChipTrackerTest(unittest.TestCase):
    def setUp(self):
        # create tracker
        self.tracker = ChipTracker()


    def testPlayerTracking(self):
        # check untracking one player at a time
        names = [f"{j}" for j in range(10)]

        # track players
        self.tracker.TrackPlayers(names)
        num_tracked = len(self.tracker.TrackedPlayers())

        # cycle tests per individual player
        for name in names:
            # untrack player
            self.tracker.UntrackPlayers(list(name))

            # check player is no longer tracked
            self.assertNotIn(name, self.tracker.TrackedPlayers())
            # check only one player is forgotten
            num_tracked -= 1
            self.assertEqual(len(self.tracker.TrackedPlayers()), num_tracked)

        # check all players are forgotten
        self.assertEqual(num_tracked, 0)

        # check untracking different amounts of players at a time
        for i in range(10):
            # track players
            names = [f"{j}" for j in range(i+1)]
            self.tracker.TrackPlayers(names)

            # check correct amount of players tracked
            self.assertEqual(len(self.tracker.TrackedPlayers()), len(names))
            # check correct hash of players tracked
            self.assertEqual(set(names), set(self.tracker.TrackedPlayers()))

            # untrack players
            self.tracker.UntrackPlayers(names)
            # check all players are forgotten
            self.assertEqual(len(self.tracker.TrackedPlayers()), 0)

        # check can't forget a player if not tracked
        names = [f"{i}" for i in range(10)]
        self.tracker.TrackPlayers(names)
        self.assertRaises(KeyError, self.tracker.UntrackPlayers, names=["10"])


    def testChipAssignment(self):
        # track players
        names = [f"{i}" for i in range(10)]
        self.tracker.TrackPlayers(names)

        # check cant assign or unassign to player if not tracked
        some_chips = 500
        self.assertRaises(KeyError, self.tracker.Reward, name="10", amount=some_chips)
        self.assertRaises(KeyError, self.tracker.Spend, name="10", amount=some_chips)

        # check assignment of chips individually
        total = 0
        for i in range(10):
            # assign chips to player
            player = names[i]
            self.tracker.Reward(player, some_chips)
            total += some_chips

            # check tracking attributes
            self.assertEqual(some_chips, self.tracker.Stack(player))
            self.assertEqual(abs(self.tracker), total)

        # check removal of chips individually
        total = abs(self.tracker)
        for i in range(10):
            # renove chips from player
            player = names[i]
            self.tracker.Spend(player, some_chips)
            total -= some_chips

            # check tracking attributes
            self.assertEqual(0, self.tracker.Stack(player))
            self.assertEqual(abs(self.tracker), total)

        # check all players have no chips
        self.assertEqual(set(names), set(self.tracker.SkintPlayers()))


    def testBetting(self):
        # check comparisions between bet amounts and player stack size
        some_chips = 500

        # track players
        names = [f"{i}" for i in range(10)]
        self.tracker.TrackPlayers(names)

        # give all players chips
        total = 0
        for name in names:
            self.tracker.Reward(name, some_chips)
            total += some_chips

        # cycle tests through different bet amounts to compare with players stack
        name = names[0]
        for i in range(10):
            # create a bet size
            bet = i * 100
            if bet <= some_chips:
                # check player has enough chips for bet
                self.assertTrue(self.tracker.HasEnough(name, bet))
            else:
                # check player doesn't have enough chips for bet
                self.assertFalse(self.tracker.HasEnough(name, bet))
                # check player can't make bet
                self.assertRaises(ValueError, self.tracker.Spend, name=name, amount=bet)

        # cycle tests through each player to check contributing
        for i in range(10):
            # select player to contribute
            player = names[i]
            # create contribution amount
            contribution = i * 50
            # get contribution from player
            self.tracker.Bet(player, contribution)

            # check player has contributed
            self.assertEqual(contribution, self.tracker.Contribution(player))
            # check player stack size decreased
            self.assertEqual(some_chips - contribution, self.tracker.Stack(player))
            # check total tracked chips remains the same
            self.assertEqual(total, abs(self.tracker))

        # check amount to call for each player
        max_contribution = self.tracker.MaxContribution()
        for name in names:
            self.assertEqual(self.tracker.CallAmount(name), max_contribution - self.tracker.Contribution(name))

        # check bet details for bets by each player
        for name in names:
            # create amount to call for player
            min_to_call = self.tracker.CallAmount(name)

            # create max bet constraint
            max_bet = (self.tracker.Contribution(name) + 100) // 50
            # cycle tests through different bet amounts to compare the bet with the amount required to call
            for i in range(max_bet):
                # create bet
                bet = i * 50
                # create bet details
                details = self.tracker.BetDetails(name, bet)

                # check raise is recognised
                if bet > min_to_call :
                    self.assertTrue(details["has_raised"])
                else:
                    self.assertFalse(details["has_raised"])

                # check all in is recognised
                if bet == self.tracker.Stack(name) and bet > 0:
                    self.assertTrue(details["has_allin"])
                else:
                    self.assertFalse(details["has_allin"])

                # check min called is recognised
                if bet >= min_to_call:
                    self.assertTrue(details["has_mincalled"])
                else:
                    self.assertFalse(details["has_mincalled"])
                
                # check folds are recognised
                if bet < min_to_call and not bet:
                    self.assertTrue(details["has_folded"])
                else:
                    self.assertFalse(details["has_folded"])


    def testRewardCalculation(self):
        # create max stack size
        some_chips = 500

        # prepare tests for different table states
        for i in range(10):
            # prepare tests by creating players
            names = [f"{j}" for j in range(10)]
            self.tracker.TrackPlayers(names)

            # prepare tests by simulating betting
            for j in range(10):
                # select player
                player = names[j]
                # give chips to player
                self.tracker.Reward(player, some_chips)
                # create contribution amount
                contribution = j * 50
                # get contribution from player
                self.tracker.Bet(player, contribution)

            # select a player
            player = names[i]
            # find contribution of player
            spec_contribution = self.tracker.Contribution(player)
            # remove all players contributions upto the specified contribution
            misc_chips = self.tracker.GatherContributions(spec_contribution)

            # check less chips were taken than total tracked chips
            self.assertLessEqual(misc_chips, some_chips * 10)

            # check amount of chips that were taken
            if i == 0:
                # check no chips were taken
                self.assertEqual(0, misc_chips)
            else:
                # calculate correct amount of chips
                tally = 0
                for j in range(1, i+1):
                    tally += (10 - j) * 50
                # check correct amount of chips were taken
                self.assertEqual(tally, misc_chips)
                
            # cycle tests through each player
            for name in names:
                # find stack size
                stack = self.tracker.Stack(name)
                contribution = self.tracker.Contribution(name)

                # check whether player had contributed less than specified contribution
                if stack >= some_chips - spec_contribution:
                    # check all contribution was taken
                    self.assertEqual(0, contribution)
                else:
                    # check enough contribution was taken
                    self.assertEqual(spec_contribution, some_chips - contribution - stack)

            # forget players
            self.tracker.UntrackPlayers(names)

        # prepare tests for split pot scenarios
        for i in range(10):
            # prepare tests by creating players
            names = [f"{j}" for j in range(10)]
            self.tracker.TrackPlayers(names)

            # prepare tests by simulating betting
            for j in range(10):
                # select player
                player = names[j]
                # give chips to player
                self.tracker.Reward(player, some_chips)
                # create contribution amount
                contribution = j * 50
                # get contribution from player
                self.tracker.Bet(player, contribution)
            

            # prepare tests by simulating group of players with same hand
            names_for_split = [name for j, name in enumerate(names) if i and i < 6 and j % i]
            contributions = {name : self.tracker.Contribution(name) for name in names_for_split}

            # reward players
            rewards = self.tracker.SplitContributions(names_for_split)

            # check amount of tracked chips doesn't change
            self.assertEqual(some_chips * 10, abs(self.tracker))
            # check total rewards is at least as much as total contributed by players with same hand
            self.assertGreaterEqual(sum(rewards.values()), sum(contributions.values()))

            # cycle tests through each player in split
            for name in names_for_split:
                # check player was rewarded more than they contributed
                self.assertGreaterEqual(rewards[name], contributions[name])


    def testAnte(self):
        # check ante can be set
        ante = 300
        self.tracker.UpdateAnte(ante)
        self.assertEqual(ante, self.tracker.Ante())

        # create max stack size
        some_chips = 500

        # prepare tests for different table states
        for i in range(10):
            # prepare tests by creating players
            names = [f"{j}" for j in range(10)]
            self.tracker.TrackPlayers(names)

            # prepare tests by simulating betting
            for j in range(10):
                # select player
                player = names[j]
                # give chips to player
                self.tracker.Reward(player, some_chips)
                # create contribution amount
                contribution = j * 50
                # get contribution from player
                self.tracker.Bet(player, contribution)
                # forget contribution
                self.tracker.GatherContributions(contribution)

            # cycle tests through each player
            for name in names:
                # find stack size
                stack = self.tracker.Stack(name)

                # pay ante
                status = self.tracker.PayAnte(name)

                # check if players coul afford ante
                if stack <= ante:
                    # check player contributed whole stack
                    self.assertEqual(stack, self.tracker.Contribution(name))
                    # check status
                    self.assertTrue(status["bet_all"])
                    self.assertFalse(status["bet_something"])  
                else:
                    # check player contributed enough
                    self.assertEqual(ante, self.tracker.Contribution(name))
                    # check status
                    self.assertFalse(status["bet_all"])
                    self.assertTrue(status["bet_something"]) 


if __name__ == "__main__":
    unittest.main()
