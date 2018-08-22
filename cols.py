import re
from io import StringIO

#utils methods
def get_level(s):
    # return len(s) - len(s.lstrip()) # just \n produces 1
    return len(re.match(r"^[ \t]*",s).group(0))

class ColItem:
    def __init__(self):
        pass

    def parse(self,raw):
        self.raw=raw

class ColSection:
    def __init__(self):
        self.items=[]
        self.parts=[]
        self.sections=[]
        pass

    def parse(self, raw):
        with StringIO(raw) as r:
            start_line = r.readline()
            for part in start_line[start_line.index("-")+1:].split(' - '):
                fpart=part.strip()
                if fpart!='': self.parts.append(fpart)

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

class ColFile:
    def __init__(self,path):
        self.sections = []
        self.raw = None
        self.meta = ""
        self.path = path

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

if __name__=="__main__":
    cf = ColFile("data.col")
    cf.parse()
    print(cf)