import scrapy
from loginform import fill_login_form
from country_films_crawler.utils import *
from urllib.parse import urljoin


class FixAvatarSpider(scrapy.Spider):
    name = "fix_avatars"

    # main_url = []  # oops :)

    avatars_data = []

    avatars_save_path = '../data/download/fix_black_avatars_images.txt'

    credentials = dict(load_tuples_list('../data/fix_credentials.txt'))

    login_url = credentials['login_url']

    login_user = credentials['login_user']
    login_password = credentials['login_password']

    def save_data(self):
        save_tuples_list(self.avatars_data, self.avatars_save_path)

    def start_requests(self):
        yield scrapy.Request(self.login_url, self.parse_login)

    def parse_login(self, response):
        data, url, method = fill_login_form(response.url, response.body,
                                            self.login_user, self.login_password)

        return scrapy.FormRequest(url, formdata=dict(data),
                                  method=method, callback=self.start_crawl)

    def start_crawl(self, response):
        for url in self.main_url:
            yield scrapy.Request(url=url, callback=self.parse_celebs_list)

    def parse_celebs_list(self, response):
        for celeb_url in response.css('ul.gy2 li a.blue::attr(href)').getall():
            yield response.follow(url=urljoin(celeb_url + '/', 'photo'), callback=self.parse_ava_photo_page)

        next_page = response.css('div.paging a.blue')
        if len(next_page) != 0:
            next_page = next_page[-1]
            if next_page.css('::text').get() == 'Next »':
                next_page_url = next_page.css('::attr(href)').get()
                yield response.follow(url=next_page_url, callback=self.parse_celebs_list)

    def parse_ava_photo_page(self, response):
        img_url = response.css('img.imgorig::attr(src)').get()
        person_name = response.css('#banner0 div.cbox-nav div.cbox-nav2 div.label h1.posl a::text').get()
        self.avatars_data.append((person_name.replace(' ', '_'), img_url.split('?')[0]))

    def close(self, spider, reason):
        self.save_data()
        super(FixAvatarSpider, self).close(spider, reason)


class FixPhotosSpider(scrapy.Spider):
    name = "fix_photos"

    main_url = []  # oops :)

    gained_data = []

    save_path = '../data/download/fix_black_images.txt'

    def save_data(self):
        self.gained_data = list(set(self.gained_data))
        self.log('GAINED %d' % len(self.gained_data))
        save_tuples_list(self.gained_data, self.save_path)

    def start_requests(self):
        for url in self.main_url:
            yield scrapy.Request(url=url, callback=self.parse_celebs_list)

    def parse_celebs_list(self, response):
        for celeb_url in response.css('ul.gy2 li a.blue::attr(href)'):
            yield response.follow(url=celeb_url, callback=self.parse_celeb_page)

        next_page = response.css('div.paging a.blue')
        if len(next_page) != 0:
            next_page = next_page[-1]
            if next_page.css('::text').get() == 'Next »':
                next_page_url = next_page.css('::attr(href)').get()
                yield response.follow(url=next_page_url, callback=self.parse_celebs_list)

    def parse_celeb_page(self, response):
        person_info = response.css('div.tnavmenu li')
        for info in person_info:
            if info.css('a::text').get() == 'Photos':
                url = info.css('a::attr(href)').get()
                yield response.follow(url=url, callback=self.parse_photos_page)

    def parse_photos_page(self, response):
        all_imgs_urls = response.css('div.cboxy div.oh a img::attr(src)').getall()
        imgs_urls = [v for v in all_imgs_urls if v.split('/')[4] == 'orig']
        person_name = response.css('div.label h1.posl a::text').get()

        for img_url in imgs_urls:
            self.gained_data.append((person_name.replace(' ', '_'), img_url.split('?')[0]))

        next_page = response.css('div.paging a.blue')
        if len(next_page) != 0:
            next_page = next_page[-1]
            if next_page.css('::text').get() == 'Next »':
                next_page_url = next_page.css('::attr(href)').get()
                yield response.follow(url=next_page_url, callback=self.parse_photos_page)

        self.save_data()

    def close(self, spider, reason):
        self.save_data()
        super(FixPhotosSpider, self).close(spider, reason)

