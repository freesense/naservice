#! /usr/bin/python3

import json
import urllib.request
import urllib.parse

def main():
    url = 'https://hub.docker.com/v2/repositories/mayflygo/mayfly-go/tags/?page_size=25&page=1&name&ordering'
    header = {
        'Host': 'hub.docker.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        #'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
        'Cache-Control': 'max-age=0',
    }
    request = urllib.request.Request(url, headers=header)
    reponse = urllib.request.urlopen(request).read()
    reponse = str(reponse, encoding='utf-8')

    obj = json.loads(reponse)
    latest = obj['results'][0]['name']
    print(latest)

if __name__ == '__main__':
    try:
        main()
    except:
        print('error')
