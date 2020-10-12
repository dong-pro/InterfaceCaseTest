# -*- coding:UTF-8 -*-
# @Time: 2020/3/30 17:13
# @Author: wyd
# @File: runAll.py

import os
import time
import sys
import platform
import unittest
from setting import *
from common.HTMLTestRunner import HTMLTestRunner

# 将当前模块加载到sys中，方便其他模块使用时import
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(cur_path)
# print(sys.path)

# 加载用例路径
test_case_path = os.path.join(cur_path, 'test_case')

'''生成HTML报告'''
# 查看当前系统
sys_type = platform.system()
if sys_type == 'Windows':
    html_report_path = output_config['report_path']['windows']
else:
    html_report_path = output_config['report_path']['linux']
# html的命名格式,用项目名+时间+html后缀
now_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
html_filename = os.path.join(html_report_path, 'baseServiceResult_' + now_time + '.html')

# time和case的报告路径不区分系统，直接从配置文件读取
time_log = output_config['time_log']
case_log = output_config['case_log']


# 运行全部case
def run_all_case():
    # 存储用例的实例
    suite = unittest.TestSuite()
    discover = unittest.defaultTestLoader.discover(test_case_path, pattern='test*.py', top_level_dir=None)
    with open(html_filename, mode='wb') as file:
        if os.path.exists(time_log):
            os.remove(time_log)
        if os.path.exists(case_log):
            os.remove(case_log)
        for test_suite in discover:
            with open(time_log, mode='a', encoding='utf-8') as time_file:
                for test_case in test_suite:
                    try:
                        suite.addTest(test_case)
                        # suite.addTests(test_case)
                    except Exception as e:
                        # 往time_log里面写入错误信息，错误的命名格式：用例名+用例错误，然后换行
                        time_file.write(str(test_case) + str(e) + '\n')
                        # # 这里为啥要用test_case._exception？？
                        # time_file.write(str(test_case)+str(test_case._exception)+'\n')
                        raise e
        runner = HTMLTestRunner(stream=file, verbosity=1, title='baseService测试报告', description='用例执行情况：')
        result = runner.run(suite)
        # 统计概率占比
        success_count = result.success_count
        fail_total_count = result.failure_count + result.error_count
        total_count = success_count + fail_total_count
        res_count = '%s  %s  %s  %s' % (total_count, success_count, fail_total_count, html_filename)
        print(res_count)
    return (total_count, fail_total_count)


def run():
    results = run_all_case()
    sys.exit(results[1])


run()
