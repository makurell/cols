import re
import os
import errno
import time
import builders
from io import StringIO

#globals
DEBUG=True
def get_level(s):
    # return len(s) - len(s.lstrip()) # just \n produces 1
    return len(re.match(r"^[ \t]*",s).group(0))

def get_parts(s,skip_start=True):
    ret=[]
    for part in (s[s.index("-") + 1:] if skip_start else s).split(' - '):
        fpart = part.strip()
        if fpart != '': ret.append(fpart)
    return ret

class ColItem:
    def __init__(self,parent):
        self.parts=[]
        self.parent=parent
        self.write=None

    def parse(self,raw):
        for part in raw.strip().split(' '):
            fpart = part.strip()
            if fpart != '': self.parts.append(fpart)

    def render(self):
        print(self.get_remote())

    #region serialisation
    def get_name(self):
        return self.parts[1]

    def get_remote(self):
        return self.parts[0]

    def to_string(self):
        ret = ""

        # parts
        for part in self.parts:
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
    def __init__(self,parent):
        self.items=[]
        self.parts=[]
        self.sections=[]
        self.depth=0
        self.parent=parent
        pass

    def parse(self, raw):
        with StringIO(raw) as r:
            start_line=r.readline()
            self.parts = get_parts(start_line)
            self.depth=get_level(start_line)

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
        dir=self.get_path()
        if DEBUG: print(dir)
        try:
            os.makedirs(dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        for section in self.sections:
            section.render()
        for item in self.items:
            item.render()

    #region serialisation
    def get_name(self,name_version=0):
        return re.sub("\([\s\S]*\)","",self.parts[name_version]).strip().replace(" ","-")

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
        self.depth=0
        self.parent=None
        self.base_path="cols"

    def parse(self,raw=None):
        if raw is None:
            with open(self.path, 'r') as f:
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

    def build(self):
        self.process()
        # self.render()

    def process(self):
        #make proc file
        proc=ColFile(path=os.path.splitext(self.path)[0]+'.proc.col')
        for section in self.sections:
            proc.sections.append(ColFile.__process_helper(section))
        proc.write()

    @staticmethod
    def __process_helper(proc: ColSection):
        if DEBUG:
            time.sleep(0.05)
            print(proc.get_path(1))
        section_list = []
        section_list.extend(proc.sections)
        proc.sections.clear()
        for section in section_list:
            proc.sections.append(ColFile.__process_helper(section))
        item_list = []
        item_list.extend(proc.items)
        proc.items.clear()
        for item in item_list:
            proc=ColFile.__process_item(proc,item)
        return proc

    @staticmethod
    def __process_item(proc: ColSection, item: ColItem):
        if DEBUG: print(item.get_remote())
        for hook in builders.hooks:
            if re.match("^"+hook[0]+"$",proc.get_path(1)):
                try:
                    if hook[2] is not None:
                        item.write=hook[2]
                    else: raise IndexError
                except IndexError:
                    item.write=builders.default_render

                procmeth=builders.default_process
                try:
                    if hook[1] is not None: procmeth=hook[1]
                except IndexError: pass
                proc=procmeth(proc,item)
                break
        else:
            item.write=builders.default_render
            proc=builders.default_process(proc,item)
        return proc

    def render(self):
        for section in self.sections:
            section.render()

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
        with open(self.path, 'w') as f:
            f.write(self.serialise())

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
    #endregion

if __name__=="__main__":
    cf = ColFile("data.col")
    cf.parse()
    # print(cf.serialise())
    cf.build()
    # print(cf.serialise())

