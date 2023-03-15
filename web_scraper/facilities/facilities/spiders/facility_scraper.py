# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
import pandas as pd
import os


class FacilityScraper(scrapy.Spider):
    name = 'facility_scraper'

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'targets/targets.csv')
    targets = pd.read_csv(path)
    allowed_domains = targets['domain'].values
    start_urls = targets['starter'].values
    custom_settings = {
        'DEPTH_LIMIT': 5,
        'DEPTH_PRIORITY': 1
    }
    visited = []


    def parse(self, response):           
        for link in LinkExtractor(allow=()).extract_links(response):
            yield response.follow(link.url, self.parse)
            if response.url not in self.visited:
                self.visited.append(response.url)
                yield {
                    'url': response.url,
                    'addresses': response.text,
                    'city': "",
                    'state': "",
                    'phone_numbers': ""
                }

