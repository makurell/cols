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
    path=item.get_name()+'.jpeg'
    write_img(item.get_remote(),base_path+path) #todo case where no name given
    return [path]
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
    path=(str(detail['illust']['user']['name'])+'_'+str(detail['illust']['user']['id']))
    cpath(base_path+path)

    urls = []
    if detail['illust']['page_count'] > 1:
        for page in detail['illust']['meta_pages']:
            page_url=None
            try:
                page_url=page['image_urls']['original']
            except (NameError,KeyError):
                try:
                    page_url=list(page['image_urls'].values())[-1]
                except (NameError,KeyError): pass
            if page_url is not None:
                urls.append(page_url)
    if len(urls)<=0:
        try:
            urls.append(detail['illust']['meta_single_page']['original_image_url'])
        except (NameError, KeyError):
            try:
                urls.append(detail['illust']['image_urls']['large'])
            except (NameError, KeyError): pass

    ret=[]
    for url in urls:
        name=str(detail['illust']['title']) + '_' + str(illust_id) + os.path.basename(url)
        ret.append(path+'/'+name)
        api.download(url, name=name, path=os.path.abspath(base_path+path))
    return ret
#endregion

hooks=[
    (r"(.*/|)pixiv/",pixiv_render),
]