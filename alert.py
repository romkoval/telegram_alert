import os
import sys
import urllib.request
import urllib.parse
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

def save_last_used(proxy):
    with open('last_used.cache', mode='w') as f:
        f.write(json.dumps(proxy))

def load_last_used() -> dict:
    """ loads last used proxy """
    if not os.path.isfile('last_used.cache'):
        return None
    try:
        with open('last_used.cache', mode='r') as f:
            return json.loads(f.read())
    except Exception as e:
        print(e, file=sys.stderr)
        return None

def install_proxy(attempts):
    proxylist = [get_rand_proxy() for _ in range(attempts)]
    last_used = load_last_used()
    if last_used:
        proxylist.insert(0, last_used)
    for proxy in proxylist:
        print('using proxy:%s %s' % (make_proxy_str(proxy), proxy['country']), end='')
        
        proxy_support = urllib.request.ProxyHandler(make_proxy_str(proxy))
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        try:
            with urllib.request.urlopen('https://telegram.org', timeout=4) as req:
                req.read(10)
            save_last_used(proxy)
            print(' OK')
            return
        except urllib.error.URLError as err:
            print(' ERR')
            print(err, file=sys.stderr)

def print_help():
    print(" Usage: %s api_key chat_id message" % sys.argv[0])

def main():
    if len(sys.argv) < 4:
        print_help()
        return 1
    api_key, chat_id, message = sys.argv[1], sys.argv[2], sys.argv[3]

    install_proxy(attempts=10)
    url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s' % (api_key, chat_id, urllib.parse.quote_plus(message))
    with urllib.request.urlopen(url, timeout=10) as response:
        res = json.loads(response.read())
        if res["ok"]:
            print("message sent: id=%d" % res["result"]["message_id"])
        else:
            print("failed to send")
        return 1 if not res["ok"] else 0

if __name__ == "__main__":
    sys.exit(main())
