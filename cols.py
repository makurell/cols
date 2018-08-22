import re
from io import StringIO

#utils methods
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
    def __init__(self):
        self.parts=[]

    def parse(self,raw):
        self.parts = get_parts(raw,skip_start=False)

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


class ColSection:
    def __init__(self):
        self.items=[]
        self.parts=[]
        self.sections=[]
        self.depth=0
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
                            sec = ColSection()
                            sec.parse(buf)
                            self.sections.append(sec)

                            #backpedal
                            r.seek(save)
                            break
                        else:
                            buf += innerline
                else:
                    # ColItem
                    item = ColItem()
                    item.parse(line)
                    self.items.append(item)

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

class ColFile:
    def __init__(self,path):
        self.sections = []
        self.raw = None
        self.meta = ""
        self.path = path
        self.depth=0

    def parse(self):
        with open(self.path, 'r') as f:
            self.raw=f.read()

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
                                sec=ColSection()
                                sec.parse(buf)
                                self.sections.append(sec)

                                #backpedal
                                r.seek(save)
                                break
                            else:
                                buf+=innerline

    def to_string(self,indent="\t"):
        ind=""
        for i in range(self.depth):
            ind+=indent
        ret=""
        for section in sorted(self.sections, key=lambda x: x.parts[0]):
            ret+=ind+section.to_string(indent=indent)
        return ret

    def __str__(self):
        return self.to_string()

    def __unicode__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

if __name__=="__main__":
    cf = ColFile("data.col")
    cf.parse()
    print(cf.to_string())
