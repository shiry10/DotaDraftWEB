
import pickle
import numpy as np
import random
import json
import os

from keras.models import load_model
from keras import backend as K
from dotacoach.models import WinrateOne, WinrateSingle




class Random_picker:
    """Randomly pick hero"""
    def __init__(self, side='Radiant', pool=set(list(range(1,24)) + list(range(25, 115)) + [119,120])):
        self.pool = pool

    def pick(self, Round, picked_r, picked_d, avail=None, Max_sampling=0):
        """
        randomly select hero
        avail: list of available heroes
        picked: list of picked heroes
        max_sampling: no use
        """
        if Round < 0 or Round > 9:
            raise Exception("Not started or have finished! Round out of range", Round)
        if avail == None:
            avail = list(self.pool)
        for hero in picked_r + picked_d:
            if hero in avail:
                avail.remove(hero)
        return random.choice(avail)




class Greedy_picker:
    def __init__(self, side='Radiant', pool=set(list(range(1,24)) + list(range(25, 115)) + [119,120])):
        self.pool = pool


    def pick(self, Round, picked_r, picked_d, avail=None, Max_sampling=0):
        """
        return the highest winrate hero against the last picked hero.
        """
        if not avail:
            avail = list(self.pool)
        for hero in picked_r + picked_d:
            if hero in avail:
                avail.remove(hero)
        picked = picked_d if self.side == 'Radiant' else picked_d
        if not picked:
            winrate_argsort = WinrateSingle.objects.order_by('-winrate')
        else:
            winrate_argsort = WinrateOne.objects.filter(op=picked[-1]).order_by('-winrate')
        top = self.select_top_from_available(avail, winrate_argsort, random_range=10)
        return random.choice(top)


    def select_top_from_available(self, avail, winrate_argsort, random_range=5):
        top = []
        ind = 0
        while random_range > 0:
            if winrate_argsort[ind].id not in avail:
                ind += 1
            else:
                top.append(winrate_argsort[ind].id)
                random_range -= 1
                ind += 1
        return top






class Monte_Carlo_picker:

    def __init__(self, side='Radiant', data=None, pool=set(list(range(1,24)) + list(range(25, 115)) + [119,120]), order=[0,3,4,7,8]):
        self.data = data
        # initialize hero pool
        self.pool = pool
        # hero pick order, the round radiant heroes are picked
        self.order = order
        # load environment
        module_dir = os.path.dirname(__file__)
        self.model_path = os.path.join(module_dir, 'static/picker/data/predictor.h5')
        K.clear_session()
        self.predictor = load_model(self.model_path)
        self.side = side


    def pick(self, Round, picked_r, picked_d, avail=None, Max_sampling=1000):
        """
        Round: int, round of current pick
        picked: list, list of picked heroes
        Max_sampling: max number of Monte Carlo sampling
        return picked hero of this round
        """
        # check if the input is valid
        if Round != len(picked_r+picked_d):
            raise Exception("Invalid input: Round and picked hero don't match", Round, picked)
        # remove picked hero from hero pool
        if avail == None:
            avail = list(self.pool)
        for hero in picked_r + picked_d:
            if hero in avail:
                avail.remove(hero)

        # First pick: randomly pick some high winrate hero available in the hero pool
        if Round == 0:
            return self.firstpick(avail)
        # Second pick: randomly pick some high winrate hero against the picked
        if Round == 1:
            if self.side == 'Radiant':
                return self.secondpick(avail, picked_d)
            else:
                return self.secondpick(avail, picked_r)
        # For further pick, do Monte Carlo sampling
        # allocate picked heroes in picking order
        picked = []
        for i in range(Round):
            if i in self.order:
                picked.append(picked_r.pop(0))
            else:
                picked.append(picked_d.pop(0))
        return self.Monte_Carlo(avail, Round, picked, Max_sampling)


    def select_top_from_available(self, avail, winrate_argsort, random_range=5):
        top = []
        ind = 0
        while random_range > 0:
            if winrate_argsort[ind].id not in avail:
                ind += 1
            else:
                top.append(winrate_argsort[ind].id)
                random_range -= 1
                ind += 1
        return top


    def firstpick(self, avail, random_range=20):
        """
        For first pick, randomly pick heros from
        top #random_range heros from available heroes.
        """
        winrate_argsort = WinrateSingle.objects.order_by('-winrate')
        top = self.select_top_from_available(avail, winrate_argsort, random_range)
        return random.choice(top)


    def secondpick(self, avail, picked, random_range=5):
        """
        For second pick, randomly pick heroes from
        top #random_range heroes against the picked hero.
        """
        winrate_argsort = WinrateOne.objects.filter(op=picked[-1]).order_by('-winrate')
        top = self.select_top_from_available(avail, winrate_argsort, random_range)
        return random.choice(top)



    def Monte_Carlo(self, avail, Round, picked, Max_sampling):
        """
        Do Monte Carlo sampling and return heroes with largest reward value.
        """
        # policy is the probability of selecting a hero in avail
        policy = np.zeros([max(avail)+1])
        selected_times = np.ones([max(avail)+1])
        # initially, for all heroes in avail, probability of picking all heroes is equal.
        for hero in avail:
            policy[hero] = 0.1
        # Do sampling Max_sampling times
        for i in range(Max_sampling):
            # single_sampling should return slected hero in first following round
            # and return win probability.
            selected_hero, win_probability = self.single_sampling_equal_prob(avail, Round, picked)
            selected_times[selected_hero] += 1
            if self.side == 'Dire':
                win_probability = 1 - win_probability
            policy[selected_hero] += win_probability
        policy = policy / selected_times
        # print(np.argmax(policy), policy)
        K.clear_session()
        return np.argmax(policy)


    def single_sampling_equal_prob(self, avail, Round, picked):
        """
        Do sampling for a single time.
        """
        if Round < 10:
            selected = random.choice(avail)
            new_avail, new_picked = avail.copy(), picked.copy()
            new_avail.remove(selected)
            new_picked.append(selected)
            win_probability = self.single_sampling_equal_prob(new_avail, Round+1, new_picked)[1]
            return selected, win_probability
        if Round == 10:
            lineup = self.assign_team(picked)
            lineup = np.array(lineup).reshape(1, 10)
            win_probability = self.predictor.predict(lineup)
            # print(lineup, win_probability)
            return None, win_probability


    def assign_team(self, picked):
        """
        picked: list of picked heroes
        return: list
        """
        lineup_r, lineup_d = [], []
        for i, hero in enumerate(picked):
            if i in self.order:
                lineup_r.append(hero)
            else:
                lineup_d.append(hero)
        return lineup_r + lineup_d


    def e_greedy(self, policy, e=0.1):
        pro = random.random()
        if pro > e:
            return np.argmax(policy)
        else:
            nonzero = [ind for ind in range(len(policy)) if policy[ind] != 0]
            return random.choice(nonzero)
