import os
import urllib.request
import json
import datetime
import random

def update_proxy_cache(cache_filename):
    with urllib.request.urlopen("https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list") as prox:
        proxylist = prox.read().decode('utf-8')
        with open('proxy.cache', 'w', encoding='utf-8') as cache:
            cache.write(proxylist)

def get_proxy_list():
    cache_filename = 'proxy.cache'
    if os.path.isfile(cache_filename):
        mdate = datetime.datetime.fromtimestamp(os.path.getmtime(cache_filename))
        if mdate.date() != datetime.datetime.now().date():
            update_proxy_cache(cache_filename)
    else:
        update_proxy_cache(cache_filename)
    
    with open(cache_filename, 'r') as proxyf:
        return [p for p in proxyf.read().split('\n') if '{' in p]

def get_rand_proxy():
    prox_str = random.choice(get_proxy_list())
    return json.loads(prox_str)

def make_proxy_str(proxy):
    port = proxy["port"]
    host = proxy["host"]
    htype = proxy["type"]
    return {htype: htype + "://" + host + ":" + str(port)}

def install_proxy():
    proxy = make_proxy_str(get_rand_proxy())
    print('using proxy:%s' % (proxy))
    proxy_support = urllib.request.ProxyHandler(proxy)
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)

def main():
    install_proxy()

    with urllib.request.urlopen('https://telegram.org/') as response:
        print(response.read())

if __name__ == "__main__":
    main()