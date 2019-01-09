# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

bet_1x2_list = ['1', 'X' , '2', 'x']
bet_double_1x2_list = ['1X', 'X1', '2X', 'X2', '12', '21', '1x', 'x1', '2x', '2x']
bet_ah_list = ['AH 1', 'AH1', 'AH 2', 'AH2']
bet_ou_list = ['TO', 'TU', 'Over', 'Under']

period_list = ['1st quarter', '2nd quarter']

bet_accepted = 'BET ACCEPTED!'
odds_changed = 'The odds have changed for event'
already_placed = 'You have already placed a bet on'
unable_place = 'Unable to place a bet on the outcome of'
blocked_bet = 'are temporarily blocked for betting'
not_enough_funds = 'Not enough funds in the account'
