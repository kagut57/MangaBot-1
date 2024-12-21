import re
from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote, quote_plus

from bs4 import BeautifulSoup

from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter


class AsuraScansClient(MangaClient):

    base_url = urlparse("https://asuracomic.net/")
    search_url = base_url.geturl()
    search_param = 'series'
    updates_url = base_url.geturl()

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def __init__(self, *args, name="AsuraScans", **kwargs):
        super().__init__(*args, name=name, headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        container = bs.find("div", {"class": "grid grid-cols-2 sm:grid-cols-2 md:grid-cols-5 gap-3 p-4"})

        cards = container.find_all("a")
        
        names = [card.find("span", class_="block text-[13.3px] font-bold").text.strip() for card in cards]
        url = [f'{self.base_url.geturl()}{card.get("href")}' for card in cards]
        images = [card.findNext("img").get("src") for card in cards]

        mangas = [MangaCard(self, *tup) for tup in zip(names, url, images)]

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        container = bs.find("div", {"class": "pl-4 pr-2 pb-4 overflow-y-auto scrollbar-thumb-themecolor scrollbar-track-transparent scrollbar-thin mr-3 max-h-[20rem] space-y-2.5"})

        lists = container.find_all("a")

        links = [f'{self.base_url.geturl()}series/{list.get("href")}' for list in lists]
        texts = [list.text.strip() for list in lists]

        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    def updates_from_page(self, content):
        bs = BeautifulSoup(content, "html.parser")

        manga_items = bs.find_all("div", {"class": "w-full p-1 pt-1 pb-3 border-b-[1px] border-b-[#312f40]"})

        urls = dict()

        for manga_item in manga_items:
            manga_url = manga_item.findNext("a").get("href")
            manga_url = "https://asuracomic.net" + manga_url

            if manga_url in urls:
                continue

            chapter_url = manga_item.find("span", class_="flex-1 inline-block mt-1").findNext("a").get("href")
            chapter_url = "https://asuracomic.net" + chapter_url

            urls[manga_url] = chapter_url

        return urls

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")
        
        scripts = bs.find_all("script")
        for script in scripts:
            if script.string and 'pages\\":[' in script.string:
                match = re.search(r'pages\\":(\[.*?\])', script.string)
                if match:
                    raw_json = match.group(1)
                    try:
                        unescaped_json = raw_json.replace('\\"', '"').replace('\\\\', '\\')
                        pages = json.loads(unescaped_json)
                        urls = [page["url"] for page in pages]
                        return urls
                    except json.JSONDecodeError as e:
                        return []
    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        query = query.strip()
        query = query.replace(" ", "+").replace("’", "+")

        request_url = self.search_url

        if query:
            request_url += f'{self.search_param}?page=1&name={query}'

        content = await self.get_url(request_url)

        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:

        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        return self.chapters_from_page(content, manga_card)[(page - 1) * 20:page * 20]

    async def iter_chapters(self, manga_url: str, manga_name) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')

        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        for chapter in self.chapters_from_page(content, manga_card):
            yield chapter

    async def contains_url(self, url: str):
        return url.startswith(self.base_url.geturl())

    async def check_updated_urls(self, last_chapters: List[LastChapter]):
        content = await self.get_url(self.updates_url)
        updates = self.updates_from_page(content)

        updated = [lc.url for lc in last_chapters if updates.get(lc.url) and updates.get(lc.url) != lc.chapter_url]
        not_updated = [lc.url for lc in last_chapters if
                       not updates.get(lc.url) or updates.get(lc.url) == lc.chapter_url]

        return updated, not_updated
