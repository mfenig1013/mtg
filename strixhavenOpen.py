# -*- coding: utf-8 -*-
"""
Created on Fri May  7 19:18:01 2021
Strixhaven Open
https://magic.wizards.com/en/articles/archive/news/may-2021-arena-open-strixhaven-sealed-2021-04-22
@author: Tom
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# buy in gems
buyInGem = 4500.
# prices as of 2021-05-07
gemPurchase = 1600. + 3400.
gemCostUSD = 10. + 20.
usdPerGem = gemCostUSD/gemPurchase
# buy-in cost in USD
buyInUSD = buyInGem*usdPerGem

# payouts for day 1 assuming best of 1 track
pday1b1 = {0: 0, 1: 0, 2: 0, 3: 400*usdPerGem, 4: 800*usdPerGem,
         5: 1200*usdPerGem, 6: 1600*usdPerGem, 7: 2000*usdPerGem}

# payouts for day 1 assuming best of 3 track
pday1b3 = {0: 0, 1: 1000*usdPerGem, 2: 2500*usdPerGem,
           3: 5000*usdPerGem, 4: 5000*usdPerGem}

# payouts for day 2
pday2 = {0: 0, 1: 2000*usdPerGem, 2: 4000*usdPerGem, 3: 6000*usdPerGem,
         4: 10000*usdPerGem, 5: 20000*usdPerGem, 6: 1000., 7: 2000.}

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

# day 2 
def tourneyDay2(winPerc):
    metrics2 = {'wins_day2': 0, 'losses_day2': 0}
    flag = True
    while(flag):
        result = play3(winPerc)
        if result == 1:
            metrics2['wins_day2'] += 1
        else:
            metrics2['losses_day2'] += 1
        if (metrics2['wins_day2'] == 7) or (metrics2['losses_day2'] == 2):
            flag = False
    day2Payout = pday2[metrics2['wins_day2']]
    return day2Payout, metrics2

# best-of-1 track on day 1
def tourneyb1(winPerc):
    metrics = {'wins_day1': 0, 'losses_day1': 0}
    flag = True
    while(flag):
        result = play3(winPerc)
        if result == 1:
            metrics['wins_day1'] += 1
        else:
            metrics['losses_day1'] += 1
        # 7 wins or 3 losses, whichever comes first
        if (metrics['wins_day1'] == 7) or (metrics['losses_day1'] == 3):
            flag = False
    day1Payout = pday1b1[metrics['wins_day1']]
    if metrics['wins_day1'] == 7:
        day2Payout, metrics2 = tourneyDay2(winPerc)
    else:
        day2Payout = 0.
        metrics2 = {'wins_day2': 0, 'losses_day2': 0}
    totalPayout = day1Payout + day2Payout
    metrics['totalPayout'] = totalPayout
    metrics['day1Payout'] = day1Payout
    metrics['day2Payout'] = day2Payout
    metrics.update(metrics2)
    return metrics
    
# best-of-3 track on day 1
def tourneyb3(winPerc):
    metrics = {'wins_day1': 0, 'losses_day1': 0}
    flag = True
    while(flag):
        result = play3(winPerc)
        if result == 1:
            metrics['wins_day1'] += 1
        else:
            metrics['losses_day1'] += 1
        # 4 wins or 1 loss, whichever comes first
        if (metrics['wins_day1'] == 4) or (metrics['losses_day1'] == 1):
            flag = False
    day1Payout = pday1b3[metrics['wins_day1']]
    if metrics['wins_day1'] == 4:
        day2Payout, metrics2 = tourneyDay2(winPerc)
    else:
        day2Payout = 0.
        metrics2 = {'wins_day2': 0, 'losses_day2': 0}
    totalPayout = day1Payout + day2Payout
    metrics['totalPayout'] = totalPayout
    metrics['day1Payout'] = day1Payout
    metrics['day2Payout'] = day2Payout
    metrics.update(metrics2)
    return metrics

def main():
    # num sims
    N = 100000
    # win percentage
    winPercs = np.arange(0.0, 1, 0.01)
    
    # best-of-1 track
    wresults1 = []
    for iw in range(len(winPercs)):
        winPerc = winPercs[iw]
        results = []
        for ix in range(N):
            results.append(tourneyb1(winPerc))
        rdf = pd.DataFrame(results)
        avgPayout = rdf['totalPayout'].mean()
        tmp = rdf['totalPayout'].describe([0.025, 0.975])
        wdict = {'winPerc': winPerc, 'expectedPayout': avgPayout, 'upper': tmp['97.5%'], 'lower': tmp['2.5%']}
        wresults1.append(wdict)
        print(wdict)
    wdf1 = pd.DataFrame(wresults1)
    
    # best-of-3 track
    wresults3 = []
    for iw in range(len(winPercs)):
        winPerc = winPercs[iw]
        results = []
        for ix in range(N):
            results.append(tourneyb3(winPerc))
        rdf = pd.DataFrame(results)
        avgPayout = rdf['totalPayout'].mean()
        tmp = rdf['totalPayout'].describe([0.025, 0.975])
        wdict = {'winPerc': winPerc, 'expectedPayout': avgPayout, 'upper': tmp['97.5%'], 'lower': tmp['2.5%']}
        wresults3.append(wdict)
        print(wdict)
    wdf3 = pd.DataFrame(wresults3)
    
    plt.figure(figsize=(10,10))
    plt.subplot(221)
    plt.plot(wdf1['winPerc']*100, wdf1['expectedPayout'], 'b-', label='best-of-1');
    plt.plot(wdf1['winPerc']*100, wdf1['lower'], 'b--', alpha=0.33);
    plt.plot(wdf1['winPerc']*100, wdf1['upper'], 'b--', alpha=0.33);
    plt.plot(wdf3['winPerc']*100, wdf3['expectedPayout'], 'g-', label='best-of-3');
    plt.plot(wdf1['winPerc']*100, wdf3['lower'], 'g--', alpha=0.33);
    plt.plot(wdf1['winPerc']*100, wdf3['upper'], 'g--', alpha=0.33);
    plt.plot(wdf3['winPerc']*100, [buyInUSD]*len(wdf3), 'r', label='buy-in')
    plt.legend();
    plt.grid();
    plt.xlabel('Assumed Win Percentage (%)')
    plt.ylabel('Payout ($)')
    plt.subplot(222)
    plt.plot(wdf1['winPerc']*100, wdf1['expectedPayout'], 'b-', label='best-of-1');
    plt.plot(wdf1['winPerc']*100, wdf1['lower'], 'b--', alpha=0.33);
    plt.plot(wdf1['winPerc']*100, wdf1['upper'], 'b--', alpha=0.33);
    plt.plot(wdf3['winPerc']*100, wdf3['expectedPayout'], 'g-', label='best-of-3');
    plt.plot(wdf1['winPerc']*100, wdf3['lower'], 'g--', alpha=0.33);
    plt.plot(wdf1['winPerc']*100, wdf3['upper'], 'g--', alpha=0.33);
    plt.plot(wdf3['winPerc']*100, [buyInUSD]*len(wdf3), 'r', label='buy-in')
    plt.legend();
    plt.grid();
    plt.xlabel('Assumed Win Percentage (%)')
    plt.ylabel('Payout ($)')
    plt.xlim([50, 60]);
    plt.ylim([0, 60]);