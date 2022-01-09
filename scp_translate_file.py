# -*- coding: utf-8 -*-
import paramiko
import logging
import os
import time

logger = logging.getLogger('scp_log')  # 设置日志
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')     # 设置日志输出内容
log_file_handler = logging.FileHandler('scp_log')
log_file_handler.setFormatter(formatter)
log_file_handler.setLevel(logging.INFO)
logger.addHandler(log_file_handler)

host = '221.4.223.114'     # 字幕服务器，需要向字幕服务器上传字幕文件
port = 8222                   # SSH端口
user = 'root'
password = 'SxwqfLGOlGzH0iwu'
transport = paramiko.Transport((host, port))
transport.connect(username=user, password=password)   # 连接字幕服务器
sftp = paramiko.SFTPClient.from_transport(transport)


def print_and_log(msg):
    try:
        print(msg)
        logger.info(msg)
    except Exception as err:
        print('Error: Unable to print msg!!!')
        print(err)
        logger.info('Error: Unable to print msg!!!')
        logger.info(err)


def scp_file(source_file, target_file):
    global transport
    global sftp
    count = 0
    while count < 3:
        try:
            sftp.put(source_file, target_file)
        except Exception as err:
            e = str(err)
            if 'close' in e:
                try:
                    transport.close()
                except:
                    pass
                time.sleep(30)
                transport = paramiko.Transport((host, port))
                transport.connect(username=user, password=password)  # 连接字幕服务器
                sftp = paramiko.SFTPClient.from_transport(transport)
                count += 1
                continue
            print_and_log('Error: Unable to transfer file: ' + source_file + ' -->> ' + e)
            return False
        else:
            return True


def scp_folder(remote_folder):
    global transport
    global sftp
    count = 0
    while count < 3:
        try:
            sftp.mkdir(remote_folder)
        except Exception as err:
            e = str(err)
            if 'close' in e:
                try:
                    transport.close()
                except:
                    pass
                time.sleep(30)
                transport = paramiko.Transport((host, port))
                transport.connect(username=user, password=password)  # 连接字幕服务器
                sftp = paramiko.SFTPClient.from_transport(transport)
                count += 1
                continue
            print_and_log('Error: Unable to transfer folder: ' + remote_folder + ' -->> ' + e)
            return False
        else:
            return True


if __name__ == '__main__':
    for imdb in os.listdir('/data/movies/'):
        if 'tmp' in imdb:
            continue
        scp_folder('/home/movies/'+imdb)
        for language in os.listdir('/data/movies/'+imdb):
            scp_folder('/home/movies/'+imdb+'/'+language)
            for file in os.listdir('/data/movies/'+imdb+'/'+language):
                scp_file('/data/movies/'+imdb+'/'+language+'/'+file, '/home/movies/'+imdb+'/'+language+'/'+file)
    transport.close()
    print_and_log('--------------finish---------------')
