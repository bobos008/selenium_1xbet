# coding=utf-8

import time
import json
import requests
import ele_utils
import mybooks
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from fuzzywuzzy import fuzz

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Client1xbet(object):
    def __init__(self, username='', password='', needlogin=True):
        self._username = username 
        self._password = password
        self._needlogin = needlogin
        self._init_url = 'https://jp.1xbet.com/en/live/Football/'
        self.event_team_split = ' — '
        # options = Options()
        # options.add_argument('-headless')
        # self._driver = webdriver.Firefox(firefox_options=options)
        init_num = 0
        while True:
            try:
                self._driver = webdriver.Chrome()
                self._driver.maximize_window()
                if init_num > 6:
                    print u'网络有问题， 请稍后请求'
                    break
                self._driver.get(self._init_url)
                if self._needlogin:
                    if self.login():
                        break
                    else:
                        init_num += 1
                        continue
                else:
                    break
                current_url = self._driver.current_url
                if current_url == self._init_url:
                    break
            except:
                continue

    def login(self):
        ''' 登录 '''
        login_num = 1
        while True:
            if login_num > 5:
                return False
            login_frame_xpath = '//div[@class="curloginDropTop"]'
            open_login_frame_ele = ele_utils.get_include_hide_element_for_wait(self._driver,\
                By.XPATH, login_frame_xpath)
            if not open_login_frame_ele:
                login_num += 1
                self._driver.refresh()
                time.sleep(3)
                continue
            open_login_frame_ele.click()

            username_xpath = '//input[@id="userLogin"]'
            username_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
                username_xpath)
            if not username_ele:
                login_num += 1
                self._driver.refresh()
                time.sleep(3)
                continue
            username_ele.send_keys(self._username)

            password_xpath = '//input[@id="userPassword"]'
            password_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
                password_xpath)
            if not password_ele:
                login_num += 1
                self._driver.refresh()
                time.sleep(3)
                continue
            password_ele.send_keys(self._password)

            login_btn_xpath = '//a[@id="userConButton"]'
            login_btn_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH, \
                login_btn_xpath)
            if not login_btn_ele:
                login_num += 1
                self._driver.refresh()
                time.sleep(3)
                continue
            login_btn_ele.click()
            return True

    def is_login(self):
        ''' 判断是否登录 '''
        account_xpath = '//span[@class="wrap_lk "]/a[1]/span'
        account_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
        account_xpath, timeout=3)
        is_login_num = 1
        while True:
            if is_login_num > 2:
                break
            if not account_ele:
                is_login_num += 1
                continue
            return True
        return False
            
    def find_event(self, data, stake='2'):
        print '================find_event=================='
        while True:
            if self.is_login():
                operate_res = self.operate_event(data, stake)
                print 'operate_res:', operate_res
                if not (self._driver.current_url == self._init_url):
                    if not self.back_live_page():
                       continue 
                self.clear_bet()
                return operate_res
            else:
                if self.login():
                    continue
                else:
                    print 'login fail'
                    return False

    def operate_event(self, data, bet_stake):
        ''' 找盘口，并打开 '''
        print '-------------operate_event----------'
        event_teams_xpath = '//span[@class="c-events__teams"]'
        while True:
            event_teams_ele_list = ele_utils.get_include_hide_elements_for_wait(self._driver,\
                By.XPATH, event_teams_xpath, 20)
            if not event_teams_ele_list:
                return False
            for event_team_ele in event_teams_ele_list:
                teams = event_team_ele.get_attribute('title').strip()
                if (not teams) and (self.event_team_split in teams):
                    return False
                home, away = teams.split(self.event_team_split)
                home_data = data.get('home', '') 
                away_data = data.get('away', '')
                # 去掉(younth)
                delete_str = ' (youth)'
                replace_str = ''
                if (delete_str in home_data) and (delete_str in away_data) :
                    home_data = home_data.replace(delete_str, replace_str)
                    away_data = away_data.replace(delete_str, replace_str)
                home_fuzzy_res = fuzz.ratio(home, home_data)
                away_fuzzy_res = fuzz.ratio(away, away_data)
                if (home_fuzzy_res >= 80) or (away_fuzzy_res >= 80):
                    event_team_ele.click()
                    break
            break

        href_num = 1
        while True:
            if href_num > 9:
                return False
            current_href = self._driver.current_url
            if current_href != self._init_url:
                break
            time.sleep(1)
            href_num += 1 

        # 选择展示样式(单列)
        if not self.single_column():
            return False

        # 选择时间
        period = data.get('period', '')
        if period in mybooks.period_list:
            if not self.choose_period(period):
                return False
            if period == '1st quarter':
                period_kw = '. 1  Half '
            elif period == '2nd quarter':
                period_kw = '. 2  Half '
            else:
                return False
        else:
            period_kw = ''

        bet_name = data.get('bet_name', '')
        bet_value = data.get('bet_value', '0')
        if (bet_name in mybooks.bet_1x2_list) or (bet_name in\
            mybooks.bet_double_1x2_list):
            if not self.operate_1x2(bet_name, home, away, period_kw):
                return False
        elif bet_name in mybooks.bet_ou_list:
            if not self.operate_ou(bet_name, bet_value, period_kw):
                return False
        elif bet_name in mybooks.bet_ah_list:
            if not self.operate_ah(bet_name, bet_value, home, away, period_kw):
                return False
        else:
            return False

        koef = data.get('koef', '0')
        if not self.to_do_bet(koef, bet_stake):
            print '投注失败！'
            return False
        return True

    def to_do_bet(self, koef, bet_stake='0'):
        ''' 开始投注操作 '''

        if bet_stake == '0':
            return False

        current_koef = self.get_koef()
        if not self.reasonable_koef(current_koef, koef):
            return False
        stake = '2'
        if not self.send_stake(stake):
            return False

        # 关闭比赛视频窗口
        self.close_window_play_png()

        if not self.click_place_bet():
            print u'点击投注按钮失败！'
            time.sleep(1000)
            return False
        if not self.bet_result(koef):
            return False
        return True

    def bet_result(self, koef):
        ''' 投注结果 '''

        bet_result_text = self.get_bet_result()
        if mybooks.bet_accepted in bet_result_text:
            self.click_ok()
            return True
        else:
            print u'投注失败！' 
            confirm_action_text_xpath = '//div[@class="ui-dialog-content ui-widget-content"]/span'
            confirm_action_text_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,
                confirm_action_text_xpath)
            if not confirm_action_text_ele:
                return False
            confirm_action_text = confirm_action_text_ele.text 
            if mybooks.odds_changed in confirm_action_text:
                print u'赔率发生改变'
                if not self.change_click_ok():
                    return False
                current_koef = self.get_koef()
                if not self.reasonable_koef(current_koef, koef):
                    return False
                if not self.click_place_bet():
                    return False
                bet_result_text = self.get_bet_result()
                if mybooks.bet_accepted in bet_result_text:
                    return True
                return False
            if mybooks.already_placed in confirm_action_text:
                print u'该盘口你已经投注了！'
                return False
            if mybooks.unable_place in confirm_action_text:
                print u'对该盘口无法下注！'
                return False
            if mybooks.blocked_bet in confirm_action_text:
                print u'该盘口暂时禁止投注'
                return False
            if mybooks.not_enough_funds in confirm_action_text:
                print u'用户资金不足！'
                return False
            print confirm_action_text
            return False

    def get_bet_result(self):
        ''' 获取投注结果 '''
        bet_result_text_xpath1 = '//div[contains(@class,  "c-coupon-modal__title c-coupon-modal__status")]'
        bet_result_text_xpath2 = '//span[@class="ui-dialog-title"]'

        is_change = True
        num = 1
        while True:
            if num > 2:
                return ''
            if is_change:
                bet_result_text_xpath = bet_result_text_xpath1
                is_change = False
            else:
                bet_result_text_xpath = bet_result_text_xpath2
            bet_result_text_ele = ele_utils.get_element_for_wait(self._driver, By.XPATH,
                bet_result_text_xpath, timeout=20)
            if not bet_result_text_ele:
                num += 1
                continue
            break

        try:
            bet_result_text = bet_result_text_ele.text
            return bet_result_text
        except:
            return ''

    def operate_1x2(self, bet_name, home, away, period_kw=''):
        ''' 1x2操作 '''
        if bet_name in mybooks.bet_1x2_list:
            hdp_1x2_init_xpath = '//div[@class="bet-title bet-title_justify" and contains(text(),\
                "1x2%s")]/following-sibling::div'%(period_kw)
        else:
            hdp_1x2_init_xpath = '//div[@class="bet-title bet-title_justify" and (text()=\
                " Double Chance%s ")]/following-sibling::div'%(period_kw)
        if bet_name == '1':
            remain_xpath = '/div/span[contains(text(), "%s")]'%home
        elif bet_name == 'X':
            remain_xpath = '/div/span[contains(text(), "%s")]'%('Draw')
        elif bet_name == '2':
            remain_xpath = '/div/span[contains(text(), "%s")]'%away
        elif (bet_name == '1X') or (bet_name == 'X1'):
            remain_xpath = '/div/span[contains(text(), "%s")]'%(home + ' Or X')
        elif (bet_name == '2X') or (bet_name == 'X2'):
            remain_xpath = '/div/span[contains(text(), "%s")]'%(away + ' Or X')
        elif (bet_name == '12') or (bet_name == '21'):
            remain_xpath = '/div/span[contains(text(), "%s")]'%(('%s Or %s')%(home, away))
        else:
            return False
        hdp_1x2_xpath = hdp_1x2_init_xpath + remain_xpath
        print hdp_1x2_xpath
        hdp_1x2_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
            hdp_1x2_xpath) 
        if not hdp_1x2_ele:
            return False
        if not ele_utils.request_num(hdp_1x2_ele, self._driver):
            return False
        return True

    def format_val(self, val):
        ''' 格式化值 '''
        val_str = str(abs(float(val)))
        front_part, last_part = val_str.split('.')
        if (int(last_part) > 0):
            return str(val)
        elif (front_part == '0') and (last_part == '0'):
            return '0'
        else:
            return str(int(float(val)))

    def operate_ah(self, bet_name, bet_value, home, away, period_kw=''):
        ''' 让分盘操作 '''

        # 判断是否亚洲让分盘
        bet_value_tmp = float(bet_value)
        bet_value_abs = abs(bet_value_tmp)
        bet_value_int = int(bet_value_abs)
        remainder_val = bet_value_abs - bet_value_int        

        if (remainder_val == 0.5) or (remainder_val == 0):
            hdp_ah_init_xpath = '//div[@class="bet-title bet-title_justify" and\
                (text()=" Handicap%s ")]/following-sibling::div'%period_kw
        else:
            asian_handicap_text = 'Asian Handicap'
            # 通过输入框找到找到盘口类 
            if not self.search_input(asian_handicap_text):
                return False
            hdp_ah_init_xpath = '//div[text()=" %s%s "]/following-sibling::div'\
                %(asian_handicap_text, period_kw)
        if float(bet_value) > 0:
            bet_value = '+%s'%(self.format_val(bet_value))
        else:
            bet_value = self.format_val(bet_value)
        if (bet_name == 'AH1') or (bet_name == 'AH 1'):
            remain_xpath = '/div/span[text()="Handiсap %s (%s)"]'%(home, bet_value)
        elif (bet_name == 'AH2') or (bet_name == 'AH 2'):
            remain_xpath = '/div/span[text()="Handiсap %s (%s)"]'%(away, bet_value)
        else:
            return False
        hdp_ah_xpath = hdp_ah_init_xpath + remain_xpath
        print hdp_ah_xpath

        hdp_ah_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
            hdp_ah_xpath)
        if not hdp_ah_ele:
            return False
        if not ele_utils.request_num(hdp_ah_ele, self._driver):
            return False
        return True

    def operate_ou(self, bet_name, bet_value, period_kw=''):
        ''' 大小球操作 '''

        # 判断是否亚洲大小球
        bet_value_tmp = float(bet_value)
        bet_value_abs = abs(bet_value_tmp)
        bet_value_int = int(bet_value_abs)
        remainder_val = bet_value_abs - bet_value_int

        if (remainder_val == 0.5) or (remainder_val == 0):
            hdp_ou_init_xpath = '//div[@class="bet-title bet-title_justify" and\
                (text()=" Total%s ")]/following-sibling::div'%period_kw
        else:
            asian_total_text = 'Asian Total'
            # 通过输入框找到找到盘口类 
            if not self.search_input(asian_total_text):
                return False
            hdp_ou_init_xpath = '//div[text()=" %s%s "]/following-sibling::div'\
                %(asian_total_text, period_kw)
        
        bet_value_str = self.format_val(bet_value)
        if (bet_name == 'TO') or (bet_name == 'Over'):
            remain_xpath = '/div/span[text()="Total Over %s"]'%(bet_value_str)
        elif (bet_name == 'TU') or (bet_name == 'Under'):
            remain_xpath = '/div/span[text()="Total Under %s"]'%(bet_value_str)
        else:
            return False
        hdp_ou_xpath = hdp_ou_init_xpath + remain_xpath
        print hdp_ou_xpath
        hdp_ou_ele = ele_utils.get_include_hide_element_for_wait(self._driver,\
            By.XPATH, hdp_ou_xpath, timeout=4)
        if not hdp_ou_ele:
            return False
        if not ele_utils.request_num(hdp_ou_ele, self._driver):
            return False
        return True

    def single_column(self):
        ''' 选择展示样式（单列） '''
        single_column_xpath = '//div[contains(@class, "single-column")]'
        single_column_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
            single_column_xpath, timeout=5)
        try:
            if single_column_ele:
                single_column_ele.click()
            else:
                return False
        except:
            return False        
        return True

    def search_input(self, hdp_name):
        ''' 输入查询的盘口类  '''
        time.sleep(1)
        search_xpath = '//input[@class="c-search__input"]'
        search_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,
            search_xpath)            
        if not search_ele:
            return False
        search_ele.send_keys(hdp_name)
        return True

    def get_koef(self):
        ''' 获取当前的赔率 '''
        koef_xpath1 = '//div[@class="c-bet-box__bet"]'
        koef_xpath2 = '//span[@id="summ_koef"]'

        is_change = True
        num = 1
        while True:
            if num > 2:
                return ''
            if is_change:
                koef_xpath = koef_xpath1
                is_change = False
            else:
                koef_xpath = koef_xpath2
            koef_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
                koef_xpath, timeout=5)
            if not koef_ele:
                num += 1
                continue
            break
        try:
            koef = koef_ele.text
            return koef
        except:
            return ''

    def reasonable_koef(self, odds, koef):
        ''' 判断赔率是否有利润 '''
        try:
            odds = float(odds)
            koef = float(koef)
        except:
            return False
        if koef == 0:
            return False
        min_koef = koef - 0.05
        max_koef = koef + 0.05
        if (odds >= min_koef) and (odds <= max_koef):
            return True
        else:
            return False
        
    def send_stake(self, stake):
        ''' 输入投注金额 '''
        stake_input_xpath1 = '//input[contains(@class, "c-spinner__input")]'
        stake_input_xpath2 = '//input[@id="bet_input"]'
        is_change = True
        num = 1
        while True:
            if num > 2:
                return False
            if is_change: 
                stake_input_xpath = stake_input_xpath1
                is_change = False
            else:
                stake_input_xpath = stake_input_xpath2
            stake_input_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
                stake_input_xpath)
            if not stake_input_ele:
                num += 1
                continue
            break
        stake_input_ele.send_keys(str(stake))
        return True

    def close_window_play_png(self):
        ''' 关闭比赛窗口 '''
        close_xpath = '//span[@class="iconsBlock"]/a[@title="Close"]'
        close_ele = ele_utils.get_element_for_wait(self._driver, By.XPATH,
            close_xpath, timeout=2)
        if not close_ele:
            return False
        if not ele_utils.request_num(close_ele, self._driver):
            return False
        return True

    def click_place_bet(self):
        ''' 输入金额后点击确定按钮 '''
        click_place_bet_xpath1 = '//button[@class=\
            "c-btn c-btn--size-l c-btn--block c-btn--gradient c-btn--gradient-accent u-upcase"]'
        click_place_bet_xpath2 = '//input[@id="goPutBetButton"]'
        is_change = True
        num = 1
        while True:
            if num > 2:
                return False
            if is_change:
                click_place_bet_xpath = click_place_bet_xpath1
                is_change = False
            else:
                click_place_bet_xpath = click_place_bet_xpath2
            click_place_bet_ele = ele_utils.get_element_for_wait(self._driver, By.XPATH,
                click_place_bet_xpath, timeout=5)
            if not click_place_bet_ele:
                num += 1
                continue
            break    

        if not ele_utils.request_num(click_place_bet_ele, self._driver):
            return False
        return True

    def max_stake(self):
        ''' 获取最大投注金额 '''
        max_stake_xpath = '//span[@id="summ_max"]'
        max_stake_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,
            max_stake_xpath)
        if not max_stake_ele:
            return '0' 
        try:
            max_stake = max_stake_ele.text
            return max_stake
        except:
            return '0'

    def change_click_ok(self):
        ''' 赔率改变点击ok '''
        change_click_ok_xpath = '//button[@class="ui-button ui-corner-all ui-widget"]'
        change_click_ok_ele = ele_utils.get_include_hide_element_for_wait(self._driver,\
            By.XPATH, change_click_ok_xpath)
        if not change_click_ok_ele:
            return False
        if not ele_utils.request_num(change_click_ok_ele, self._driver):
            return False
        return True

    def click_ok(self):
        ''' 点击确定按钮 '''

        time.sleep(1)
        click_ok_xpath1 = '//button[@class=\
            "c-btn c-btn--size-m c-btn--block c-btn--gradient c-btn--gradient-accent u-upcase"]'
        click_ok_xpath2 = '//span[@class="ui-button-text"  and text()="OK"]'

        is_change = True
        num = 1
        while True:
            print 'click-num:', num
            if num > 2:
                return False
            if is_change:
                click_ok_xpath = click_ok_xpath1
                is_change = False
            else:
                click_ok_xpath = click_ok_xpath2
            click_ok_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,
                click_ok_xpath)
            if not click_ok_ele:
                num += 1
                continue 
            break
        if not ele_utils.request_num(click_ok_ele, self._driver):
            return False
        return True

    def get_balance(self):
        ''' 剩余金额 '''
        balance_xpath = '//p[@class="top-b-acc__amount"]'
        balance_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
            balance_xpath)
        if not balance_ele:
            return 0 
        try:
            balance = balance_ele.text
            return balance
        except:
            return 0 

    def clear_bet(self):
        ''' 关闭投注窗口 '''
        time.sleep(1)
        clear_bet_xpath1 = '//button[@class=\
            "c-bet-box__del c-btn--close c-btn--flat c-btn--size-s c-btn c-btn--icon-only"]'
        clear_bet_xpath2 = '//div[@id="clearAllBetsBlock"]'

        is_change = True
        num = 1
        while True:
            if num > 2:
                return False
            if is_change:
                clear_bet_xpath = clear_bet_xpath1
                is_change = False
            else:
                clear_bet_xpath = clear_bet_xpath2
            clear_bet_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
                clear_bet_xpath)
            if not clear_bet_ele:
                num += 1
                continue
            break
        if not ele_utils.request_num(clear_bet_ele, self._driver):
            return False
        return True

    def choose_period(self, period):
        ''' 时间选择 '''

        if period == '1st quarter':
            period = '1 Half'
        elif period == '2nd quarter':
            period = '2 Half'
        else:
            return False 

        period_xpath = '//a[@class="chosen-single"]'
        period_ele = ele_utils.get_include_hide_element_for_wait(self._driver, By.XPATH,\
            period_xpath)
        if not period_ele:
            return False
        if not ele_utils.request_num(period_ele, self._driver):
            return False
        all_period_list_xpath = '//li[@class="active-result dopEvsWrap-select__item"]'
        all_period_list = ele_utils.get_elements_for_wait(self._driver, By.XPATH,\
            all_period_list_xpath) 
        if not all_period_list:
            return False
        period_ele = ''
        for one_period in all_period_list:
            if period in one_period.text:
                period_ele = one_period
                break
        if not period_ele:
            return False
        if not ele_utils.request_num(period_ele, self._driver):
            return False
        return True

    def back_live_page(self):
        ''' 回到滚球页面 '''
        self._driver.get(self._init_url)
        num = 1
        while True:
            if num > 5:
                return False
            if self._driver.current_url == self._init_url:
                return True
            else:
                num += 1

    def is_srv_connected(self):
        try:
            self._driver.switch_to_default_content()
            return True
        except:
            return False

    def close(self):
        if self._driver:
            self._driver.quit()
        
