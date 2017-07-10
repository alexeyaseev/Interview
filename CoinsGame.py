import random
from itertools import product
import time
import numpy as np
import pandas as pd

COINS = [1, 5, 10, 25, 50, 100]

class PerfectGame(object):
    def MinMaxCalc(board):
        parity = len(board) % 2
        vals = [ 0 ] * (len(board)+1)
        size = 0
        while len(vals) > 2:
            newvals = []
            for i in range(1,len(vals)):
                if parity == 0:
                    val = min(vals[i-1] - board[i-1+size], vals[i] - board[i-1])
                else:
                    val = max(vals[i-1] + board[i-1+size], vals[i] + board[i-1])
                newvals.append(val)
            vals = newvals
            size += 1
            parity = 1 - parity
        return vals
    def GetGameResult(board):
        vals = PerfectGame.MinMaxCalc(board)
        return max(vals[0] + board[-1], vals[1] + board[0])
    def GetBestMove(board):
        vals = PerfectGame.MinMaxCalc(board)
        return 1 if (vals[0] + board[-1]) > (vals[1] + board[0]) else 0
    
"""INTERVIEW QUESTION 1:
Is it better to be first or second player?

ANSWER: It is always better to be first player.

PROOF: it is enough to prove two statements: 
       1)There is no board where first player lose
       (practical proof)
         Exhaustive search is done for small boards, for example, size 8 and 6, where each player makes
         even and odd number of moves (different parity idea comes from symmetry considerations).
         Small board sizes sufficiency idea comes from recursive nature of the game. If some trick is available
         in the game then it is usually can be discovered on local scale.
       (theoretical proof)
         First player is able to collect all even-placed coins or all odd-placed coins, so at least draw is
         guaranteed.
       2)There is no draw board (board where first player has at least draw strategy) where first player
         can win by passing turn to second player.
        (theoretical proof)
         By contradiction: second player will choose to play for draw as it is more optimal than to lose.
"""
def Question1_Answer():
    BOARDSIZE = 6#8 #should be even
    if BOARDSIZE % 2: print("ERROR: Even number of coins required!"); return
    
    counter = 0
    for board in product(COINS, repeat = BOARDSIZE):
        hasWinOrDraw = PerfectGame.GetGameResult( board ) >= 0
        if not hasWinOrDraw: print('FOUND losing position for first player:', board);
        counter += 1
        if counter % 10000 == 0: print(counter) #to see the progress (6: 46656, 8: 1679616)

"""INTERVIEW QUESTION 2:
What is an optimal strategy for first player?

ANSWER: Optimal strategy is to build game tree and do minimax calculations on it. Game tree size has square number
        of nodes because two board positions are merged (player1 takes left and player2 takes right leads to same
        position as player1 takes right and player2 takes left). So branching factor 2 is not happening here.
        Optimal strategy is implemented in class PerfectGame. Performance complexity is square on board size.

        Suboptimal easy-to-use strategy is also provided. Strategy consists of two parts. First we try greedy
        approach by considering only 4 coins (two left and two right). If greedy approach is not applicable then
        we just compare sum of even-placed coins with sum of odd-placed coins, so performance complexity is linear.
        Greedy approach:
         1) if maximum of four coins is at any end then take it
         2) if second maximum of four coins is at any end and maximum coin is at other end then take it
        Global approach:
         Take all even-placed coins or all odd-placed coins (which sum is bigger)
        NOTE: global approach works only for even sized boards so can be used only for first player

SIMULATION: Simulation is done via running round-robin tournament, where all strategies play against each other
            except for strategies number 2 and 4 which can be used only for first player.
            Board size is fixed (BOARDSIZE=14). Number of played games is fixed (RUNS=2000)
            Collected metrics:
            1. score (percent value)
             Score is evaluated as sum of coins collected by first player divided by total value of coins.
             For example score 50% means draw.
            2. win rate (percent value)
             Win rate is evaluated as number of games won divided by total number of games
            3. bad strategy flag (0/1 value)
             Flag is set when strategy lost any position during simulation

            Strategies:
                Strategy1 - random strategy
                Strategy2 - suboptimal strategy global part (FIRST PLAYER ONLY!)
                Strategy3 - suboptimal strategy greedy part
                Strategy4 - suboptimal strategy global + greedy (FIRST PLAYER ONLY!)
                Strategy5 - perfect play

            So results are presented as three tables of sizes 5x3, where row means strategy for first player
            and column means strategy for second player


                        strategy1 | strategy3 | strategy5 |
                        __________|___________|___________|
            strategy1 |      x    |     x     |     x     |
            strategy2 |      x    |     x     |     x     |           
            strategy3 |      x    |     x     |     x     |
            strategy4 |      x    |     x     |     x     |
            strategy5 |      x    |     x     |     x     |                
"""
def Question2_Answer():
    def Strategy1(board): #random
        return random.choice((0, 1))

    # only for first player
    def Strategy2(board): #suboptimal global
        if len(board) == 1: return 0
        if len(board) <= 3: # if two or three coins are left just take bigger one
            return 0 if board[0] >= board[-1] else 1        

        # global approach
        return 0 if sum(board[0::2]) > sum(board[1::2]) else 1

    def Strategy3(board): #suboptimal greedy
        if len(board) == 1: return 0
        if len(board) <= 3: # if two or three coins are left just take bigger one
            return 0 if board[0] >= board[-1] else 1        

        # greedy approach
        L, LL, R, RR = board[0], board[1], board[-1], board[-2]
        coins = sorted((L,LL,R,RR), reverse = True)
        maxcoin, smaxcoin = coins[0],coins[1]
        if maxcoin in (L,R): #max coin is at any end then take it
            return 0 if maxcoin == L else 1
        if smaxcoin in (L,R): #second max coin is at any end then take it if max coin is at other end
            if maxcoin == LL and smaxcoin == R: return 1
            if maxcoin == RR and smaxcoin == L: return 0

        return 0

    # only for first player
    def Strategy4(board): #suboptimal greedy + global
        if len(board) == 1: return 0
        if len(board) <= 3: # if two or three coins are left just take bigger one
            return 0 if board[0] >= board[-1] else 1        

        # greedy approach
        L, LL, R, RR = board[0], board[1], board[-1], board[-2]
        coins = sorted((L,LL,R,RR), reverse = True)
        maxcoin, smaxcoin = coins[0],coins[1]
        if maxcoin in (L,R): #max coin is at any end then take it
            return 0 if maxcoin == L else 1
        if smaxcoin in (L,R): #second max coin is at any end then take it if max coin is at other end
            if maxcoin == LL and smaxcoin == R: return 1
            if maxcoin == RR and smaxcoin == L: return 0
                    
        # global approach
        return 0 if sum(board[0::2]) > sum(board[1::2]) else 1

    def Strategy5(board): # perfect play
        return PerfectGame.GetBestMove(board)

    def HeadsUpSimulation( strategy_1, strategy_2, board ):
        cboard = list( board )
        strategy1PlayResult = strategy2PlayResult = 0
        while cboard:
            strategy1Move = strategy_1( cboard )
            strategy1PlayResult += cboard.pop( -strategy1Move )
            strategy2Move = strategy_2( cboard )
            strategy2PlayResult += cboard.pop( -strategy2Move )
        return (strategy1PlayResult, strategy2PlayResult)


    # run round-robin tournament
    BOARDSIZE = 14
    if BOARDSIZE % 2 != 0: print("ERROR: Even number of coins required!"); return None
    GAMES = 2000
    STRATEGIES1 = ( Strategy1, Strategy2, Strategy3, Strategy4, Strategy5 )
    STRATEGIES2 = ( Strategy1, Strategy3, Strategy5 ) # Strategy2 and Strategy4 are only for first player
    STRATEGIES1NAMES = ("rand", "global", "greedy", "greedy+global", "perfect")
    STRATEGIES2NAMES = ("rand", "greedy", "perfect")
    
    scoreTable   = np.zeros((len(STRATEGIES1), len(STRATEGIES2)))
    winRateTable = np.zeros((len(STRATEGIES1), len(STRATEGIES2)), dtype=np.float64)
    badFlagTable = np.zeros((len(STRATEGIES1), len(STRATEGIES2)), dtype=np.int8)

    for game in range(1, GAMES+1):
        board = random.choices(COINS, k = BOARDSIZE)
        #print(board)
        for i,strategy1 in enumerate(STRATEGIES1):
            for j,strategy2 in enumerate(STRATEGIES2):
                coins1, coins2 = HeadsUpSimulation( strategy1, strategy2, board )

                if (coins1 < coins2):
                    badFlagTable[i,j] = 1
                elif (coins1 > coins2):
                    winRateTable[i,j] += 1
                score1 = coins1 / (coins1 + coins2)
                scoreTable[i,j] = scoreTable[i,j] * (game-1)/game + (1/game) * score1
        #if game % 1000 == 0: print(game); #to see progress
    winRateTable *= (100/GAMES)
    scoreTable *= 100
    
    # present results
    df = pd.DataFrame(scoreTable, index=STRATEGIES1NAMES, columns=STRATEGIES2NAMES)
    df = df.round(1)
    print("Score table:")
    print(df,end="\n\n")
    df = pd.DataFrame(winRateTable, index=STRATEGIES1NAMES, columns=STRATEGIES2NAMES)
    df = df.round(1)
    print("Win rate table:")
    print(df,end="\n\n")
    df = pd.DataFrame(badFlagTable, index=STRATEGIES1NAMES, columns=STRATEGIES2NAMES)
    print("Bad strategy flag table:")
    print(df,end="\n\n")

#Question1_Answer()
Question2_Answer()
