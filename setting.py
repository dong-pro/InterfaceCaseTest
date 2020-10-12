# -*- coding: UTF-8 -*-
# @Time: 2020-03-30 21:44
# @Author: wyd
# @File: setting.py

'''
配置文件
'''

import os

cur_path = os.path.abspath(os.path.dirname(__file__))

# 测试环境
appId = 'xxx'
tenantId = 'xxx'
aes_key = 'xxx'

# 输出配置
output_config = {
    'report_path': {
        # 不分环境，只区分系统
        'linux': './test_result/',
        'windows': os.path.join(cur_path, 'test_result'),
    },
    'time_log': os.path.join(cur_path, 'test_result/time.txt'),
    'case_log': os.path.join(cur_path, 'test_result/caseInfo.txt'),
}

# 客户端配置
client_config = {
    'dsb_headers': {
        "Content-Type": "application/json;charset=utf-8",
        "x-bigtree-appid": appId,
        "x-bigtree-nonce": "xxx",
        "x-bigtree-sign": ""
    }
}
# 服务器地址
server_config = {
    'base_url': 'http://aaa.bbb.ccc.com',
}

# 加密签名字符串

encrypt_config = {
    'kkk': {
        'xxtea_key': 'xxx',
        'appId': appId,
        'aes_key': aes_key,
        'aes_iv': 'xxx',
        'rsa_public_key': """-----BEGIN PUBLIC KEY-----
                            -----END PUBLIC KEY-----""",
        'rsa_private_key': """-----BEGIN RSA PRIVATE KEY-----
                            -----END RSA PRIVATE KEY-----""",
    },
    'pf_signkey': {
        'signkey': 'xxx'
    },
}
