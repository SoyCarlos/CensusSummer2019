# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
import os
import pandas as pd


class GetTrainingDataSpider(scrapy.Spider):
    name = 'get_training_data'

    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 'targets/training_targets.csv')
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
                    'text': response.text
                }
