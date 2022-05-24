#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Melanie Menge
# date: 19.03.2020
# description: Text Summarizer

from urllib.error import URLError
from bs4 import BeautifulSoup
import urllib.request
from nltk.tokenize import *
from nltk.corpus import *
from nltk.stem import PorterStemmer
import re
from langdetect import detect

class summarizer:
    """
    Textsummarizer using ranking

    Methods
    -------
    filehandler(filename)
        opens the input file and reads its lines,
        saves the retrieved data in a list

    webscraper(url)
        gets the text from a website and saves it
        in a list

    texthandler(text)
        saves the raw text input in a list

    splitText(data)
        tokenizes the text and replaces
        words/elements which are not used

    frequency(sentences, language)
        checks the language of the text
        and calculates the frequency of
        each word in the text

    rating(sentences, dictionary)
        rates the sentences according to the
        frequency of the words in the sentence

    average(rank)
        calculates the average of the
        before calculated ratings

    summary(sentences, rank, threshold, count)
        writes the summary into an output file according
        to the threshold and count of sentences

    getError()
        returns the error-count

    getErrorMessage()
        returns the error-messages
    """
    error = 0
    errors = []
    data = []

    def filehandler(self, filename):
        """
        opens and reads input file

        :param filename: filename of the input file
        :return: list of sentences
        """
        try:
            infile = open(filename, "r")
            data = infile.readlines()
            infile.close()
            return data
        except FileNotFoundError as e:
            self.error += 1
            self.errors.append(e)

    def webscraper(self, url):
        """
        gets text from website

        :param url: url for retrieving the text
        :return: list of sentences
        """
        try:
            geturl = urllib.request.urlopen(url)
            page = geturl.read()
            parsedpage = BeautifulSoup(page, 'lxml')
            text = parsedpage.find_all('p')
            for p in text:
                line = p.text
                self.data.append(line)
            return self.data
        except URLError as e:
            self.error += 1
            self.errors.append(e)



    def texthandler(self, text):
        """
        gets the text from raw input

        :param text: raw text input
        :return: list of sentences
        """
        text = sent_tokenize(text)
        for element in text:
            self.data.append(element)
        return self.data

    def splitText(self, data):
        """
        splits text into sentences and
        replaces unwanted characters

        :param data: list of sentences
        :return: replaced list of sentences
        """
        sentences = [sent_tokenize(s) for s in data]
        fixedSents = []
        for sentence in sentences:
            if len(sentence) != 0 and len(sentence) < 20:
                for i in sentence:
                    if i == "" or i == ".":
                        sentence.remove(i)
                    else:
                        """
                        replacing spaces at beginning of sentence
                                  parentheses
                                  every character which is not a-z A-Z äöü ÄÖÜ or 0-9
                                  characters in brackets
                        """
                        i = re.sub(r"^\s+", "", i)
                        i = re.sub(r'\(.+\)', ' ', i)
                        i = re.sub(r'[^a-zA-ZäöüÄÖÜ0-9]', ' ', i)
                        i = re.sub(r'\[[0-9]*\]', ' ', i)
                        fixedSents.append(i)

            else:
                sentences.remove(sentence)

        return fixedSents

    def frequency(self, sentences, language):
        """
        checks the language of the text and
        calculates the frequency of the words
        in the text

        :param sentences: list of sentences
        :param language: language input
        :return: dictionary with the frequency of the words
        """
        lang = ""
        if language == "english":
            lang = 'en'
        elif language == "german":
            lang= 'de'
        elif language == "french":
            lang = 'fr'
        elif language == "spanish":
            lang = 'es'
        else:
            pass

        langcheck = detect(sentences[0])
        if langcheck != lang:
            self.error += 1
            self.errors.append("Wrong language selection!")
        else:
            swords = set(stopwords.words(language))
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

    def rating(self, sentences, dictionary):
        """
        rates the sentences according to the
        frequency of words in each sentence

        :param sentences: list of sentences
        :param dictionary: dictionary with the frequency of each word
        :return: dictionary with the rating of each sentence
        """
        rank = {}
        for sentence in sentences:
            numwords = len(word_tokenize(sentence))
            words = word_tokenize(sentence.lower())
            """
            for each word in the sentence, it is checked if the word is a key 
            of the frequency dictionary. 
            if it is, then the frequency of the word is added to the sentence.
            the rating is calculated as:
                sum of frequency divided by number of words in sentence
            """
            for word in words:
                if word in dictionary.keys():
                    if sentence in rank.keys():
                        rank[sentence] += dictionary[word]
                    else:
                        rank[sentence] = dictionary[word]
            if sentence in rank:
                rank[sentence] = rank[sentence] / numwords
        return rank

    def average(self, rank):
        """
        calculates the average of all rankings

        :param rank: dicitonary with the rating of each sentence
        :return: average rating
        """
        sum = 0
        for ranknum in rank:
            sum += rank[ranknum]

        avg = sum / len(rank)

        return avg

    def summary(self, sentences, rank, threshold, count):
        """
        creates the summary and saves it in a file.

        :param sentences: list of sentences
        :param rank: dictionary with the rating of each sentence
        :param threshold: average rating
        :param count: count of sentences in the summary
        """
        c = int(count) - 1
        sentcount = 0
        file = open('summary_ranking.txt', 'w')
        file.write("This is your generated summary: \n\n")
        for sentence in sentences:
            if sentence in rank.keys() and rank[sentence] > threshold:
                file.write(sentence + "\n")
                sentences.remove(sentence)
                if sentcount >= c or len(sentences) == 0:
                    break
                else:
                    sentcount += 1
        file.close()

    def getErrors(self):
        """
        returns the count of errors
        :return: error-count
        """
        return self.error


    def getErrorMessage(self):
        """
        returns the error messages
        :return: error-message
        """
        for message in self.errors:
            return message