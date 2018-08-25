import urllib.parse as urlparse
from pixivpy3 import AppPixivAPI
from cols import ColSection, ColItem
from PIL import Image
from io import BytesIO
import os
import errno
import requests

#region default/utils
def cpath(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def write_img(remote,local):
    with Image.open(BytesIO(requests.get(remote).content)) as img:
        img.save(local,quality=75,optimize=True)

def default_render(item: ColItem, base_path):
    write_img(item.get_remote(),base_path+item.get_name()+'.jpeg') #todo case where no name given
#endregion
#region pixiv
api=AppPixivAPI()
if 'PIXIV_USERNAME' in os.environ:
    api.login(os.environ.get('PIXIV_USERNAME'),os.environ.get('PIXIV_PASS'))
else: print("Pixiv env variables not set!")

def get_illust_id(url):
    return urlparse.parse_qs(urlparse.urlparse(url).query)['illust_id'][0]

def pixiv_render(item,base_path):
    #todo multiple pictures case (manga) (either create dir or do all)
    illust_id = get_illust_id(item.get_remote())

    detail = api.illust_detail(illust_id)
    path=os.path.abspath(base_path+str(detail['illust']['user']['name'])+'_'+str(detail['illust']['user']['id']))
    cpath(path)

    url = None
    try:
        url = detail['illust']['meta_single_page']['original_image_url']
    except (NameError, KeyError):
        url = detail['illust']['image_urls']['large']

    api.download(url, prefix=str(detail['illust']['title'])+'_'+str(illust_id), path=os.path.abspath(path))
#endregion

hooks=[
    (r"(.*/|)pixiv/",pixiv_render),
]