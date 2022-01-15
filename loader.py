import urequests
try:
    import mrequests
except:
    mrequests = None
import ujson
import os
import gc
import btree
try:
    f = open("files_state", "r+b")
except OSError:
    f = open("files_state", "w+b")
files_state = btree.open(f)

def load_json(filename):
    with open(filename,"r") as f:
        data = ujson.loads(f.read())
    return data
config = load_json("config.json")

def exists(filename):
    try:
        with open(filename, 'r'):
            return True
    except:
        return False


def load(url, filename, chunk_size=256):
    response = urequests.get(url, stream=True, headers={'User-Agent': 'request'})
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
    gc.collect()
    return True

def get_files_list(username, repo, branch):
    list_url = "https://api.github.com/repos/"+username+"/"+repo+"/git/trees/"+branch+"?recursive=1"
    response = urequests.get(list_url, stream=True, headers={'User-Agent': 'request'})
    sha = response.raw.read(47).decode().split(':')[1][1:]
    del response
    gc.collect()
    if 'files_state' in files_state:
        if sha == files_state:
            print("Files already up to date")
            return False
        else:
            files_state['files_state'] = sha
            files_state.flush()
    else:
        files_state['files_state'] = sha
        files_state.flush()
    print("File list changed, loading files list..")
    load(list_url, "file-list.json")
    print("File list downloaded")
    return True

def update():
    for listname in ["requirements"]:
        for k, v in config[listname].items():
            result = load(v,k)
    if get_files_list(config['username'], config['repo']):
        target_state = load_json("file-list.json")['tree']
        base_url = "https://raw.githubusercontent.com/"+config['username']+"/"+config['repo']+"/"+config['branch']+"/"
        for file in target_state:
            filename = file['path']
            need_load = False
            if filename not in files_state:
                need_load = True
            else:
                if files_state[filename] != file['sha']:
                    need_load = True
            if need_load:
                load(base_url+filename, filename)
                files_state[filename] = file['sha']
                files_state.flush()
        print(target_state)

