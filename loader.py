import urequests
import ujson

def test_load(chunk_size=256):
    headers = {'content-type': 'application/json'}
    # response = urequests.get('https://raw.githubusercontent.com/vpuhoff/esp8266/master/loader.py', headers=headers, stream=True)
    # if response.status_code == 200:
    #     print(response.headers['last-modified'])
    response = urequests.get('https://raw.githubusercontent.com/SpotlightKid/mrequests/master/mrequests.py', stream=True)
    if response.status_code == 200:
        with open('loaded.dat', 'wb') as f:
            #while True:
            #    chunk = response.content.read(chunk_size)
            #    if not chunk:
            #        break
            f.write(response.content)
        print("File download success!: ", response.status_code)
    else:
        print("File download failed!: ", response.status_code)

