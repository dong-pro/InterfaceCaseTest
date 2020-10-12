# -*- coding:UTF-8 -*-
# @Time: 2020/3/31 9:56
# @Author: wyd
# @File: 企业数据接入testdata.py.py

import setting

API_ALL = {
    '用户推送': {
        'url': '/aaa/bbb',
        'postdata': {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
        },
        'postdata_required': {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
        },
    },
    '单据推送': {
        'url': '/aaa/bbb',
        'postdata_required': {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
        },
    },
}
