# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import html2text
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
import pickle
import os
import usaddress
import pyap
import phonenumbers
import string
import csv
import datetime


class FacilitiesPipeline(object):
    dirname = os.path.dirname(__file__)
    classifier = open(os.path.join(dirname, 'classify\\classifier.pkl'), 'rb')
    classifier = pickle.load(classifier)
    vectorizer = open(os.path.join(dirname, 'classify\\vectorizer.pkl'), 'rb')
    vectorizer = pickle.load(vectorizer)
    transformer = open(os.path.join(dirname, 'classify\\transformer.pkl'), 'rb')
    transformer = pickle.load(transformer)
    pipeline = Pipeline([
        ('vect', vectorizer),
        ('tfidf', transformer),
        ('clf', classifier)
    ])

    def clean_html(self, string, replace=" "):
            """Pass in html as text.
            
            Arguments:
                string {str} -- HTML
            
            Keyword Arguments:
                replace {str} -- Choose what to replace regex matches with, by default one whitespace (default: {" "})
            
            Returns:
                [str] -- Returns cleaned up HTML
            """
            file_regex = '\S*\.(?:jpg|gif|png|pdf|doc|docx)'
            new_line_regex = '\\n'
            url_regex = '(http|https|www)+\S+\s?'
            url_regex_2 = '\S+\.(com|org|edu|gov)\S*'
        
            string = html2text.html2text(string)
            string = re.sub(file_regex, replace, string)
            string = re.sub(new_line_regex, replace, string)
            string = re.sub(url_regex, replace, string)
            string = re.sub(url_regex_2, replace, string)

            return string

    
    def remove_whitespace(self, string):
        """Takes in string and removes whitespaces between numbers.
        
        Arguments:
            string {String} -- Raw text (Unstructured)
        
        Returns:
            String -- Input string with whitespaces removed between digits.
        """
        split = list(string)
        remove = []
        digit_found = False
        for i in range(len(split)):
            if str.isdigit(split[i]):
                digit_found = True
            if digit_found:
                if str.isalpha(split[i]):
                    digit_found = False
                if split[i] == ' ':
                    remove.append(i)
        remove = remove
        remove.sort(reverse=True)
        for index in remove:
            del split[index]
        return ''.join(split)


    def add_whitespace(self, string):
        """Adds whitespaces between digits and letters.
        
        Arguments:
            string {String} -- Raw text (Unstructured)
        
        Returns:
            String -- Input string with whitespaces removed between digits.
        """
        split = list(string)
        add = []
        for i in range(len(split)):
            if str.isdigit(split[i]) and i > 0:
                if str.isalpha(split[i-1]):
                    add.append(i)
                elif i != (len(split) - 1) and str.isalpha(split[i+1]):
                    add.append(i+1)
        prev = 0
        breaks = []
        for elem in add:
            breaks.append(split[prev:elem])
            prev = elem
        if (len(split) - 1) not in add:
            breaks.append(split[prev:])
        res = ''
        for lst in breaks:
            res += ''.join(lst) + ' '
        return res


    def find_numbers(self, text):
        """Gets unstructured text and parses for phone numbers.
        
        Arguments:
            text {String} -- Raw text (Unstructured)
        
        Returns:
            List[String] -- List of phone numbers found in unstructured text.
        """
        text = self.add_whitespace(text)
        found_numbers = []
        for number in phonenumbers.PhoneNumberMatcher(text, region='US'):
            found_numbers.append(number.raw_string)
        return list(set(found_numbers))
        

    def find_addresses(self, string, country="US"):
        """Takes in unstructured text and returns addresses found.
        
        Arguments:
            string {String} -- Raw text (Unstructured)
        
        Keyword Arguments:
            country {String} -- Country code for address parsing. (default: {"US"})
        
        Returns:
            List[List[Tuples(Strings)]] -- List of addresses. Top-level lists are addresses split into tuples.
        """
        extracted = pyap.parse(string, country=country)
        parsed = []
        for address in extracted:
            parsed.append(usaddress.parse(str(address)))
        return parsed
    

    def clean_addresses(self, adds):
        """Splits up parsed addresses into its parts.
        
        Arguments:
            adds {List[List{String}]} -- List of List of Addresses
        
        Returns:
            Lists -- Addresses, Cities, and States
        """
        addresses = []
        cities = []
        states = []

        for address in adds: 
            add = ""
            state = ""
            city = ""
            for element in address:
                add += element[0] + " "
                try:
                    if element[1] == 'StateName':
                        state = element[0].translate(str.maketrans('', '', string.punctuation))
                    elif element[1] == 'PlaceName':
                        city = element[0].translate(str.maketrans('', '', string.punctuation))
                except:
                    pass
            addresses.append(add)
            cities.append(city)
            states.append(state)
        return addresses, cities, states


    def process_item(self, item, spider):
        """Takes scraped pages, determines if relevant and then extracts addresses, phone numbers, cities and states.
        
        Arguments:
            item {Scrapy Item} -- Dictionary like object with url and page text
            spider {Scrapy spider} -- Spider
        
        Raises:
            DropItem: Drop Item if there is no address and phone numbers on page.
            DropItem: Drop Item if not relevant.
        
        Returns:
            Scrapy Item -- Scrapy item with url, addresses, cities, states and phone numbers.
        """
        if 'text' in item.keys():
            item['text'] = self.clean_html(item['text'])
            print("\n\n\n\nIt worked\n\n\n\n")
            return item

        
        text = self.clean_html(item['addresses'])

        if self.pipeline.predict([text])[0]:
            adds = self.clean_addresses(self.find_addresses(text))
            item['addresses'] = adds[0]
            item['phone_numbers'] = self.find_numbers(text)
            item['city'] = adds[1]
            item['state'] = adds[2]

            if len(item['addresses']) == 0 and len(item['phone_numbers']) == 0:
                raise DropItem("No addresses or phone numbers found: %s" % item['url'])
        else:
            raise DropItem("Page not classified as relevant: %s" % item['url'])
        
        return item

class toCSVPipeline(object):
    dirname = os.path.dirname(__file__)
    time = datetime.datetime.today()
    time = time.strftime('%m-%d_%H-%M')
    path = 'scraped\\scraped_information_' + time + '.csv'
    csv_file_path = os.path.join(dirname, path)

    def write_to_csv(self, item):
        writer = csv.writer(open(self.csv_file_path, 'a'), lineterminator='\n')
        writer.writerow([item[key] for key in item.keys()])

    def process_item(self, item, spider):

        self.write_to_csv(item)
        return item   