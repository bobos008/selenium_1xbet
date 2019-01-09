# coding=utf-8

from selenium import webdriver
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def get_cur_line():
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    return '%s, %s, ' % (f.f_code.co_name, str(f.f_lineno))


def get_element_for_wait(driver, by, by_s, timeout=10):
    try:    
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, by_s)))
        ele = driver.find_element(by, by_s)
        return ele
    except:
        pass
    return ''

def get_include_hide_element_for_wait(driver, by, by_s, timeout=20):
    try:
        ele = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, by_s))
        )
        return ele
    except Exception as error:
           pass
    return ''


def get_include_hide_elements_for_wait(driver, by, by_s, timeout=20):
    try:
        ele_list = WebDriverWait(driver, timeout).until(
            EC.visibility_of_all_elements_located((by, by_s))
        )
        return ele_list
    except Exception as error:
        pass
    return [] 


def get_elements_for_wait(driver, by, by_s, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, by_s)))
        ele = driver.find_elements(by, by_s)
        return ele
    except Exception, e:
        pass
    return ''


def request_num(element, driver, allow_num=5):
    ''' 请求次数 '''
    num = 1 
    while True:
        print 'num:', num
        if num > allow_num:
            return False
        try:
            element.click()
        except:
            num += 1
            time.sleep(2)
            continue
        return True
