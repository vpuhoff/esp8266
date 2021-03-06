import urequests
import ujson
import os
import machine
import uos as os
import gc
import btree
try:
    f = open("files_state", "r+b")
except OSError:
    f = open("files_state", "w+b")
files_state = btree.open(f)

def isdir(file):
    return list(os.stat(file))[-1] == 0

def split(p):
    sep = '/'
    i = p.rfind(sep) + 1
    head, tail = p[:i], p[i:]
    if head and head != sep*len(head):
        head = head.rstrip(sep)
    return head, tail

def makedirs(name, exist_ok=True):
    head, tail = split(name)
    if not tail:
        head, tail = split(head)
    if head and tail and not exists(head):
        try:
            makedirs(head, exist_ok=exist_ok)
        except FileExistsError:
            pass
        cdir = '.'
        if isinstance(tail, bytes):
            cdir = bytes('.', 'ASCII')
        if tail == cdir:
            return
    try:
        os.mkdir(name)
    except OSError:
        if not exist_ok or not isdir(name):
            raise

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

def load(url, filename, chunk_size=64):
    if split(filename)[0] is not None:
        folder = split(filename)[0]
        makedirs(folder)
    response = urequests.get(url, stream=True, headers={'User-Agent': 'request', 'Cache-Control': 'no-cache'})
    chunk = b''
    if response.status_code == 200:
        if exists(filename+".new"):
            os.remove(filename+".new")
        with open(filename+".new", 'wb') as f:
            while True:
                chunk = response.raw.read(chunk_size)
                if not chunk or len(chunk) == 0:
                    break
                f.write(chunk)
                del chunk
            print("File " + filename + " download success!: ", response.status_code)
        if exists(filename):
            os.remove(filename)
        os.rename(filename+".new", filename)
    else:
        print("File " + filename + " download failed!: ", response.status_code)
    del response
    gc.collect()
    return True

def get_files_list(username, repo, branch):
    list_url = "https://api.github.com/repos/"+username+"/"+repo+"/git/trees/"+branch+"?recursive=1"
    response = urequests.get(list_url, stream=True, headers={'User-Agent': 'request'})
    sha = response.raw.read(47).decode().split(':')[1][1:]
    print("Current state:", sha)
    del response
    gc.collect()
    if 'files_state' in files_state:
        if sha == files_state['files_state'].decode():
            print("Files already up to date")
            return True
        else:
            files_state['files_state'] = sha
            files_state.flush()
    else:
        files_state['files_state'] = sha
        files_state.flush()
    load(list_url, "file-list.json")
    return True

def update():
    machine.freq(160000000)
    for listname in ["requirements"]:
        for k, v in config[listname].items():
            if not exists(k):
                load(v,k)
    gc.collect()
    if get_files_list(config['username'], config['repo'], config['branch']):
        target_state = {}
        if exists("file-list.json"):
            target_state = load_json("file-list.json")['tree']
        current_commit = files_state['files_state'].decode()
        base_url = "https://raw.githubusercontent.com/"+config['username']+"/"+config['repo']+"/"+current_commit+"/"
        for file in target_state:
            filename = file['path']
            if file['type'] == 'blob':
                need_load = False
                if filename not in files_state:
                    need_load = True
                else:
                    if files_state[filename].decode() != file['sha']:
                        need_load = True
                if need_load:
                    load(base_url+filename, filename)
                    files_state[filename] = file['sha']
                    files_state.flush()
                    gc.collect()
        gc.collect()
        files_state.close()
    machine.freq(80000000)
    print("Restart system...")
    machine.soft_reset()
