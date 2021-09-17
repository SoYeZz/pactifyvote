import requests
import time
import random
import string
from threading import Thread
from twocaptcha import TwoCaptcha
from proxy import Proxy

def read_lines(path):
    """ Read all lines in C# style """
    list_of_lines = []

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
        for line in lines:
            line = line.rstrip('\n')
            list_of_lines.append(line)

    return list_of_lines

def get_n():
    digs = string.digits + string.ascii_letters
    x = int(2147483647 * random.uniform(0, 1)) & 2147483647
    base = 16
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


class Bot:
    def __init__(self, proxy = ''):
        self.session = requests.Session()
        self.player = ''
        self.provider = ''
        self.n = get_n()
        self.waitingTime = 0
        self.token = ''
        if proxy != '':
            self.session.proxies = {'https': f'http://{proxy}', 'http': f'http://{proxy}'}
            self.proxy = proxy
    
    def print(self, text):
        print(f'{self.player}: {text}')

    def get_first_step_json(self, player):
        return {"player":player,"server":"pactify"}

    def first_step(self, player):
        req = self.session.post('https://ascentia-votes.ipv4dns.fr/api/check', json=self.get_first_step_json(player)).json()
        self.player = req["player"]["id"]
        self.provider = req["providers"][0]["id"]
        print(self.provider)

    def second_step(self):
        url = 'https://ascentia-votes.ipv4dns.fr/api/wall/begin'
        solver = TwoCaptcha('5f7db765f6574a90bf6f15b79a4461ca')
        if self.player == '' or self.provider == '':
            raise Exception('fuck you nigga')
        captcha_code = solver.recaptcha('6LdT9gAVAAAAANWhLhFGJLoB7DJgWRTSr1HIEWBu', f'https://votes.ascentia.fr/wall?pl={self.player}&pr={self.provider}&n={self.n}')['code']
        print('captcha code:' + captcha_code)
        json = {"player": self.player, "provider": self.provider, "captcha": captcha_code}
        print(json)
        response = self.session.post(url, json=json)
        print(response.text)
        print(response.json())
        self.token = response.json()['token']
        self.waitingTime = response.json()['waitingTime']
        self.print('token: ' + self.token)
        self.print('waiting time: ' + str(self.waitingTime))

    def third_step(self):
        
        time.sleep(self.waitingTime + 1)
        url = 'https://ascentia-votes.ipv4dns.fr/api/wall/end'
        json = {"token": self.token}
        self.session.post(url, json=json)
        #print(response.text)
    
    def final_step(self):
        json = {"player":self.player,"provider":self.provider,"token":self.token,"reward":"vip_points"}
        
        url = 'https://ascentia-votes.ipv4dns.fr/api/validate'
        self.print(self.session.post(url, json=json).text)

    def start(self, player):
        print(f'Started voting for: {player}')
        self.first_step(player)
        self.second_step()
        self.third_step()
        self.final_step()


p = Proxy('US')
p.get_working_proxies()



usernames = read_lines('usernames.txt')
print(f'Usernames loaded: {str(len(usernames))}')

proxy_count = input('How much proxies you want: ')
delay = input('Delay between each vote (in seconds): ')





def threadedfunc(proxy, username):
    Bot(proxy).start(username)

while True:
    while True:
        if(int(proxy_count) < len(p.working_proxies)):
            # start checking threaded
            if delay == '0':
                for username in usernames:
                    Thread(target=threadedfunc, args=(p.get_next(), username)).start()
            else:
                for username in usernames:
                    Bot(p.get_next()).start(username)
                    print(f'Waiting {delay} for the next vote')
                    time.sleep(int(delay))
                    print(f'Done waiting starting next one if there is')
            break
        else:
            print(f'Waiting for proxies: {str(len(p.working_proxies))} working proxies')
        time.sleep(1)
    print("Done voting, waiting 3 hours")
    time.sleep(10900)


print('end')