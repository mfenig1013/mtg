# -*- coding: utf-8 -*-
"""
Created on Fri May  7 21:17:08 2021
Formats Analysis
@author: Tom
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# play one round
def play1(winPerc):
    return int(np.random.rand() <= winPerc)

# play a best of 3 match
# note this isn't really necessary given independence assumption on winPerc
# but if we start adding adjustments for sideboarding, etc. could be useful later
def play3(winPerc):
    r1 = play1(winPerc)
    r2 = play1(winPerc)
    r12 = r1 + r2
    if r12 == 0:
        # lose games 1 and 2
        return 0
    elif r12 == 2:
        # won games 1 and 2
        return 1
    else:
        # won at least one, result determined by game 3
        return play1(winPerc)

def premier(winPerc):
    payouts = {0: 50, 1: 100, 2: 250, 3: 1000, 4: 1400, 5: 1600, 6: 1800, 7: 2200}
    metrics = {'wins': 0, 'losses': 0}
    flag = True
    while(flag):
        result = play1(winPerc)
        if result == 1:
            metrics['wins'] += 1
        else:
            metrics['losses'] += 1
        if (metrics['wins'] == 7) or (metrics['losses'] == 3):
            flag = False
    payout = payouts[metrics['wins']]
    return payout

def traditional(winPerc):
    payouts = {0: 0, 1: 0, 2: 1000, 3: 3000}
    metrics = {'wins': 0, 'losses': 0}
    result1 = play3(winPerc)
    result2 = play3(winPerc)
    result3 = play3(winPerc)
    wins = result1 + result2 + result3
    payout = payouts[wins]
    return payout

def quick(winPerc):
    payouts = {0: 50, 1: 100, 2: 200, 3: 300, 4: 450, 5: 650, 6: 850, 7: 950}
    metrics = {'wins': 0, 'losses': 0}
    flag = True
    while(flag):
        result = play3(winPerc)
        if result == 1:
            metrics['wins'] += 1
        else:
            metrics['losses'] += 1
        if (metrics['wins'] == 7) or (metrics['losses'] == 3):
            flag = False
    payout = payouts[metrics['wins']]
    return payout

def runSim(N, foo):
    sresults = []
    winPercs = np.arange(0.0, 1, 0.01)
    for si in range(len(winPercs)):
        winPerc = winPercs[si]
        results = []
        for ix in range(N):
            results.append(foo(winPerc))
        payout = pd.Series(results)
        tmp = payout.describe([0.025, 0.975])
        wdict = {'winPerc': winPerc, 'expectedPayout': payout.mean(), 'upper': tmp['97.5%'], 'lower': tmp['2.5%']}
        sresults.append(wdict)
    rdf = pd.DataFrame(sresults)
    return rdf

def main():
    premierCost = 1500
    traditionalCost = 1500
    quickCost = 750

    # num sims
    N = 10000
    premierDF = runSim(N, premier)
    tradDF = runSim(N, traditional)
    quickDF = runSim(N, quick)
    
    plt.figure(figsize=(10,10))
    plt.plot(premierDF['winPerc']*100, premierDF['expectedPayout'], 'b', label='premier')
    plt.plot(premierDF['winPerc']*100, premierDF['lower'], 'b--', alpha=0.33)
    plt.plot(premierDF['winPerc']*100, premierDF['upper'], 'b--', alpha=0.33)
    plt.plot(premierDF['winPerc']*100, [premierCost]*len(premierDF), 'b', label='premier buy-in')
    
    plt.plot(tradDF['winPerc']*100, tradDF['expectedPayout'], 'g', label='traditional')
    plt.plot(tradDF['winPerc']*100, tradDF['lower'], 'g--', alpha=0.33)
    plt.plot(tradDF['winPerc']*100, tradDF['upper'], 'g--', alpha=0.33)
    plt.plot(tradDF['winPerc']*100, [traditionalCost]*len(tradDF), 'g', label='traditional buy-in')
    
    plt.plot(quickDF['winPerc']*100, quickDF['expectedPayout'], 'r', label='quick')
    plt.plot(quickDF['winPerc']*100, quickDF['lower'], 'r--', alpha=0.33)
    plt.plot(quickDF['winPerc']*100, quickDF['upper'], 'r--', alpha=0.33)
    plt.plot(quickDF['winPerc']*100, [quickCost]*len(quickDF), 'r', label='quick buy-in')
    plt.xlabel('Assumed Win %')
    plt.ylabel('Payoff in Gems')
    
    plt.grid()
    plt.legend()