import os
import requests
import flet as ft
from pathlib import Path


def open_snack_bar(page, msg):
    page.snack_bar.content = ft.Text(msg)
    page.snack_bar.open = True
    page.update()


class BookHelper:
    def __init__(self):
        self.hierarchies = self.fetch_hierarchies()
        self.books = self.fetch_books()

    def fetch_hierarchies(self):
        """
        获取标签元数据
        """
        response = requests.get('https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/tags/tch_material_tag.json')
        hierarchies = response.json().get('hierarchies')[0].get('children')[0].get('hierarchies')
        # 解析hierarchies数据
        return self.parse_hierarchies(hierarchies)

    def fetch_books(self):
        """
        获取教材
        """
        with requests.Session() as session:
            response = session.get(
                'https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/version/data_version.json')
            urls = response.json().get('urls').split(',')
            response_list = [session.get(url).json() for url in urls]

        book_list = []
        for books_data in response_list:
            book_list.extend(books_data)

        books = []
        for book in book_list:
            tags_dict = {book['tag_id']: book['tag_name'] for book in book['tag_list']}

            tag_paths = book['tag_paths']
            custom_properties = book.get('custom_properties')

            download_path_parts = [tags_dict.get(tag) for tag in tag_paths[0].split('/')]
            download_path = os.sep.join(download_path_parts)
            download_format = custom_properties.get('format')
            title = book.get('title')

            books.append({
                'id': book.get('id'),
                'title': title,
                'size': custom_properties.get('size'),
                'preview': custom_properties.get('preview'),
                'thumbnails': custom_properties.get('thumbnails')[0],
                'create_time': book.get('create_time'),
                'update_time': book.get('update_time'),
                'tag_path': '/'.join(tag_paths[0].split('/')[2:]),
                'file_path': f"{download_path}/{title}.{download_format}".replace(' ', ''),
                'download_url': f"https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/{book['id']}.pkg/pdf.pdf"
            })

        return books

    def parse_hierarchies(self, hierarchies):
        """
        递归解析标签
        """
        if not hierarchies:
            return None
        parsed_hierarchies = {}
        for h in hierarchies:
            for ch in h['children']:
                tag_id = ch['tag_id']
                parsed_hierarchies[tag_id] = {
                    'tag_id': tag_id,
                    'tag_name': ch['tag_name'],
                    'children': self.parse_hierarchies(ch.get('hierarchies', []))
                }
        return parsed_hierarchies

    def get_term(self):
        """
        获取学段
        """
        return self.hierarchies

    def get_subject(self, term_id):
        """
        获取学科
        """
        return self.get_term().get(term_id, {}).get('children', {})

    def get_version(self, term_id, sub_id):
        """
        获取版本
        """
        return self.get_subject(term_id).get(sub_id, {}).get('children', {})

    def get_grade(self, term_id, sub_id, version_id):
        """
        获取年级
        """
        return self.get_version(term_id, sub_id).get(version_id, {}).get('children', {})

    def get_books(self, search_str):
        """
        获取教材
        """
        books = list(filter(lambda item: item['tag_path'].startswith(search_str), self.books))
        res_ids = ','.join(book['id'] for book in books)
        try:
            response = requests.get(
                f'https://x-api.ykt.eduyun.cn/proxy/cloud/v1/res_stats/actions/query?res_ids={res_ids}',
                headers={
                    "User-Agent":
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                })
            response.raise_for_status()
            statistics = {item['id']: {'total_uv': item.get('total_uv', 0), 'like_count': item.get('like_count', 0)}
                          for item in response.json()}
        except requests.exceptions.RequestException:
            statistics = {res_id: {'total_uv': 0, 'like_count': 0} for res_id in res_ids.split(',')}

        for book in books:
            book.update(statistics.get(book['id']))

        return books

    def download(self, progress_bar, e, session=requests.Session()):
        progress_bar.visible = True
        download_url = e.control.data['download_url']
        file_path = e.control.data['file_path']
        download_path = os.path.join(Path.home(), file_path)
        if not os.path.exists((os.path.dirname(download_path))):
            os.makedirs(os.path.dirname(download_path))

        with session.get(download_url, stream=True) as r:
            with open(download_path, 'wb') as f:
                r.raw.decode_content = True
                downloaded_size = 0
                size = int(r.headers['Content-Length'])
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress_bar.value = downloaded_size / size
                    e.page.update()
        open_snack_bar(e.page, f"文件已成功保存到{download_path}")
