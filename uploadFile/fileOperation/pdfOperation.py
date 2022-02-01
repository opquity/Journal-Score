import fitz
from pandas import read_excel
from re import compile
from os import path
from operator import itemgetter
from django.conf import settings


JIF_path = path.join(settings.BASE_DIR, 'static', 'fileUpload','JCR_RANKINGS.xlsx')
JIF_table = read_excel(JIF_path)

class PDFFile:
    def __init__(self,file,category):
        self.file = file
        self.category = category
        self.veracity = 0

    def fonts(self, doc, granularity=False):
        """
        Extracts fonts and their usage in PDF documents.
        :param doc: PDF document to iterate through
        :type doc: <class 'fitz.fitz.Document'>
        :param granularity: also use 'font', 'flags' and 'color' to discriminate text
        :type granularity: bool
        :rtype: [(font_size, count), (font_size, count}], dict
        :return: most used fonts sorted by count, font style information
        """
        styles = {}
        font_counts = {}
        for page in doc:
            blocks = page.getText("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                if b['type'] == 0:  # block contains text
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if granularity:
                                identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                                styles[identifier] = {  
                                                        'size': s['size'],
                                                        'flags': s['flags'],
                                                        'font': s['font'],
                                                        'color': s['color']
                                                    }
                            else:
                                identifier = "{0}".format(s['size'])
                                styles[identifier] = {
                                                        'size': s['size'],
                                                        'font': s['font']
                                                    }

                            font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

        font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)
        if len(font_counts) < 1:
            raise ValueError("Zero discriminating fonts found!")

        return font_counts, styles

    def font_tags(self, font_counts, styles):
        """
        Returns dictionary with font sizes as keys and tags as value.
        :param font_counts: (font_size, count) for all fonts occuring in document
        :type font_counts: list
        :param styles: all styles found in the document
        :type styles: dict
        :rtype: dict
        :return: all element tags based on font-sizes
        """
        p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
        p_size = p_style['size']  # get the paragraph's size

        # sorting the font sizes high to low, so that we can append the right integer to each tag
        font_sizes = []
        for (font_size, count) in font_counts:
            font_sizes.append(float(font_size))
        font_sizes.sort(reverse=True)

        # aggregating the tags for each font size
        idx = 0
        size_tag = {}
        for size in font_sizes:
            idx += 1
            if size == p_size:
                idx = 0
                size_tag[size] = '<p>'
            if size > p_size:
                size_tag[size] = '<h{0}>'.format(idx)
            elif size < p_size:
                size_tag[size] = '<s{0}>'.format(idx)

        return size_tag

    def attaching_tags(self, doc, size_tag):
        """
        Scrapes headers & paragraphs from PDF and return texts with element tags.
        :param doc: PDF document to iterate through
        :type doc: <class 'fitz.fitz.Document'>
        :param size_tag: textual element tags for each size
        :type size_tag: dict
        :rtype: list
        :return: texts with pre-prended element tags
        """
        element_tag = []  # list with headers and paragraphs
        first = True  # boolean operator for first header
        previous_s = {}  # previous span

        for page in doc:
            blocks = page.getText("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                if b['type'] == 0:  # this block contains text
                    # REMEMBER: multiple fonts and sizes are possible IN one block
                    block_string = ""  # text found in block
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if s['text'].strip():  # removing whitespaces:
                                if first:
                                    previous_s = s
                                    first = False
                                    block_string = size_tag[s['size']] + s['text']
                                else:
                                    if s['size'] == previous_s['size']:
                                        if block_string and all((c == "|") for c in block_string):
                                            # block_string only contains pipes
                                            block_string = size_tag[s['size']] + s['text']
                                        if block_string == "":
                                            # new block has started, so append size tag
                                            block_string = size_tag[s['size']] + s['text']
                                        else:  # in the same block, so concatenate strings
                                            block_string += " " + s['text']

                                    else:
                                        block_string += size_tag[s['size']]
                                        element_tag.append(block_string)
                                        block_string = size_tag[s['size']] + s['text']

                                    previous_s = s

                        # new block started, indicating with a pipe
                        block_string += "|"

                    block_string += size_tag[s['size']]
                    element_tag.append(block_string)
        return element_tag

    def read_pdf(self):
        try:
            doc = fitz.open(self.file)
            font_counts, styles = self.fonts(doc, granularity=False)
            size_tag = self.font_tags(font_counts, styles)
            elements = self.attaching_tags(doc, size_tag)
            text = ' '.join(elements)
        except Exception:
            return False
        else:
            return text

    def check_methdology(self,text):
        pattern = compile("<h\d>[\s\w\d\.|]*Methodology[\s\w\d\.|]*<h\d>")
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

    def check_category(self):
        if self.category in JIF_table['CATEGORY NAME'].values:
            return JIF_table['2019 IMPACT FACTOR'].loc[JIF_table['CATEGORY NAME'] == self.category].values[0]
        return False

    def check_sample_size(self, text):
        pattern = compile(r"<p>[\s\w\d\.|]*sample size")
        match = pattern.search(text)
        return match
        
    def check_standard_deviation(self, text):
        pattern = compile(r"<p>[\s\w\d\.|]*standard deviation")
        match = pattern.search(text)
        return match
        
    def check_confidence_level(self, text):
        pattern = compile(r"<p>[\s\w\d\.|]*confidence level")
        match = pattern.search(text)
        return match
        
    def check_p_value(self, text):
        pattern = compile(r"<p>[\s\w\d\.|]*(p value|ANOVA)")
        match = pattern.search(text)
        return match
        
    def main(self):
        # doc = fitz.open(self.file)
        # font_counts, styles = self.fonts(doc, granularity=False)
        # size_tag = self.font_tags(font_counts, styles)
        # elements = self.attaching_tags(doc, size_tag)
        # text = ' '.join(elements) 
        doc = self.read_pdf()
        if doc:
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
