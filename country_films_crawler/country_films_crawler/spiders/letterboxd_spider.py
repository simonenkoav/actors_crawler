import scrapy
from country_films_crawler.utils import *
from urllib.parse import urljoin


class CountryFilmsLtbSpider(scrapy.Spider):
    name = "films_ltb"

    countries = load_list('../data/scrap/letterboxd_black_countries.txt')
    main_url = 'https://letterboxd.com/films/ajax/popular/country/%s/size/small/'

    save_path = '../data/download/black_actors_ltb.txt'

    gained_data = []

    def save_data(self):
        self.gained_data = list(set(self.gained_data))
        self.log('GAINED %d' % len(self.gained_data))
        save_list(self.gained_data, self.save_path)

    def start_requests(self):
        urls = [self.main_url % country for country in self.countries]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_country)

    def parse_country(self, response):
        film_urls = response.css('ul.poster-list li.listitem div.react-component a::attr(href)')
        for url in film_urls:
            yield response.follow(url=url, callback=self.parse_film)

        for url in response.css('div.paginate-nextprev a.next::attr(href)'):
            yield response.follow(url=url, callback=self.parse_country)

    def parse_film(self, response):
        country_field = response.css('#tab-details div.text-sluglist')[1]
        countries_urls = country_field.css('p a::attr(href)').getall()
        film_countries = [v.split('/')[-2] for v in countries_urls]
        if all(c in self.countries for c in film_countries):
            cast_urls = response.css('#tab-cast div.cast-list p a::attr(href)')
            for url in cast_urls:
                yield response.follow(url=url, callback=self.parse_person)
            crew_urls = response.css('#tab-crew div.text-sluglist p a::attr(href)')
            for url in crew_urls:
                yield response.follow(url=url, callback=self.parse_person)

    def parse_person(self, response):
        yield scrapy.Request(url=urljoin(response.css('p.text-link a::attr(href)').get(), 'images/profiles/'),
                             callback=self.parse_tmdb_page)

    def parse_tmdb_page(self, response):
        name = response.css('div.header div.single_column div.title a h2::text').get()
        urls = response.css('div.white_column section.panel div.results ul.images '
                            'li div.image_content a::attr(href)').getall()
        for url in urls:
            self.gained_data.append((name, url))

    def close(self, spider, reason):
        self.save_data()
        super(CountryFilmsLtbSpider, self).close(spider, reason)


