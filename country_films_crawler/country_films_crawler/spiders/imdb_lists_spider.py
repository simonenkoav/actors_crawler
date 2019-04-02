import scrapy
from html.parser import HTMLParser
from country_films_crawler.utils import load_list


class PhotoPageHTMLParser(HTMLParser):
    content = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attrs_d = dict(attrs)
            if 'itemprop' in attrs_d and attrs_d['itemprop'] == 'image':
                self.content = attrs_d['content']


class ImdbListsSpider(scrapy.Spider):
    name = "imdb_list"

    gained_data = []

    gained_actors = []

    urls = set(load_list('../data/imdbs_lists_urls.txt'))

    photo_page_html_parser = PhotoPageHTMLParser()

    def save_data(self):
        self.gained_data = list(set(self.gained_data))
        self.log('GAINED %d' % len(self.gained_data))
        with open('../data/black_lists_imdb_data.txt', 'w') as fd:
            for url in self.gained_data:
                fd.write(url + '\n')

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        for info in response.css('div.lister-list div.lister-item h3.lister-item-header'):
            name = info.css('a::text').get().replace(' ', '')
            if name in self.gained_actors:
                return
            else:
                self.gained_actors.append(name)
            actor_url = info.css('a::attr(href)')[0]
            yield response.follow(url=actor_url, callback=self.parse_actor)

        for href in response.css('div.list-pagination a.next-page::attr(href)'):
            yield response.follow(url=href, callback=self.parse_list)

    def parse_actor(self, response):
        photos_url = response.css('div.see-more a::attr(href)')[0]
        yield response.follow(url=photos_url, callback=self.parse_photos)

    def parse_photos(self, response):
        for href in response.css('div.media_index_thumb_list a::attr(href)'):
            yield response.follow(url=href, callback=self.parse_single_photo)

    @staticmethod
    def formate_photo_url(url):
        return url[:url.find('_V1_')+4] + '.jpg'

    def parse_single_photo(self, response):
        self.photo_page_html_parser.feed(str(response.body))
        photo_url = self.photo_page_html_parser.content
        photo_url = self.formate_photo_url(photo_url)
        self.gained_data.append(photo_url)
        self.save_data()

    def close(self, spider, reason):
        self.save_data()
        super(ImdbListsSpider, self).close(spider, reason)
