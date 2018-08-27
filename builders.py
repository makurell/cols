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

def default_render(item: ColItem, base_path,debug=False):
    path=item.get_name()+'.jpeg'
    write_img(item.get_remote(),base_path+path)
    return [path],{}
#endregion
#region pixiv
pixiv_api=None
pixiv_username=None
pixiv_password=None

def get_illust_id(url):
    return urlparse.parse_qs(urlparse.urlparse(url).query)['illust_id'][0]

def pixiv_render(item,base_path,debug=False):
    global pixiv_api
    if pixiv_api is None:
        pixiv_api=AppPixivAPI()
        pixiv_api.login(pixiv_username,pixiv_password)

    illust_id = get_illust_id(item.get_remote())

    detail = pixiv_api.illust_detail(illust_id)
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
        pixiv_api.download(url, name=name, path=os.path.abspath(base_path + path))
        if debug: print('.',end='',flush=True)
    return ret, detail
#endregion

hooks=[
    (r".*pixiv\.net\/.*illust_id=\d+.*",pixiv_render),
]