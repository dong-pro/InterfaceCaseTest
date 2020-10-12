# -*- coding: UTF-8 -*-
# @Time: 2020-03-30 23:56
# @Author: wyd
# @File: test01_企业数据接入_01用户推送.py

import unittest
from setting import *
from common.baseAct import runRequest
from test_data.企业数据接入testdata import API_ALL
from common.genCreditCode import CreditIdentifier
from common.userInfoMaker import createPhoneNumber


class UserPush(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.req = runRequest()
        f = cls.req.openFileToStream(cls.req.caseInfo_file)
        f.write('开始测试%s-' % __name__)
        cls.req.closeFile()
        # f.close()
        headers = client_config.get('dsb_headers')
        cls.baseUrl = server_config.get('dsb_baseUrl')
        cls.req.headers = headers

    @classmethod
    def tearDownClass(cls):
        cls.req.closeFile()
        print("%s end!" % __name__)

    def userPush(self, post_data, api_name):
        url = server_config['base_url'] + API_ALL['用户推送']['url']
        res = runRequest(client_config['dsb_headers']).test_api_encrypt_AES(url, post_data, 'post', apiName=api_name)
        return res

    def test01_A01_用户推送_必填参数(self):
        post_data = API_ALL['用户推送']['postdata']
        post_data['userId'] = CreditIdentifier().genSocialCreditCode()
        post_data['operatorPhone'] = createPhoneNumber()
        res = self.userPush(post_data, '用户推送')
        self.assertIn('成功', res['message'])

    def test02_pass(self):
        print('userpush_test02')
        pass

    def test03_pass(self):
        print('userpush_test03')
        pass

if __name__ == '__main__':
    UserPush().test01_A01_用户推送_必填参数()
