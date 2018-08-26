import copy
import hashlib
import json
import re
import os
import errno
import shutil
import time

import builders
from io import StringIO

# region globals
DEBUG=True
def get_level(s):
    # return len(s) - len(s.lstrip()) # just \n produces 1
    return len(re.match(r"^[ \t]*",s).group(0))

def get_parts(s,skip_start=True):
    ret=[]
    for part in (s[s.index("-") + 1:] if skip_start else s).split(' - '):
        fpart = part.strip()
        if fpart != '': ret.append(fpart)
    for i in range(max(3 - len(ret), 0)):
        ret.append(None)
    return ret

def get_renderer(item):
    for hook in builders.hooks:
        if re.match("^"+hook[0]+"$",item.get_remote()):
            try:
                if hook[1] is not None:
                    return hook[1]
            except IndexError: pass
    return builders.default_render

def hash_file(file_path):
    m=hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096),b''):
            m.update(chunk)
    return m.hexdigest()

def hash_string(string):
    return hashlib.sha256(str(string).encode('utf-8')).hexdigest()

def cpath(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
#endregion

class ColItem:
    def __init__(self,parent):
        self.parts=[]
        self.parent=parent
        self.skip_render=False

    def parse(self,raw):
        for part in raw.strip().split(' '):
            fpart = part.strip()
            if fpart != '': self.parts.append(fpart)
        for i in range(max(3-len(self.parts),0)):
            self.parts.append(None)

    def render(self):
        if DEBUG: print(self.get_remote())
        save_ret=get_renderer(self)(self, self.parent.get_path())
        d={}
        d['data']=save_ret[1]
        d['timestamp']=int(round(time.time() * 1000))
        d['name']=self.get_name()
        d['source']=self.get_remote()

        return self.parent.get_path(), save_ret[0], d

    #region serialisation
    def get_name(self):
        try:
            ret = self.parts[1]
            if ret is None: raise IndexError
            else: return ret
        except IndexError:
            own_index=0
            for sibling in self.parent.items:
                if sibling is self:
                    break
                own_index+=1
            return str(own_index+1)

    def get_remote(self):
        return self.parts[0]

    def to_string(self):
        ret = ""

        # parts
        for part in self.parts:
            if part is None: continue
            ret += part + " "
        ret += "\n"

        return ret

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
    #endregion

class ColSection:
    def __init__(self, parent):
        self.items=[]
        self.parts=[]
        self.sections=[]
        self.depth=parent.depth+1
        self.parent=parent
        pass

    def parse(self, raw):
        with StringIO(raw) as r:
            start_line=r.readline()
            self.parts = get_parts(start_line)
            # self.depth=get_level(start_line)

            while True:
                line=r.readline()
                if len(line)<=0:break
                if line.lstrip().startswith("-"):
                    # ColSection
                    buf = line
                    start_level = get_level(line)
                    while True:
                        save = r.tell()
                        innerline = r.readline()
                        if len(innerline)>0 and innerline.strip()=="":
                            continue
                        if (get_level(innerline) <= start_level or len(innerline) <= 0) and len(buf)>0:
                            # flush buf
                            sec = ColSection(self)
                            sec.parse(buf)
                            self.sections.append(sec)

                            #backpedal
                            r.seek(save)
                            break
                        else:
                            buf += innerline
                else:
                    # ColItem
                    item = ColItem(self)
                    item.parse(line)
                    self.items.append(item)

    def render(self):
        ret=[]
        cpath(self.get_path())
        # if DEBUG: print(self.get_path(1))
        for section in self.sections:
            ret.extend(section.render())
        for item in self.items:
            if not item.skip_render:
                ret.append((item,item.render()))
        return ret

    def get_items(self):
        ret=[]
        for section in self.sections:
            ret.extend(section.get_items())
        for item in self.items:
            ret.append(item)
        return ret

    #region serialisation
    def get_name(self,name_version=0):
        try:
            return re.sub("\([\s\S]*\)","",self.parts[name_version]).strip().replace(" ","-")
        except:
            return re.sub("\([\s\S]*\)","",self.parts[0]).strip().replace(" ","-")

    def get_path(self, name_version=0):
        path_list = [self.get_name(name_version=name_version)]

        parent=self.parent
        while parent is not None:
            try:
                path_list.append(parent.get_name(name_version=name_version))
            except AttributeError:
                break
            parent=parent.parent
            pass

        ret=''
        for path_part in reversed(path_list):
            ret+=path_part+'/'
        return ret

    def to_string(self,indent="\t"):
        ind=""
        for i in range(self.depth):
            ind+=indent
        ret=""

        #parts
        ret+=ind
        for part in self.parts:
            if part is None: continue
            ret+="- "+part+" "
        ret+="\n"

        #sections
        for section in sorted(self.sections, key=lambda x: x.parts[0]):
            ret+=ind+section.to_string(indent=indent)

        #items
        for item in self.items:
            ret+=ind+ind+item.to_string()
        return ret

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
    #endregion

class ColFile:
    def __init__(self,path):
        self.sections = []
        self.raw = None
        self.meta = ""
        self.path = path
        self.depth=-1
        self.parent=None
        self.base_path="cols"

    def parse(self,raw=None):
        if raw is None:
            with open(self.path, 'r',encoding='utf-8') as f:
                self.raw=f.read()
        else:
            self.raw=raw

        started=False
        with StringIO(self.raw) as r:
            while True:
                line = r.readline()
                if len(line)<=0: break
                if not started:
                    if not line.startswith("---"):
                        self.meta+=line
                    else:
                        #end of meta
                        started=True
                else:
                    if line.lstrip().startswith("-"):
                        #ColSection
                        buf=line
                        start_level=get_level(line)
                        while True:
                            save=r.tell()
                            innerline=r.readline()
                            if len(innerline) > 0 and innerline.strip() == "":
                                continue
                            if (get_level(innerline) <= start_level or len(innerline) <= 0) and len(buf) > 0:
                                #flush buf
                                sec=ColSection(self)
                                sec.parse(buf)
                                self.sections.append(sec)

                                #backpedal
                                r.seek(save)
                                break
                            else:
                                buf+=innerline

    def render(self):
        locs=self.render_from_locs()
        #todo add data to locs as well
        # locs={}

        #render everything and build locdict
        for section in self.sections:
            for loc in section.render():
                hsh = hash_string(loc[0].get_remote())
                if hsh not in locs:
                    locs[hsh]=[loc[1]]
                else:
                    locs[hsh].append(loc[1])
        #todo remove loc entries which are empty
        self.save_locs(locs)

    def render_from_locs(self):
        #read locs
        locs=None
        try:
            with open('locs.json','r') as f:
                locs=json.loads(f.read())
        except FileNotFoundError:
            return {}
        loc_items=copy.deepcopy(locs).items()

        for hsh,llocs in loc_items:
            i=0
            for loc in llocs:
                for item in self.get_items():
                    if item.skip_render:continue
                    curhash = hash_string(item.get_remote())
                    if hsh==curhash:
                        item_path=item.parent.get_path()
                        if item_path==loc[0]:
                            # already in correct place
                            files_exist=True
                            for f in loc[1]:
                                if not os.path.isfile(loc[0]+f):
                                    files_exist=False
                                    break # NB: case is not covered: where you rename, it will not delete the old  file
                            if files_exist:
                                if DEBUG: print("Already correct: " + loc[0] + loc[1][0]+'-'+loc[1][-1])
                                item.skip_render=True
                            else:
                                del locs[curhash][i]
                        else:
                            for f in loc[1]:
                                if DEBUG:
                                    if not os.path.isfile(item_path+f): print(loc[0]+f+" >> "+item_path+f)
                                cpath(item_path+os.path.split(f)[0])

                                try:
                                    shutil.copyfile(loc[0]+f,item_path+f) # copy to destination
                                except FileNotFoundError:
                                    # the src file (most likely) doesn't exist
                                    break
                            else:
                                needs_appending=True
                                for xloc in locs[hsh]:
                                    if xloc[0]==item_path:
                                        needs_appending=False
                                        break
                                if needs_appending:
                                    locs[hsh].append((item_path,loc[1],loc[2]))
                                item.skip_render=True # if loop was never broken (i.e: src file exists)
                i+=1

        for hsh,llocs in list(loc_items):
            for loc in llocs:
                needed=False
                for item in self.get_items():
                    if item.parent.get_path()==loc[0] and hash_string(item.get_remote())==hsh:
                        needed=True
                        break
                if not needed:
                    # delete orig
                    locs[hsh].remove(loc) # del from locdict

                    for f in loc[1]:
                        os.remove(loc[0]+f) # del file

                    rem_dir = os.path.split(loc[1][0])[0]
                    if rem_dir != '':
                        try:
                            os.rmdir(loc[0]+rem_dir) # del dir
                        except OSError:
                            pass

                    if DEBUG: print("Deleted: "+loc[0]+(loc[1][0] if rem_dir != '' else rem_dir))

        return locs

    def save_locs(self, locs):
        with open('locs.json','w') as f:
            f.write(json.dumps(locs))

    def get_items(self):
        ret=[]
        for section in self.sections:
            ret.extend(section.get_items())
        return ret

    #region serialisation
    def get_name(self,name_version=0):
        return self.base_path

    def to_string(self,indent="\t"):
        ind=""
        for i in range(self.depth):
            ind+=indent
        ret=""
        for section in sorted(self.sections, key=lambda x: x.parts[0]):
            ret+=ind+section.to_string(indent=indent)
        return ret

    def serialise(self,indent="\t"):
        ret=self.meta
        for i in range(len(self.meta.strip())):
            ret+='-'
        ret+="\n\n"
        ret+=self.to_string(indent=indent)
        return ret

    def write(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(self.serialise())

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
    #endregion

def run(raw=None,show_time=True):
    start_time = time.time()
    if raw is None:
        cf = ColFile("data.col")
        cf.parse()
    else:
        cf=ColFile("data.temp.col")
        cf.parse(raw)
    cf.render()
    # print(cf.serialise())
    if show_time: print("time elapsed: "+str(time.time() - start_time)+'s')

if __name__=='__main__':
    run()