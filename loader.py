import urequests

def test_load(chunk_size=256):
    response = urequests.get('http://jsonplaceholder.typicode.com/albums/1', stream=True)
    if response.status_code == 200:
        with open('loaded.dat', 'wb') as f:
            #while True:
            #    chunk = response.content.read(chunk_size)
            #    if not chunk:
            #        break
            f.write(response.content)
    else:
        print("File download failed!: ", response.status_code)
