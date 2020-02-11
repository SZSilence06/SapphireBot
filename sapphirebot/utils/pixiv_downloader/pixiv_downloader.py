# coding=utf-8
from pixivpy3 import ByPassSniApi
import json
import time
import requests
import os
from concurrent import futures
import asyncio
import random
import threading
from PIL import Image

ONE_PAGE = 30  # 一页共30张插画
TOTAL_RETRY_TIMES = 3 # 最多重试3次下载

class PixivDownloadError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return str(self.error['message'])


class IllustInfo(object):
    def __init__(self, url: dict, id: int):
        self.url = url
        self.id = id


class DownloadResult(object):
    SUCCESS = 0
    SKIPPED = 1
    ERROR_UNKNOWN = 2
    ERROR_404 = 3
    

class PixivDownloader(object):
    def __init__(self):
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.has_logged_in = False
        self.lock = threading.Lock()
        self.image_dir = 'download'

        # 创建下载目录
        full_image_dir = os.path.join(self.dir, self.image_dir)
        if not os.path.exists(full_image_dir):
            os.mkdir(full_image_dir)

    def login_pixiv(self):
        self.api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
        self.api.require_appapi_hosts()

        account_data = None
        with open("account.json", "r") as f:
            account_data = json.loads(f.read())

        self.api.login(account_data["username"], account_data["password"])
        self.has_logged_in = True

    def download_illust(self, illust):
        info = IllustInfo(
            url= {
                'squareMedium': illust.image_urls.get('square_medium'),
                'medium': illust.image_urls.get('medium'),
                'large': illust.image_urls.get('large'),
                'original' : illust.meta_single_page.get('original_image_url'),
            },
            id=illust.id
        )
        self.download_image(info)

    def download_image(self, info: IllustInfo) -> DownloadResult:
        # 按以下优先级对URL进行下载。如果下载出来是404则尝试下载下一个URL
        urls = [info.url['large'], info.url['original'], info.url['medium'], info.url['squareMedium']]
        for url in urls:
            result = self.download_image_using_url(url=url, id=info.id)
            if result in (DownloadResult.SUCCESS, DownloadResult.SKIPPED):
                return result

            elif result == DownloadResult.ERROR_404:
                print('[WARNING] 404: %s' % url)
                continue

            elif result == DownloadResult.ERROR_UNKNOWN:
                break
        
        # 下载失败
        print('[ERROR] Download failed!!! image id=%s' % url)
        return DownloadResult.ERROR_UNKNOWN

    def download_image_using_url(self, url: str, id: int) -> DownloadResult:
        '''
        从给定的URL下载图片
        返回下载结果
        '''
        retry_times = TOTAL_RETRY_TIMES
        while retry_times > 0:
            try:
                ext = os.path.splitext(url)[1]
                img_name = 'pixiv_%d%s' % (id, ext)
                full_image_name = os.path.join(self.dir, self.image_dir, img_name)
                if os.path.exists(full_image_name):
                    if self.is_valid_image(full_image_name):
                        print('skip %s' % url)
                        return DownloadResult.SKIPPED
                    # 是损坏的图片文件
                    os.remove(full_image_name)
                
                # 因为下载过程可能是多线程并发执行的，而登录只需要全局进行一次，所以用锁保护起来
                # 判断两次是典型的单例模式的写法
                if self.has_logged_in is False:
                    self.lock.acquire()
                    if self.has_logged_in is False:
                        self.login_pixiv()
                    self.lock.release()

                if retry_times == TOTAL_RETRY_TIMES:
                    # 首次尝试下载
                    print('Download', url)
                else:
                    print('Retry download', url)
                
                self.api.download(url, path=self.image_dir, name=img_name, replace=False)
                time.sleep(random.random() * 10.0 + 10.0)  #  防止下载过于频繁被封

                if self.is_404(full_image_name):
                    os.remove(full_image_name)
                    return DownloadResult.ERROR_404

                if self.is_valid_image(full_image_name):
                    return DownloadResult.SUCCESS
                
                print('[WARNING]Invalid image: %s' % url)
            except Exception as e:
                print("[WARNING]download %s failed: %s" % (url, str(e)))

            retry_times -= 1

        # 几次反复尝试后全部失败
        if os.path.exists(full_image_name):
            os.remove(full_image_name)
        return DownloadResult.ERROR_UNKNOWN

    def is_404(self, filename: str):
        try:
            with open(filename, 'r') as f:
                text = f.read()
                return '404 Not Found' in text
        except:
            return False

    def is_valid_image(self, filename: str):
        try:
            im = Image.open(filename)
            im.save(filename)
            return True
        except IOError:
            # filename not an image file
            return False
 
    def download_tag_most_popular(self, tag: str, number: int):
        '''
        下载某个标签的收藏最多的xx张图片。
        由于pixiv按热度排序需要超级会员，此接口只有在bot拥有超级会员时有效
        '''
        if self.has_logged_in is False:
            self.login_pixiv()

        json_result = self.api.search_illust(tag, search_target='partial_match_for_tags', sort='popular_desc')
        if hasattr(json_result, 'error'):
            raise PixivDownloadError(json_result.error)
        illusts = json_result.illusts

        for illust in illusts[:number]:
            self.download_illust(illust)

    def download_tag_most_popular_using_pixivic(self, tag: str, number: int, offset=0):
        '''
        下载某个标签的收藏最多的xx张图片。
        使用http://www.pixivic.com 提供的API
        '''
        end = offset + number
        start_page = offset // ONE_PAGE + 1
        end_page = (end-1) // ONE_PAGE + 1

        # 获取插画的信息。分页来处理
        illust_infos = []
        for i in range(start_page, end_page + 1):
            # 构建报文
            params = {
                'page': i,
                'keyword': tag
            }
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                'origin': 'https://pixivic.com',
                'referer': 'https://pixivic.com/popSearch'
            }
            url = 'https://api.pixivic.com/illustrations'

            # 获取数据
            response = requests.get(url, params=params, headers=headers)
            result = response.json()

            # 根据offset和end，把需要的插画数据添加到illust_infos数组中
            offset_in_this_page = offset - ONE_PAGE * (i - 1)
            offset_in_this_page = max([offset_in_this_page, 0])
            end_in_this_page = end - ONE_PAGE * (i - 1)
            end_in_this_page = min(end_in_this_page, ONE_PAGE)
            illust_infos += result['data']['illustrations'][offset_in_this_page:end_in_this_page]

        infos = [IllustInfo(
            id=info['id'], 
            url={
                'squareMedium': info['imageUrls'][0]['squareMedium'],
                'medium': info['imageUrls'][0]['medium'],
                'large': info['imageUrls'][0]['large'],
                'original': info['imageUrls'][0]['original'],
            }
        ) for info in illust_infos]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download_illusts_async(infos))
        

    async def download_illusts_async(self, illust_infos: list):
        # 启用线程池来异步下载
        loop = asyncio.get_event_loop()
        results = []
        with futures.ThreadPoolExecutor(8) as executor:
            tasks = [loop.run_in_executor(executor, self.download_image, info) for info in illust_infos]
            results = await asyncio.gather(*tasks)

        # 统计结果
        failed_images = []
        succeeded_count = 0
        failed_count = 0
        skipped_count = 0
        for i, result in enumerate(results):
            info = illust_infos[i]
            if result == DownloadResult.SUCCESS:
                succeeded_count += 1
            elif result == DownloadResult.SKIPPED:
                skipped_count += 1
            else:
                failed_images.append(info.id)
                failed_count += 1
            
        # 打印结果
        print('=======Download result==========')
        print('Total succeeded files: %d' % succeeded_count)
        print('Total skipped files: %d' % skipped_count)
        print('Total failed files: %d' % failed_count)
        if failed_count > 0:
            print('Failed File are:')
            for id in failed_images:
                print('id=%d' % id)
        print('=======Download result end======')

    def download_recommended(self, number: int):
        # get recommended
        if self.has_logged_in is False:
            self.login_pixiv()

        json_result = self.api.illust_recommended()
        if hasattr(json_result, 'error'):
            raise PixivDownloadError(json_result.error)
        illusts = json_result.illusts

        for illust in illusts[:number]:
            self.download_illust(illust)


if __name__ == '__main__':
    try:
        downloader = PixivDownloader()
        downloader.download_tag_most_popular_using_pixivic(tag='水着', number=100, offset=0)
    except PixivDownloadError as e:
        print('Download failed: %s' % e)



    