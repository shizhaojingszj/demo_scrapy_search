# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Item
from scrapy.http import FormRequest
from scrapy.shell import inspect_response

class AQ(object):
    timestamp_pat = re.compile("(?P<year>\d{4})年"
                               "(?P<month>\d{2})月"
                               "(?P<day>\d{2})日"
                               "(?P<hour>\d{2}):"
                               "(?P<minute>\d{2}):(?P<second>\d{2})")
    name_pat = re.compile("“(?P<name>.*)”的问题")

    def __init__(self, aq_block):
        '''
        This is a class for parsing scrapy.selector obj
        '''
        assert isinstance(aq_block, scrapy.selector.unified.Selector), \
            type(aq_block)
        self._aq_block = aq_block
        self.ask_time, *self.answer_time = self._parse_times()
        self.name = self._parse_names()
        self.ques = self._parse_ques()

    def _parse_times(self):
        '''
        self.ask_time and self.answer_time
        '''
        block = self._aq_block
        times = block.css("h1 span").extract()
        assert len(times) >= 2, times
        res = []
        # only get first 2(one should be ask, the other should be answer)
        for time in times:
            match = AQ.timestamp_pat.search(time)
            assert match, time
            res.append({k: int(v) for k, v in match.groupdict().items()})
        return res

    def _parse_names(self):
        '''
        self.name
        '''
        block = self._aq_block
        name = block.select("h1/text()")[0].extract()
        match = AQ.name_pat.match(name)
        assert match, name
        return match.groupdict()['name']

    def _parse_ques(self):
        '''
        ques
        '''
        block = self._aq_block
        ques = block.css("div.ques").select("text()").extract()
        res = []
        # first is question
        for x in ques:
            res.append(x.strip())
        return res

    def report(self):
        '''
        to a dict
        '''
        return {
            "name": self.name,
            "ask_time": self.ask_time,
            "answer_time": self.answer_time,
            "ques": self.ques
        }


class AllSpider(scrapy.Spider):
    name = 'all'
    allowed_domains = ['apply.bjhjyd.gov.cn']
    start_urls = ['http://apply.bjhjyd.gov.cn/apply/zczx/result.html']

    def parse(self, response):
        #inspect_response(response, self)
        all_aq = response.selector.css(
            "div.blist#consult > dl > dd div.sconsul")
        for n, aq in enumerate(all_aq, 1):
            aq_obj = AQ(aq)
            yield aq_obj.report()
        # next_page
        next_page_index = response.selector.xpath("//a[@pageno]/text()") \
                                           .extract().index("下一页")
        next_page_number = (response.selector.xpath("//a[@pageno]")
                            [next_page_index].xpath("@pageno")
                            .extract_first())
        yield FormRequest(response.url, callback=self.parse,
                          formdata={"pageNo": next_page_number})
