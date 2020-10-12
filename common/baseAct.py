# -*- coding: utf-8 -*-
import time
import json

import requests
import urllib.parse
import shutil
import random
import string
import hashlib
import pyotp
import math
import copy
import xxtea
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5, AES

from setting import *
import socket

xxtea_key = encrypt_config['kkk']['xxtea_key']
aes_key = encrypt_config['kkk']['aes_key']
aes_iv = encrypt_config['kkk']['aes_iv']
appId = encrypt_config['kkk']['appId']
rsa_public_key = encrypt_config['kkk']['rsa_public_key']

time_file = output_config['time_log']
caseInfo_file = output_config['case_log']


class HandleFile(object):
    def __init__(self):
        # nowtime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        pass

    # 复制文件夹
    def copyDir(self, sourceDir, targetDir):
        # 目标文件夹不存在则创建.
        # 如果文件夹已经存在，返回一个FileExistsError错误，提示文件已存在
        shutil.copytree(sourceDir, targetDir)
        return 0

    # 复制文件夹里的所有文件
    def copyFiles(self, sourceDir, targetDir):
        if not os.path.exists(targetDir):
            # os.makedirs(targetDir)  # 逐级创建
            os.mkdir(targetDir)
        for file in os.listdir(sourceDir):
            sourceFile = os.path.join(sourceDir, file)
            targetFile = os.path.join(targetDir, file)
            # cover the same files
            if os.path.isfile(sourceFile):
                open(targetFile, "wb").write(open(sourceFile, "rb").read())
        return 0

    # 复制文件夹或文件(单个)
    def copyTo(self, sourceDirFile, targetDirFile):
        if not os.path.exists(targetDirFile):
            os.mkdir(targetDirFile)  # 创建
        shutil.copy(sourceDirFile, targetDirFile)
        return 0

    # 移动文件夹或文件(单个)
    def moveTo(self, sourceDirFile, targetDirFile):
        if not os.path.exists(targetDirFile):
            os.mkdir(targetDirFile)  # 创建
        shutil.move(sourceDirFile, targetDirFile)
        return 0

    # 重命名文件夹或文件(单个)
    def renameIt(self, sourceDirFile, targetDirFile):
        shutil.move(sourceDirFile, targetDirFile)
        return 0

    # 删除文件夹或文件(单个)
    def removeIt(self, targetDirFile):
        if os.path.isfile(targetDirFile):
            os.remove(targetDirFile)
        elif os.path.isdir(targetDirFile):
            # os.rmdir(targetDirFile)
            shutil.rmtree(targetDirFile)
        else:
            return 1
        return 0

    # 删除文件夹里指定格式的文件
    def removeSuffixFiles(self, targetDir, typelist):
        for file in os.listdir(targetDir):
            targetFile = os.path.join(targetDir, file)
            if os.path.isfile(targetFile) and targetFile.split('.')[1] in typelist:
                os.remove(targetFile)
        return 0

    # 创建文件夹
    def createDir(self, targetDir):
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)  # 逐级创建
        return 0

    # 往指定文件夹写文本文件
    def writeVersionInfo(self, targetDir):
        open(targetDir, "wb").write("Revison:")
        return 0


class runRequest():
    def __init__(self, client=''):
        self.headers = client
        self.time_file = time_file
        self.caseInfo_file = caseInfo_file

    def openFileToStream(self, path, method='a'):
        self.fopen = open(path, method)
        return self.fopen

    def closeFile(self):
        self.fopen.close()

    def rsa_encrypt(self, str):
        rsakey = RSA.importKey(rsa_public_key)  # pulic_key格式一定不能错，必须！！！一定！
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        bytes_ori_password = bytes(str, encoding='utf8')  # 加密的明文必须得转为字节类型
        cipher_text = base64.b64encode(cipher.encrypt(bytes_ori_password))
        return cipher_text

    def encryptRequest_AES(self, data, key, iv):
        PADDING = '\0'
        text = json.dumps(data, ensure_ascii=False, separators=(',', ':'))  # 序列化
        print(text)
        pad_it = lambda s: s + (16 - len(s.encode('utf8')) % 16) * PADDING  # text不足十六位的倍数用空格补充
        generator = AES.new(key.encode('utf8'), AES.MODE_CBC, iv.encode('utf8'))
        crypt = generator.encrypt(pad_it(text).encode('utf8'))
        cryptedStr = base64.b64encode(crypt)
        print(cryptedStr)
        return cryptedStr.decode()

    def encrypt_AES(self, data, key, iv):
        PADDING = '\0'
        text = data
        print(text)
        pad_it = lambda s: s + (16 - len(s.encode('utf8')) % 16) * PADDING
        generator = AES.new(key.encode('utf8'), AES.MODE_CBC, iv.encode('utf8'))
        crypt = generator.encrypt(pad_it(text).encode('utf8'))
        cryptedStr = base64.b64encode(crypt)
        print(cryptedStr)
        return cryptedStr.decode()

    def encryptRequest(self, data, keys):
        postdata_copy = copy.deepcopy(data)
        for jsonkey in postdata_copy:
            if postdata_copy[jsonkey] is None:
                postdata_copy[jsonkey] = 'null'
            value = xxtea.encrypt(str(postdata_copy[jsonkey]), keys)
            postvalue = base64.b64encode(value)
            postdata_copy[jsonkey] = postvalue.decode('utf-8')
        return postdata_copy

    def AES_Decrypt(self, data, key):
        vi = 'AtuaE#I7NZB63VzB'
        data = data.encode('utf8')
        encodebytes = base64.decodebytes(data)
        # 将加密数据转换为bytes类型数据
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
        text_decrypted = cipher.decrypt(encodebytes)
        text_decrypted = text_decrypted.decode().strip(b'\x00'.decode())
        # unpad = lambda s: s[0:-s[-1]]
        # text_decrypted = unpad(text_decrypted)
        # 去补位
        # text_decrypted = text_decrypted.decode('utf8')
        return text_decrypted

    def decryptRequest(self, data, keys):
        print(data)
        postdata_copy = copy.deepcopy(data)
        for jsonkey in postdata_copy:
            value = base64.b64decode(postdata_copy[jsonkey])
            value = xxtea.decrypt(value, keys)
            postdata_copy[jsonkey] = value.decode('utf-8')
        return postdata_copy

    def test_postFileWithinPostdata(self, url, params, apiName='', **kargs):
        # 文件包含在postdata参数里面
        if len(kargs) > 0:
            self.headers = {**self.headers, **kargs}  # 其他的键值信息加到headers里去，比如凭证类，参数格式为token="123456"
        self.headers['Content-Type'] = params.content_type
        print(self.headers)
        try:
            res = requests.post(url=url, data=params, headers=self.headers)
            res.close()
        except UnicodeDecodeError as e:
            print('-----UnicodeDecodeError url:', url)
        except urllib.error.URLError as e:
            print("-----urlError url:", url)
        except socket.timeout as e:
            print("-----socket timout:", url)
        print(res.url)
        res_status = res.status_code  # 返回状态码
        res_fail_reason = res.reason  # 失败原因，正常为空
        ext_path = urllib.parse.urlparse(url).path
        if res_status == 200:
            # 请求耗时统计
            f = self.openFileToStream(self.time_file)
            f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
            res_json = res.json()  # json格式内容

            f_case = self.openFileToStream(self.caseInfo_file)
            postdata = params.__dict__.get('fields')
            multipartFile = {}
            if 'multipartFile' in postdata.keys():
                multipartFile = {'multipartFile': postdata.get('multipartFile')}
                postdata.pop('multipartFile')
                postdata = self.decryptRequest(postdata, xxtea_key)
            postdata = {**multipartFile, **postdata}
            f_case.write(apiName + "---" + url + "---" + str(postdata) + "--- " + str(res_json) + "\n")
            print("%s_返回数据：%s" % (apiName, res_json))
            return res_json
        else:
            fail_msg = '状态码%s:%s' % (res_status, res_fail_reason)
            self.openFileToStream(self.time_file).write(
                ext_path + " " + str(res.elapsed.total_seconds()) + " " + fail_msg + "\n")
            print('HTTP请求失败返回状态码是：%s，错误原因：%s' % (res_status, res_fail_reason))
            self.openFileToStream(self.caseInfo_file).write(
                apiName + "---" + url + + "---" + str(params) + "---" + fail_msg + "\n")
            print('HTTP请求失败返回状态码是：%s，错误原因：%s' % (res_status, res_fail_reason))

    def test_postFile(self, url, params, files, apiName='', **kargs):
        if len(kargs) > 0:
            self.headers = {**self.headers, **kargs}  # 其他的键值信息加到headers里去，比如凭证类，参数格式为token="123456"
        if len(params) == 0:
            # res = requests.post(url=url, data={}, headers=self.headers)
            res = requests.post(url=url, data={}, files=files)
        elif 'is_url_para' in list(params.keys()):
            del params["is_url_para"]
            param_parse = urllib.parse.urlencode(params)
            res = requests.post(url=url, data=param_parse, headers=self.headers)
        else:
            res = requests.post(url=url, data=params, files=files)
        print(res.url)
        res_status = res.status_code  # 返回状态码
        res_fail_reason = res.reason  # 失败原因，正常为空
        ext_path = urllib.parse.urlparse(url).path
        if res_status == 200:
            # 请求耗时统计
            f = self.openFileToStream(self.time_file)
            f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
            res_json = res.json()  # json格式内容
            print("%s_返回数据：%s" % (apiName, res_json))
            return res_json
        else:
            fail_msg = '状态码%s:%s' % (res_status, res_fail_reason)
            self.openFileToStream(self.time_file).write(
                ext_path + " " + str(res.elapsed.total_seconds()) + " " + fail_msg + "\n")
            print('HTTP请求失败返回状态码是：%s，错误原因：%s' % (res_status, res_fail_reason))

    def test_postFile_import(self, url, params, files, apiName='', **kargs):

        headers = {'Accept': 'application/json, text/plain, */*',
                   }
        if len(kargs) > 0:
            headers = {**headers, **kargs}  # 其他的键值信息加到headers里去，比如凭证类，参数格式为token="123456"
        print(headers)
        if len(params) == 0:
            res = requests.post(url=url, params={}, files=files, headers=headers)
        elif 'is_url_para' in list(params.keys()):
            del params["is_url_para"]
            param_parse = urllib.parse.urlencode(params)
            res = requests.post(url=url, data=param_parse, files=files, headers=headers)
        else:
            try:
                res = requests.post(url=url, data=params, files=files, headers=headers)
            except UnicodeDecodeError as e:

                print('-----UnicodeDecodeError url:', url)

            except urllib.error.URLError as e:
                print("-----urlError url:", url)

            except socket.timeout as e:
                print("-----socket timout:", url)
        print(res.url)
        res_status = res.status_code  # 返回状态码
        res_fail_reason = res.reason  # 失败原因，正常为空
        ext_path = urllib.parse.urlparse(url).path
        if res_status == 200:
            # 请求耗时统计
            f = self.openFileToStream(self.time_file)
            f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
            res_json = res.json()  # json格式内容
            print("%s_返回数据：%s" % (apiName, res_json))
            return res_json
        else:
            fail_msg = '状态码%s:%s' % (res_status, res_fail_reason)
            self.openFileToStream(self.time_file).write(
                ext_path + " " + str(res.elapsed.total_seconds()) + " " + fail_msg + "\n")
            print('HTTP请求失败返回状态码是：%s，错误原因：%s' % (res_status, res_fail_reason))

    def test_getFile(self, url, params, apiName='', **kargs):
        print('请求报文：%s' % params)
        if len(kargs) > 0:
            self.headers = {**self.headers, **kargs}  # 其他的键值信息加到headers里去，比如凭证类，参数格式为token="123456"
        params_str = json.dumps(params)
        if len(params) == 0:
            res = requests.get(url=url, headers=self.headers)
        elif 'is_url_para' in list(params.keys()):  # 针对url字符串格式的参数的接口加上key：is_url_para
            del params["is_url_para"]
            param_parse = "?" + urllib.parse.urlencode(params)
            res = requests.get(url=url + param_parse, headers=self.headers)
        else:  # json格式为默认
            res = requests.get(url=url, params=params_str, headers=self.headers)
        print(res.url)
        res_status = res.status_code
        res_headers = res.headers  # 响应头
        res_fail_reason = res.reason  # 失败原因，正常为空
        ext_path = urllib.parse.urlparse(url).path
        if res_status == 200:
            try:
                res_json = res.json()  # 返回数据不带文件内容（多用于下载失败情形）
                # 请求耗时统计
                f = self.openFileToStream(self.time_file)
                f_case = self.openFileToStream(self.caseInfo_file)
                f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
                f_case.write(apiName + "---" + url + "---" + str(params) + "--- " + str(res_json) + "\n")
                print("%s_返回数据：%s" % (apiName, res_json))
                return res_status, res_json
            except Exception as e:
                res_content = res.content  # 文件的二进制内容
                # res_content = res.text  # 文件的文本内容（str格式乱码表示，输出内容较多慎用！）
                # 请求耗时统计
                f = self.openFileToStream(self.time_file)
                f_case = self.openFileToStream(self.caseInfo_file)
                f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
                f_case.write(apiName + "---" + url + "---" + str(params) + "--- " + "\n")
                fileType = res_headers['Content-Type'].split(';')[0]
                print("%s_返回的文件类型为%s，内容为%s" % (apiName, fileType, res_content))
                return res_status, fileType
        else:
            fail_msg = '状态码%s:%s' % (res_status, res_fail_reason)
            self.openFileToStream(self.time_file).write(
                ext_path + " " + str(res.elapsed.total_seconds()) + " " + fail_msg + "\n")
            self.openFileToStream(self.caseInfo_file).write(
                apiName + "---" + url + "---" + str(params) + "---" + fail_msg + "\n")
            print('HTTP请求失败返回%s' % fail_msg)
            return res_status, res_fail_reason

    def test_api(self, url, params, method, apiName='', **kargs):
        print('请求方法%s,报文：%s' % (method, params))
        headers = self.headers
        params_urlencode = urllib.parse.urlencode(params)
        if 'application/json' in headers['Content-Type']:
            params_str = json.dumps(params)
        elif 'application/x-www-form-urlencoded' in headers['Content-Type']:
            params_str = params_urlencode
        else:
            print('不支持的Content-Type类型')
            return 1
        if len(kargs) > 0:
            headers = {**headers, **kargs}  # 其他的键值信息加到headers里去，比如凭证类，参数格式为token="123456"
        res = ""
        if method == "get":
            if len(params) == 0:
                res = requests.get(url=url, headers=headers)
            else:  # 默认为urlencode格式
                param_parse = "?" + params_urlencode
                res = requests.get(url=url + param_parse, headers=headers)
        elif method == "put":
            res = requests.put(url=url, data=params_str, headers=headers)
        elif method == "patch":
            res = requests.patch(url=url, data=params_str, headers=headers)
        elif method == "delete":
            res = requests.delete(url=url, data=params_str, headers=headers)
        elif method == "post":
            res = requests.post(url=url, data=params_str, headers=headers)
        print(res.url)
        res_status = res.status_code  # 返回状态码
        res_fail_reason = res.reason  # 失败原因，正常为空
        ext_path = urllib.parse.urlparse(url).path
        if res_status == 200:
            # 请求耗时统计
            f = self.openFileToStream(self.time_file)
            f_case = self.openFileToStream(self.caseInfo_file)
            f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
            res_json = res.json()  # json格式内容
            if apiName != '获取token':
                f_case.write(apiName + "---" + url + "---" + str(params) + "--- " + str(res_json) + "\n")
            print("%s_返回数据：%s" % (apiName, res_json))
            return res_json
        else:
            fail_msg = '状态码%s:%s' % (res_status, res_fail_reason)
            self.openFileToStream(self.time_file).write(
                ext_path + " " + str(res.elapsed.total_seconds()) + " " + fail_msg + "\n")
            if apiName != '获取token':
                self.openFileToStream(self.caseInfo_file).write(
                    apiName + "---" + url + "---" + str(params) + "---" + fail_msg + "\n")
            print('HTTP请求失败返回状态码是：%s，错误原因：%s' % (res_status, res_fail_reason))
            return res_status

    def test_api_encrypt(self, url, params, method, apiName='', **kargs):
        headers = self.headers
        if len(kargs) > 0:
            headers = {**headers, **kargs}  # 其他的键值信息加到headers里去，比如凭证类，参数格式为token="123456"
        encrypt_params = self.encryptRequest(params, xxtea_key)
        params_str = json.dumps(encrypt_params)
        res = ""
        if method == "get":
            param_parse = "?" + urllib.parse.urlencode(encrypt_params)
            res = requests.get(url=url + param_parse, headers=headers)
        elif method == "post":
            res = requests.post(url=url, data=params_str, headers=headers)
        print(res.url)
        res_status = res.status_code  # 返回状态码
        res_fail_reason = res.reason  # 失败原因，正常为空
        ext_path = urllib.parse.urlparse(url).path
        if res.status_code == 200:
            # 请求耗时统计
            f = self.openFileToStream(self.time_file)
            f_case = self.openFileToStream(self.caseInfo_file)
            f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
            res_json = res.json()  # json格式内容
            if apiName != '获取token':
                f_case.write(apiName + "---" + str(encrypt_params) + "--- " + str(res_json) + "\n")
            print("%s_返回数据：%s" % (apiName, res_json))
            return res_json
        else:
            fail_msg = '状态码%s:%s' % (res_status, res_fail_reason)
            self.openFileToStream(self.time_file).write(
                ext_path + " " + str(res.elapsed.total_seconds()) + " " + fail_msg + "\n")
            if apiName != '获取token':
                self.openFileToStream(self.caseInfo_file).write(
                    apiName + "---" + str(encrypt_params) + "---" + fail_msg + "\n")
            print('HTTP请求失败返回状态码是：%s，错误原因：%s' % (res_status, res_fail_reason))

    def test_api_encrypt_AES(self, url, params, method, apiName='', **kargs):
        headers = self.headers
        if len(kargs) > 0:
            headers = {**headers, **kargs}  # 其他的键值信息加到headers里去，比如凭证类，参数格式为token="123456"
        aes_str = self.encryptRequest_AES(params, aes_key, aes_iv)
        sign = Generators().md5((aes_key + aes_str + appId + aes_iv).replace('\r\n', ''))
        headers['x-bigtree-sign'] = sign
        aes_data = urllib.parse.quote(aes_str)
        print(aes_data)
        data = json.dumps({"data": aes_data})
        # print(headers)
        # print(url)
        # print(str(data))
        res = requests.post(url=url, data=data, headers=headers)
        print(res)
        res_status = res.status_code  # 返回状态码
        res_fail_reason = res.reason  # 失败原因，正常为空
        ext_path = urllib.parse.urlparse(url).path
        if res.status_code == 200:
            # 请求耗时统计
            f = self.openFileToStream(self.time_file)
            f_case = self.openFileToStream(self.caseInfo_file)
            f.write(ext_path + " " + str(res.elapsed.total_seconds()) + "\n")
            res_json = res.json()  # json格式内容
            if apiName != '获取token':
                f_case.write(apiName + "---" + url + "---" + str(params) + "--- " + str(res_json) + "\n")
            print("%s_返回数据：%s" % (apiName, res_json))
            return res_json
        else:
            fail_msg = '状态码%s:%s' % (res_status, res_fail_reason)
            self.openFileToStream(self.time_file).write(
                ext_path + " " + str(res.elapsed.total_seconds()) + " " + fail_msg + "\n")
            if apiName != '获取token':
                self.openFileToStream(self.caseInfo_file).write(
                    apiName + "---" + url + "---" + str(data) + "---" + fail_msg + "\n")
            print('HTTP请求失败返回状态码是：%s，错误原因：%s' % (res_status, res_fail_reason))


class Generators(object):
    def __init__(self):
        pass

    def random_text(self, min_length=1, max_length=8):
        if max_length > min_length:
            local_max_len, local_min_len = max_length, min_length
        else:
            local_max_len, local_min_len = min_length, max_length
        legal_characters = string.ascii_letters
        random.Random()
        while (True):
            length = random.randint(local_min_len, local_max_len)
            array = [random.choice(legal_characters) for x in range(0, length)]
            return ''.join(array)

    def random_int(self, min_value=0, max_value=2147483647):
        """ Random integer generator for up to 32-bit signed ints """
        random.Random()
        while (True):
            return random.randint(min_value, max_value)

    def random_float(self, min_value=None, max_value=1, digits=8):
        random.uniform(0, max_value)
        if min_value is None:
            min_value = 1 / (10 ** digits)
        rand = random.uniform(min_value, max_value)
        # 控制随机数的精度round(数值，精度)
        return (round(rand, digits))

    def sha1(self, input):
        if isinstance(input, bytes):
            tmp = input
        else:
            tmp = str(input).encode()
        return hashlib.sha1(tmp).hexdigest()

    def md5(self, string):
        md = hashlib.md5()
        md.update(string.encode())
        res = md.hexdigest()
        return res

    def timestamp(self, format=None):
        if format is None:
            return int(time.time())
        else:
            try:
                return time.strftime(format)
            except TypeError as e:
                return time.strftime('%Y-%m-%d %X')

    def googleCode(self, googleKey):
        totp = pyotp.TOTP(googleKey)
        return totp.now()

    def sin(self, degree_step=0.00000001, addend=0, multiplier=1):
        v = 0
        while True:
            o = math.sin(v % (math.pi * 2))
            v += degree_step
            if v >= math.pi * 2:
                v = 0
            yield o * multiplier + addend


if __name__ == '__main__':
    # json_dict = {'fontFamily': '微软雅黑', 'fontSize': 12, 'BaseSettings': {'font': 1, 'size': {'length': 40, 'wigth': 30}}}
    # key = '#z6?*y75eqbfarS8'
    # iv = 'AtuaE#I7NZB63VzB'
    # runRequest().encryptRequest_AES(json_dict, key,iv )
    Generators().random_text(1, 5)
