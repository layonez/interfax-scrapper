# -*- coding: utf-8 -*-
from scrapy import Request, Spider
from datetime import timedelta, date
from re import compile


def daterange(start_date, end_date):
    d = start_date
    delta = timedelta(days=1)
    while d <= end_date:
        yield d
        d += delta


class JobsSpider(Spider):
    def __init__(self, start_date, end_date, *args, **kwargs):
        super(JobsSpider, self).__init__(*args, **kwargs)
        # extract date part of url
        p = compile('\\d{4}\\/\\d{2}\\/\\d{2}')
        if p.search(start_date) is None or p.search(end_date) is None:
            raise ValueError(
                'Required params start_date and end_date should be in format yyyy/MM/dd\n' +
                'your input was start_date={} end_date={}'.format(start_date, end_date))

        self.start_date = start_date
        self.end_date = end_date

    name = 'jobs'
    allowed_domains = ['interfax.ru']
    custom_settings = {
        # specifies exported fields and order
        'FEED_EXPORT_FIELDS': ['Date', 'Title', 'Link', 'Tags', 'Description', 'Text'],
    }

    def start_requests(self):
        st_year, st_month, st_day = int(self.start_date[0:4]), int(
            self.start_date[5:7]), int(self.start_date[8:10])
        end_year, end_month, end_day = int(self.end_date[0:4]), int(
            self.end_date[5:7]), int(self.end_date[8:10])

        for d in daterange(date(st_year, st_month, st_day), date(end_year, end_month, end_day)):
            day = '%02d' % d.day
            month = '%02d' % d.month
            year = '%04d' % d.year
            yield self.make_requests_from_url("https://www.interfax.ru/news/{}/{}/{}".format(year, month, day))

    def parse(self, response):
        news_list = response.css('div.an>div')
        # extract date part of url
        p = compile('\\d{4}\\/\\d{2}\\/\\d{2}')

        date = p.findall(response.request.url)[0].replace('/', '.')

        for news in news_list:
            title = news.css('a>h3::text').extract_first()
            time = news.css('span::text').extract_first()
            link = news.css('a::attr(href)').get()
            if link.startswith('/'):
                link = 'https://www.interfax.ru' + link
            description = news.css('.showText::text').extract_first()
            yield response.follow(link,
                                  callback=self.parse_details,
                                  meta={'Date': date + ' ' + time, 'Title': title, 'Link': link, 'Description': description})

        relative_next_url = response.css('.pages>a.active+a::attr(href)').get()
        if relative_next_url:
            absolute_next_url = response.urljoin(relative_next_url)
            yield Request(absolute_next_url, callback=self.parse)

    def parse_details(self, response):
        text = response.css(
            'article[itemprop="articleBody"]>p::text,div.wg_script_block::text').extract()

        tags = ''
        tagsEls = response.css('div.textMTags>a')
        for idx, tagEl in enumerate(tagsEls):
            tags += (',' if idx > 0 else '') + \
                tagEl.css('::text').extract_first()

        yield{'Date': response.meta['Date'],
              'Title': response.meta['Title'],
              'Link': response.meta['Link'],
              'Text': text,
              'Tags': tags,
              'Description': response.meta['Description']}
