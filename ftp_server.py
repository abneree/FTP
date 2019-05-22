"""
ftp 文件服务器
并发网络功能训练
"""

from socket import *
from threading import Thread
import signal
import os
import time

signal.signal(signal.SIGCHLD,signal.SIG_IGN)

# 全局变量
FTP = "/home/tarena/FTP/"

# 将客户请求封装为类
class FtpServer:
    def __init__(self,connfd,path):
        self.connfd = connfd
        self.path = path

    def do_list(self):
        files = os.listdir(self.path)
        print(files)
        if not files:
            self.connfd.send("文件为空".encode())
            return
        else:
            self.connfd.send(b'OK')
        fs = ""
        for i in files:
            if i[0] !='.' and os.path.isfile(self.path+i):
                fs+=i+'\n'
            print(fs)
        self.connfd.send(fs.encode())

    def do_get(self,filename):
        try:
            fd = open(self.path+filename,'rb')
        except Exception:
            self.connfd.send('文件不存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)

        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

    def do_put(self,filename):
        if os.path.exists(self.path + filename):
            self.connfd.send("该文件已存在".encode())
            return
        self.connfd.send(b'OK')
        fd = open(self.path + filename,'wb')
        # 接收文件
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()

def handle(connfd):
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP+cls+"/"
    ftp = FtpServer(connfd,FTP_PATH)
    while True:
        data = connfd.recv(1024).decode()
        print(FTP_PATH,":",data)
        if not data or data[0] == "Q":
            return
        elif data =='L':
            ftp.do_list()
        elif data[0] == 'G':
            data = data.split(" ")[-1]
            ftp.do_get(data)

# 网络搭建
def main():
    ADDR = ('0.0.0.0',18888)
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(3)
    print("wait for connet......")

    while True:
        try:
            connfd , addr = s.accept()
            print(connfd.getpeername())
        except KeyboardInterrupt:
            print("退出服务")
            return
        except Exception as e :
            print(e)
            continue

        print("链接的客户端：",addr)
        # 创建线程处理请求
        client = Thread(target=handle,args=(connfd,))
        client.setDaemon(True)
        client.start()

if __name__ == '__main__':
    main()
