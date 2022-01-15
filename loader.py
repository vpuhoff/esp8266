import urequests
try:
    import mrequests
except:
    mrequests = None
import ujson
import os
import gc

def load_json(filename):
    with open(filename,"r") as f:
        data = ujson.loads(f.read())
    return data

def exists(filename):
    try:
        with open(filename, 'r'):
            return True
    except:
        return False

def get_date(url, header_name='ETag'):
    response = mrequests.head(url, save_headers=True)
    for header in response.headers:
        vars = header.decode().split(':', 1)
        if vars[0].strip() == header_name:
            del response
            return vars[1]
    del response
    gc.collect()


config = load_json("config.json")
if not exists("files-state.json"):
    files_state = {}
else:
    files_state = load_json("files-state.json")


def load(url, filename, chunk_size=256):
    existed = False
    if mrequests:
        remote_date = get_date(url)
        local_date = files_state.get(filename, None)
        #print(local_date, remote_date)
        if remote_date == local_date:
            existed = True
        else:
            files_state[filename] = remote_date
    if not existed:
        response = urequests.get(url, stream=True)
        chunk = b''
        if response.status_code == 200:
            with open(filename+".new", 'wb') as f:
                while True:
                    chunk = response.raw.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
            if exists(filename):
                os.remove(filename)
            os.rename(filename+".new", filename)
            print("File " + filename + " download success!: ", response.status_code)
        else:
            print("File " + filename + " download failed!: ", response.status_code)
        del response
        return True
    else:
        print("File " + filename + " already up to date!: ")
        return False

def save_state():
    with open("files-state.json" ,"wb") as f:
        ujson.dump(files_state, f)
        print("Files state saved success")

def update():
    new_files = False
    for listname in ["requirements","modules"]:
        for k, v in config[listname].items():
            result = load(v,k)
            if result:
                new_files = True
    if new_files:
        save_state()
