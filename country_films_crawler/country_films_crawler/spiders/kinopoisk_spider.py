import scrapy
from country_films_crawler.utils import *


class ContryFilmsSpider(scrapy.Spider):
    name = "country_films"

    gained_data = []

    countries = load_list('../data/asian_countries.txt')
    countries = [v.split() for v in countries]

    main_url = 'https://www.kinopoisk.ru/lists/m_act[country]/%s'

    save_path = '../data/download/asian_actors.txt'

    def save_data(self):
        self.gained_data = list(set(self.gained_data))
        self.log('GAINED %d' % len(self.gained_data))
        with open(self.save_path, 'w') as fd:
            for pname, url in self.gained_data:
                line = pname.replace(' ', '_') + ' ' + url
                fd.write(line + '\n')

    def start_requests(self):
        urls = [self.main_url % code for code in self.countries.values()]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_country)

    def parse_country(self, response):
        for film_info in response.css('div.tenItems div.item'):
            film_url = film_info.css('div.info div.name a::attr(href)')[0]
            film_countries = film_info.css('div.flags div.flag a::attr(title)').getall()
            if all(c in self.countries for c in film_countries):
                yield response.follow(url=film_url, callback=self.parse_film)

        for href in response.css('div.navigator li.arr a::attr(href)'):
            yield response.follow(url=href, callback=self.parse_country)

    def parse_film(self, response):
        cast_url = response.css('#actorList h4 a::attr(href)')[0]
        yield response.follow(url=cast_url, callback=self.parse_cast)

    def parse_cast(self, response):
        for href in response.css('div.name a::attr(href)'):
            yield response.follow(url=href, callback=self.parse_actor)

    def parse_actor(self, response):
        for href in response.css('div.film-img-box a::attr(href)'):
            yield response.follow(url=href, callback=self.parse_photos)

    def parse_photos(self, response):
        for href in response.css('table.js-rum-hero td b a::attr(href)'):
            yield response.follow(url=href, callback=self.parse_one_photo)

        for href in response.css('div.navigator li.arr a::attr(href)'):
            yield response.follow(url=href, callback=self.parse_photos)

    def parse_one_photo(self, response):
        img_url = response.css('#main_table td img::attr(src)').get()
        person_name = response.css('#main_table td img::attr(alt)').get()[:-1]  # last symbol of name is space
        self.gained_data.append((person_name, img_url))
        self.save_data()

    def close(self, spider, reason):
        self.save_data()
        super(ContryFilmsSpider, self).close(spider, reason)
