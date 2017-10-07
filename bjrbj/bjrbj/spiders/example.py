# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin
import scrapy
from scrapy.shell import inspect_response
from scrapy import Request


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = \
        ['www.bjrbj.gov.cn']
    start_urls = \
        ["http://www.bjrbj.gov.cn/LDJAPP/search/ddyy/"
         "ddyy_01_outline_new.jsp?sword="]
        #['http://www.bjrbj.gov.cn/LDJAPP/search/ddyy/ddyy_01_outline_new.jsp/']

    INFO_PATTERN = re.compile('<font.*【<b>(?P<key>.*)</b>】'
                              '</font>(?P<value>.*)</font>')

    def parse(self, response):
        #inspect_response(response, self)

        # table entries
        all_entries = response\
            .css("html body center table tr td:nth-child(1) span")\
            .xpath('a[contains(@href,"id")]')[::2]  # only first ones

        for entry in all_entries:
            entry_url = urljoin(response.url,
                                entry.xpath("@href").extract_first())
            req = Request(entry_url, callback=self.parse_detail)
            req.meta['id_number'] = entry.xpath("text()").extract_first()
            yield req

        # next page
        next_page_url = response\
            .css("html body center table tr td:nth-child(1) span")\
            .xpath("a[contains(text(),'下一页')]")\
            .xpath("@href").extract_first()

        yield Request(urljoin(response.url, next_page_url),
                      callback=self.parse)

    def parse_detail(self, response):
        infos = response.css("td table td").xpath('font').extract()
        item = {}
        item['id_number'] = int(response.meta['id_number'])
        for info in infos:
            kv = self.INFO_PATTERN.match(info).groupdict()
            item[kv['key']] = kv['value']
        yield item
