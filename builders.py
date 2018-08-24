from cols import ColSection, ColItem
from PIL import Image
from io import BytesIO
import requests

def write_img(remote,local):
    with Image.open(BytesIO(requests.get(remote).content)) as img:
        img.save(local)

def default_process(proc: ColSection, item: ColItem):
    proc.items.append(item)
    return proc

def default_render(item: ColItem, path):
    write_img(item.get_remote(),path+item.get_name()+'.jpeg')

hooks=[
    (r"(.*/|)pixiv/",default_process),
]