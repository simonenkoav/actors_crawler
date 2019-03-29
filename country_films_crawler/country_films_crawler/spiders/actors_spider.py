import scrapy


class ContryFilmsSpider(scrapy.Spider):
    name = "country_films"

    gained_data = []

    def start_requests(self):
        urls = [
            'https://www.kinopoisk.ru/film/255611/cast/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
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

    def close(self, spider, reason):
        self.log('GAINED %d' % len(self.gained_data))
        with open('data/gained_data.txt', 'w') as fd:
            for pname, url in self.gained_data:
                line = pname.replace(' ', '_') + ' ' + url
                fd.write(line + '\n')
        super(ContryFilmsSpider, self).close(spider, reason)
