# /usr/bin/python2
#coding=utf8

import threading

import multiprocessing
import time
import Queue
import os
import re
import requests

#SHARE_Q = Queue.Queue()  #构造一个不限制大小的的队列
SHARE_Q = multiprocessing.Queue()  #构造一个不限制大小的的队列
_WORKER_THREAD_NUM = 2   #设置线程个数
_WORKER_PROCESS_NUM = 8  #设置进程数量

class MyThread(threading.Thread) :

    def __init__(self, func, q) :
        super(MyThread, self).__init__()
        self.func = func
        self.queue = q

    def run(self) :
        self.func(self.queue)

def worker(q):
    session = requests.Session()
    while not q.empty():
        url, name = q.get() #获得任务
        print "Processing : ", url, name
        with open(name, 'w') as f:
            f.write(session.get(url).content)

def main() :
    global SHARE_Q


for root,dirs,files in os.walk('data'):
    for filespath in files:
        url = os.path.join(root,filespath)
        url = os.path.abspath(url)
        temp = []
        if url.endswith('m3u8'):
            path = os.path.dirname(url)
            new_m3u8_path = os.path.join(path, 'new_video.m3u8')
            content = open(url).read()
            for x in content.split('\n'):
                if x.startswith('http://'):
                    x = x.split('?')[0]
                    _, name = os.path.split(x)
                    save_path = os.path.join(path, name)
                    temp.append(name)
                    if not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
                        #print 'download', x, save_path
                        #os.system('wget %s -O %s' % (x, save_path))
                        SHARE_Q.put([x, save_path])
                        #with open(save_path, 'w') as f:
                            #f.write(requests.get(x).content)
                else:
                    temp.append(x)
            with open(new_m3u8_path, 'w') as f:
                f.write("\n".join(temp))
            #exit()

processs = []
print 'Queue length', SHARE_Q.qsize()

def func(q, max_thread_num):
    threads = []
    for i in xrange(max_thread_num) :
        thread = MyThread(worker, q)
        thread.start()
        threads.append(thread)
    for thread in threads :
        thread.join()

for i in xrange(_WORKER_PROCESS_NUM):
    p = multiprocessing.Process(target=func, args=(SHARE_Q, _WORKER_THREAD_NUM))
    p.start()
    processs.append(p)

while True:
    time.sleep(10)
    print 'Queue length', SHARE_Q.qsize()

for p in processs:
    p.join()