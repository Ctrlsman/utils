#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import re
from splinter.browser import Browser

#####################################################
# global instance
CLOASE_AFTER_TEST = False
GBK = "gbk"
UTF8 = "utf8"

#####################################################
# encoding for console
reload(sys)
sys.setdefaultencoding(UTF8)

#####################################################
# small method
encoding = lambda x:x.encode('gbk')

#####################################################
def output(x):
    """
        encode and print
    """
    print encoding(x)

def resultMsg(x):
    """
        judge result and print, x : True or False
    """
    if x == True:
        print 'pass'
    else:
        print '[X]not pass'
    print '--------------------------'

def checkresult(x):
    """
        check result message, x : the error message u want
    """
    resultMsg(browser.is_text_present(x))

def testLogin(desc, username, password, result):
    """
        fill login form message and submit, check result message and print
    """
    output(desc)
    browser.fill('TPL_username',username.decode(UTF8))
    browser.fill('TPL_password',password.decode(UTF8))
    browser.find_by_value('登录').first.click()
    checkresult(result)

__testUrl = 'http://waptest.taobao.com/login/login.htm?tpl_redirect_url=http%3A%2F%2Fm.taobao.com%2F'

# chrome driver : http://code.google.com/p/selenium/wiki/ChromeDriver
# already support firefox
browser = Browser()
browser.visit(__testUrl)

output("测试页面:"+browser.title)

try:
    # test login
    testLogin('测试未输入用户名','','','请输入会员名')
    testLogin('测试未输入密码','qd_test_001','','请输入密码')
    testLogin('测试帐户不存在','这是一个不存在的名字哦','xxxxxxx','该账户名不存在')
    testLogin('测试成功登录','qd_test_001','taobao1234','继续登录前操作')

    # test find password
    output("测试[找回密码]链接")
    browser.visit(__testUrl)
    backPasswordLink = browser.find_link_by_text('取回密码')
    if 1 == len(backPasswordLink):
        backPasswordLink.first.click()
        ru = re.findall(re.compile(".*(reg/gp.htm).*", re.IGNORECASE), browser.url)
        if ru is not None:
            checkresult('找回密码')
        else:
            output("测试找回密码链接失败")

except Exception,x:
    print x

if CLOASE_AFTER_TEST:
    browser.quit()