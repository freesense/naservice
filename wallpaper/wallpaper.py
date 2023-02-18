#! /usr/bin/env python3
#coding: utf8

import json, os, re
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup

holdcount = 256
today = datetime.today().strftime('%Y%m%d')

def save(name, date, content):
	savepath = "/nchome/__groupfolders/1/picture/desktop/"
	fpath = savepath + date + "_" + name + ".jpg"
	f = open(fpath, "wb")
	f.write(content)
	f.close()

	files = os.listdir(savepath)
	if len(files) > holdcount:
		files.sort()
		os.remove(os.path.join(savepath, files[0]))

def bing():
	urlbase = "https://cn.bing.com"
	url = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
	rsp = urlopen(url)
	data = rsp.read().decode('utf8')
	obj = json.loads(data)
	urlpath = obj["images"][0]["url"]
	date = obj["images"][0]["startdate"]
	rsp = urlopen(urlbase + urlpath)
	save('bing', date, rsp.read())

def nasa():
	url = 'https://www.nasachina.cn/nasa-image-of-the-day'
	rsp = urlopen(url)
	data = rsp.read().decode('utf8')
	soup = BeautifulSoup(data, 'html.parser')
	imgs = [[x.find('img')['srcset'].split(' '), x.find('span', class_='elementor-post-date').string.strip(' \n\t')] for x in soup.find_all('div', class_='elementor-post__card')]
	imgs = [[[m[i:i+2] for i in range(0, len(m), 2)], d] for m, d in imgs]
	imgs = [[[[url, int(width.strip(',w'))] for url, width in urls], d] for urls, d in imgs]
	for urls, d in imgs:
		urls.sort(key=lambda x: x[1], reverse=True)
	imgs = [[urls[0][0], d]for urls, d, in imgs][0]
	rsp = urlopen(imgs[0])
	mo = re.compile(r'(\d{4})年(\d+)月(\d+)日').search(imgs[1])
	date = f"{mo.group(1)}{int(mo.group(2)):02d}{int(mo.group(3)):02d}"
	save('nasa', date, rsp.read())

def one():
	url = 'http://m.wufazhuce.com/one'
	rsp = urlopen(url)
	data = rsp.read().decode('utf8')
	print(data)

if __name__ == '__main__':
	bing()
	nasa()
	#one()
