"""
ftp客户端程序
"""
from socket import *
import sys
from time import sleep

# 请求
class FtpClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L')  # 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        # 　ｏｋ表示请求成功
        if data == 'OK':
            # 　接收文件列表
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit("退出程序")

    def do_get(self,file):
        fd = open(file, 'wb')
        filename = file.split("/")[-1]
        self.sockfd.send(('G '+filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            while True:
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send("##".encode())
                self.sockfd.send(data)
        fd.close()


    def do_put(self, filename):
        try:
            f = open(filename,'rb')
        except Exception:
            print("没有该文件")
            return

        # 　发送请求
        filename = filename.split('/')[-1]
        self.sockfd.send(('P ' + filename).encode())
        # 　等待回复
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            while True:
                data = f.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            f.close()
        else:
            print(data)


def request(sockfd):
    ftp = FtpClient(sockfd)
    while True:
        print("list")
        print("get file")
        print("put file")
        print("quit")
        cmd = input("请输入操作：")
        if cmd.strip() == "list":
            ftp.do_list()
        elif cmd.strip() =="quit":
            ftp.do_quit()
        elif cmd[:3] == "get":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_put(filename)


# 网络链接
def main():
    sockfd = socket()
    server_addr = ('127.0.0.1',8080)
    try:
        sockfd.connect(server_addr)
    except Exception:
        print("链接失败")

    # 收发消息
    while True:
        print("1. Data  2. File  3. Image")
        list01 = ['Data','File','Image']
        cls = input("请输入要获取文件：")
        if  cls not in list01:
            print("输入错误")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)

if __name__ == '__main__':
    main()
