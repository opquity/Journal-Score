from pandas import read_excel
from django.conf import settings
from os import path
import requests
#from bs4 import BeautifulSoup
from re import compile

JIF_path = path.join(settings.BASE_DIR, 'static', 'fileUpload','JCR_RANKINGS.xlsx')
JIF_table = read_excel(JIF_path)

class HTMLFile:
    def __init__(self, link, category):
        self.url = link
        self.category = category
        self.veracity = 0

    def read_html(self):
        try:
            response = requests.get(self.url)
        except Exception as e:
            print(e)
            return False
        else:
            if response.status_code:
                # text = BeautifulSoup(response.text, "html.parser").get_text()
                text = response.text
                return text
            return False
    
    def clean_html(self, html):
        return html
    
    def check_methdology(self, text):
        pattern = compile(r"<h\d>[\s\w\d\.|]*methodology")
        match = pattern.search(text)
        return match
    
    def evaluate_methodology(self, text):
        methdology_level = 0
        have_sample_size = self.check_sample_size(text)
        if have_sample_size:
            methdology_level += 1
        have_standard_deviation = self.check_standard_deviation(text)
        if have_standard_deviation:
            methdology_level += 1
        have_confidence_level = self.check_confidence_level(text)
        if have_confidence_level:
            methdology_level += 1
        have_p_value = self.check_p_value(text)
        if have_p_value:
            methdology_level += 1
        if methdology_level>3:
            self.veracity += 10
        elif methdology_level>0 and methdology_level<3:
            self.veracity += 5
        else:
            self.veracity += 0
        return self.veracity
       
    def check_sample_size(self, text):
        pattern = compile(r"<p>[\s\w\d\.|]*sample size")
        match = pattern.search(text)
        return match
        
    def check_standard_deviation(self, text):
        pattern = compile(r"<p>[\s\w\d\.|]*standard deviation")
        match = pattern.search(text)
        return match
        
    def check_confidence_level(self,text):
        pattern = compile(r"<p>[\s\w\d\.|]*confidence level")
        match = pattern.search(text)
        return match
        
    def check_p_value(self, text):
        pattern = compile(r"<p>[\s\w\d\.|]*(p value|ANOVA)")
        match = pattern.search(text)
        return match
         
    def check_category(self):
        if self.category in JIF_table['CATEGORY NAME'].values:
            return JIF_table['2019 IMPACT FACTOR'].loc[JIF_table['CATEGORY NAME'] == self.category].values[0]
        return False

    def main(self):
        html = self.read_html()
        doc = self.clean_html(html)
        if doc is not None:
            print("Text", doc[:2000])
            JIF = self.check_category()
            if JIF:
                self.veracity += 10
                if JIF>0 and JIF<=2:
                    self.veracity += 1
                elif JIF>2 and JIF<=5:
                    self.veracity += 3
                elif JIF>5 and JIF<=10:
                    self.veracity += 5
                else:
                    self.veracity += 10
                have_methdology_section = self.check_methdology(doc)
                if have_methdology_section:
                    score = self.evaluate_methodology(doc)
                    return score
                else:
                    return self.veracity
            else:
                have_methdology_section = self.check_methdology(doc)
                if have_methdology_section:
                    score = self.evaluate_methodology(doc)
                    return score
                else:
                    return 'commentary/opinion'
        return "unable to read from the webpage"    