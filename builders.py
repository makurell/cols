import urllib.parse as urlparse
from pixivpy3 import AppPixivAPI
from cols import ColSection, ColItem
from PIL import Image
from io import BytesIO
import os
import requests

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
api=AppPixivAPI()
if 'PIXIV_USERNAME' in os.environ:
    api.login(os.environ.get('PIXIV_USERNAME'),os.environ.get('PIXIV_PASS'))
else: print("Pixiv env variables not set!")

def get_illust_id(url):
    return urlparse.parse_qs(urlparse.urlparse(url).query)['illust_id'][0]

def pixiv_render(item,path):
    illust_id = get_illust_id(item.get_remote())
    detail = api.illust_detail(illust_id)
    url = None
    try:
        url = detail['illust']['meta_single_page']['original_image_url']
    except:
        url = detail['illust']['image_urls']['large']
    api.download(url, prefix=item.get_name(), path=os.path.abspath(path))

def pixiv_process(proc: ColSection, item: ColItem):
    illust_id=get_illust_id(item.get_remote())

    detail=api.illust_detail(illust_id)
    item.parts[1]=str(detail['illust']['title'])+'-'+str(illust_id)

    sec = ColSection(proc)
    sec.parts.append(str(detail['illust']['user']['name'])+'-'+str(detail['illust']['user']['id']))
    item.parent=sec
    sec.items.append(item)
    #todo: store details in item somehow + thing like date modified

    proc.sections.append(sec)
    return proc
#endregion

hooks=[
    (r"(.*/|)pixiv/",pixiv_process,pixiv_render),
]