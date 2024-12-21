import re

from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus

from bs4 import BeautifulSoup

from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter


class MgekoClient(MangaClient):
    base_url = urlparse("https://www.mgeko.cc/")
    image_cdn = "https://cdn.mangageko.com/avatar/288x412"
    search_url = urljoin(base_url.geturl(), "search")
    search_param = "search"
    update_url = urljoin(base_url.geturl(), "jumbo/manga/")

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 14; zh-cn; 2211133C Build/UKQ1.230804.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.118 Mobile Safari/537.36 XiaoMi/MiuiBrowser/18.5.40902'
    }

    def __init__(self, *args, name="MGeko", **kwargs):
        super().__init__(*args, name=name, headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")
        cards = bs.find_all('li', class_='novel-item')
        names = []
        urls = []
        images = []

        for card in cards:
            a_tag = card.find('a')
            if a_tag is not None:
                name = a_tag.get("title").strip()
                url = urljoin(self.base_url.geturl(), a_tag.get('href').strip())
                img_tag = card.find("img")
                image =(
                    self.image_cdn
                    + img_tag.get('data-src').strip()) if img_tag else None

                names.append(name)
                urls.append(url)
                images.append(image)

        mangas = [MangaCard(self, *tup) for tup in zip(names, urls, images)]
        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        chapter_items = bs.find_all('li', {
            'data-chapterno': True,
            'data-volumeno': True,
            'data-orderno': True
        })

        links = [
            urljoin(self.base_url.geturl(), item.find('a').get('href'))
            for item in chapter_items
        ]
        titles = [
            f"Chapter {title.split('-')[0]}"
            for title in [
                item.find('strong', class_='chapter-title').text.strip()
                for item in chapter_items
            ]
        ]

        return list(
            map(lambda x: MangaChapter(self, x[0], x[1], manga, []),
                zip(titles, links)))

    def updates_from_page(self, content: bytes):
        bs = BeautifulSoup(content, "html.parser")

        container = bs.find("ul", {"class": "novel-list grid col col2 chapters"})
        items = container.findAll("li", {"class": "novel-item"})

        urls = dict()

        for item in items:
            manga_url = urljoin(self.base_url.geturl(), item.find('a').get('href'))
            if manga_url in urls:
                continue
            chapter_title = item.find("h5", {"class": "chapter-title text1row"}).text.strip()
            chapter_url = f"{self.base_url.scheme}://{self.base_url.netloc}/reader/en/{manga_url.split('/')[-2]}-{chapter_title.lower().replace(' ', '-')}/"
            urls[manga_url] = chapter_url

        return urls

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")

        chapter_reader_div = bs.find("div", {"id": "chapter-reader"})
        image_items = chapter_reader_div.find_all("img") if chapter_reader_div else []

        images_url = [image_item.get("src") for image_item in image_items]

        return images_url

    async def get_picture(self, manga_chapter: MangaChapter, url, *args, **kwargs):
        headers = dict(self.headers)
        headers['Referer'] = self.base_url.geturl()

        return await super(MgekoClient, self).get_picture(manga_chapter, url, headers=headers, *args, **kwargs)

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        request_url = self.search_url
        query = query.strip()
        query = query.replace(" ", "+").replace("’", "+")

        if query:
            request_url = f'{request_url}?{self.search_param}={query}'

        content = await self.get_url(request_url)

        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:
        request_url = f'{manga_card.url}all-chapters/'

        content = await self.get_url(request_url)

        return self.chapters_from_page(content, manga_card)[(page - 1) * 20:page * 20]

    async def iter_chapters(self, manga_url: str, manga_name) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')

        request_url = f'{manga_card.url}all-chapters/'

        content = await self.get_url(request_url)

        for chapter in self.chapters_from_page(content, manga_card):
            yield chapter

    async def contains_url(self, url: str):
        return url.startswith(self.base_url.geturl())

    async def check_updated_urls(self, last_chapters: List[LastChapter]):
        updates = await self.updates_from_page()

        updated = []
        not_updated = []
        for lc in last_chapters:
            if lc.url in updates.keys():
                if updates.get(lc.url) != lc.chapter_url:
                    updated.append(lc.url)
            elif updates.get(lc.url) == lc.chapter_url:
                not_updated.append(lc.url)
                
        return updated, not_updated
