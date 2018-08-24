import urllib.parse as urlparse
from pixivpy3 import AppPixivAPI
from cols import ColSection, ColItem
from PIL import Image
from io import BytesIO
import requests

#region utils
#endregion
#region default
def write_img(remote,local):
    with Image.open(BytesIO(requests.get(remote).content)) as img:
        img.save(local,quality=75,optimize=True)

def default_process(proc: ColSection, item: ColItem):
    proc.items.append(item)
    return proc

def default_render(item: ColItem, path):
    write_img(item.get_remote(),path+item.get_name()+'.jpeg')
#endregion
#region pixiv
api=AppPixivAPI
def pixiv_render(item,path):
    pass

def pixiv_process(proc: ColSection, item: ColItem):
    illust_id=urlparse.parse_qs(urlparse.urlparse(item.get_remote()).query)['illust_id'][0]
    item.parts[1]=illust_id
    proc.items.append(item)
    return proc
#endregion

hooks=[
    (r"(.*/|)pixiv/",pixiv_process),
]