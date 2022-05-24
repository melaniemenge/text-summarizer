#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Melanie Menge
# date: 19.03.2020
# description: Text Summarizer

import nltk

from nltk.tokenize import *
from nltk.corpus import *
from nltk.stem import PorterStemmer
import re
nltk.download('stopwords')
def filehandler():
    filename = "insects_adventure.txt"
    infile = open(filename, "r")
    data = infile.readlines()
    infile.close()
    return data


def splitText(data):
    sentences = [sent_tokenize(s) for s in data]
    fixedSents = []
    for element in sentences:
        if len(element) != 0:
            for i in element:
                if i == "":
                    element.remove(i)
                else:
                    i = re.sub(r"^\s+", "", i)
                    fixedSents.append(i)

        else:
            sentences.remove(element)

    return fixedSents


def frequency(sentences):
    swords = set(stopwords.words('english'))
    porterstemmer = PorterStemmer()

    dictionary = {}

    for sentence in sentences:
        words = word_tokenize(sentence)
        for word in words:
            word = porterstemmer.stem(word)
            if word not in swords:
                if word in dictionary:
                    dictionary[word] += 1
                else:
                    dictionary[word] = 1

    return dictionary


sentences = splitText(filehandler())
print(frequency(sentences))