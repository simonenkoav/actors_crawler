import scrapy


class ContryFilmsSpider(scrapy.Spider):
    name = "country_films"

    gained_data = []

    asian_countries = {'Вьетнам': 52, 'Вьетнам Северный': 170, 'Гонконг': 28, 'Казахстан': 122, 'Китай': 31,
                       'Корея': 156, 'Корея Северная': 137, 'Корея Южная': 26, 'Кыргызстан': 86, 'Малайзия': 83,
                       'Монголия': 132, 'Мьянма': 1034, 'Сиам': 1021, 'Сингапур': 45, 'Таджикистан': 70, 'Таиланд': 44,
                       'Тайвань': 27, 'Туркменистан': 152, 'Узбекистан': 71, 'Филиппины': 47, 'Япония': 9}

    main_url = 'https://www.kinopoisk.ru/lists/m_act[country]/%d'

    def start_requests(self):
        urls = [self.main_url % code for code in self.asian_countries.values()]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_country)

    def parse_country(self, response):
        for film_info in response.css('div.tenItems div.item'):
            film_url = film_info.css('div.info div.name a::attr(href)')[0]
            film_countries = film_info.css('div.flags div.flag a::attr(title)').getall()
            if all(c in self.asian_countries for c in film_countries):
                yield response.follow(url=film_url, callback=self.parse_film)

        for href in response.css('div.navigator li.arr a::attr(href)'):
            yield response.follow(url=href, callback=self.parse_country)

    def parse_film(self, response):
        cast_url = response.css('#actorList h4 a::attr(href)')[0]
        self.log('cast_url ' + str(cast_url.get()))
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

    def close(self, spider, reason):
        self.gained_data = list(set(self.gained_data))
        self.log('GAINED %d' % len(self.gained_data))
        with open('../data/asians_gained_data.txt', 'w') as fd:
            for pname, url in self.gained_data:
                line = pname.replace(' ', '_') + ' ' + url
                fd.write(line + '\n')
        super(ContryFilmsSpider, self).close(spider, reason)
