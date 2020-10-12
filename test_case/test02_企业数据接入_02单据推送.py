# -*- coding:UTF-8 -*-
# @Time: 2020/3/31 11:24
# @Author: wyd
# @File: test02_企业数据接入_02单据推送.py

import unittest
from common.baseAct import runRequest
from setting import *

class BillPush(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.req = runRequest()
        f = cls.req.openFileToStream(cls.req.caseInfo_file)
        f.write('开始测试%s-' % __name__)
        # cls.req.closeFile()
        f.close()
        headers = client_config.get('dsb_headers')
        cls.baseUrl = server_config.get('dsb_baseUrl')
        cls.req.headers = headers

    @classmethod
    def tearDownClass(cls):
        cls.req.closeFile()
        print("%s end!" % __name__)

    def test01(self):
        print('test02')