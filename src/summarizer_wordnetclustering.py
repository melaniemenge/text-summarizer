#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Melanie Menge
# date: 19.03.2020
# description: Text Summarizer
import itertools
import urllib.request
from urllib.error import URLError
import nltk
from bs4 import BeautifulSoup
from nltk.tokenize import *
from pywsd.lesk import simple_lesk
from nltk.corpus import wordnet as wn
import numpy as np
from numpy import dot


class summarizerWordnet:
    """
    Textsummarizer using Wordnet

    Methods
    -------
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

    getFullVerb(token)
        changes the contractions to the
        normal version

    getWordTokenized(sentences)
        tokenizes each sentence

    wordsToCompare(sentences)
        tags all words with the according
        parts-of-speech tag

    simpleLesk(sentence,tag)
        disambiguates a sentence

    wsd(sentences)
        disambiguates all sentences

    getSimilarities(sentsyns)
        compares each synset from each sentence
        with each synset and each other sentences

    firstclustering(senses, sentences, sentenceCount)
        creates a first clustering of the sentences

    getClusteredSentences(newdict)
        reduces each sentence with only the maxvalue
        of similarities to other sentences and clusters
        them once more

    getSimilarSentences(clusters)
        calculates the similarity between
        all the sentences

    getSummary(finaldict,sentencesandsynsets)
        creates the summary which is then
        saved in a new file

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

    def splitData(self, data):
        """
        splits text into sentences and
        replaces unwanted characters

        :param data: list of sentences
        :return: replaced list of sentences
        """
        sentences = []
        for element in data:
            sentences += sent_tokenize(element)
        return sentences

    def getFullVerb(self, token):
        """

        changes contracted tokens
        to full version

        :param token: token
        :return: uncontracted token
        """
        if token == "'ve":
            token = "have"
        elif token == "'d":
            token = "would"
        elif token == "'m":
            token = "am"
        elif token == "'ll":
            token = "will"
        elif token == "'s":
            token = "is"
        elif token == "'re":
            token = "are"
        else:
            pass
        return token

    def getWordTokenized(self, sentences):
        """
        Tokenizes each sentence

        :param sentences: list of sentences
        :return: list of tokenized sentences
        """
        tokenizedwords = [word_tokenize(s) for s in sentences]
        return tokenizedwords

    def wordsToCompare(self, sentences):
        """
        Tags each sentence with the according
        pos-tag

        :param sentences: list of sentences
        :return: list of pos-tagged sentences
        """
        tokens = []
        for sentence in sentences:
            senttokens = word_tokenize(sentence)
            for token in senttokens:
                if re.match(r'^\'\w+', token):
                    token = self.getFullVerb(token)
                    tokens.append(token)
                else:
                    tokens.append(token)
        postoken = nltk.pos_tag(tokens)
        #makes a list of all words that are tagged Nound or Verb, for further processing
        postoken = [tag for tag in postoken if tag[1].startswith('N') or tag[1].startswith('V')]
        return postoken

    def simpleLesk(self, sentence, tag):
        """
        disambiguates a sentence and returns the synset

        :param sentence: tokenized sentence
        :param tag: pos-tag
        :return: synset
        """
        simple = simple_lesk(sentence, tag[0], tag[1][0].lower())
        return simple

    def wsd(self, sentences):
        """
        disambiguates all sentences

        :param sentences: list of sentences
        :return: dictionary with all synsets and count of sentences
        """
        postoken = self.wordsToCompare(sentences)
        sense = {}
        tokenized = self.getWordTokenized(sentences)
        sentenceCount = {}
        c1 = 0
        c2 = 0
        c3 = 0
        for sentence in tokenized:
            for token in sentence:
                if re.match(r'^\'', token):
                    token = self.getFullVerb(token)
                alist = [tag for tag in postoken if token in tag]
                if len(alist) == 0:
                    if token.isalpha():
                        c2 += 1
                else:
                    for tag in alist:
                        sense[tag[0]] = self.simpleLesk(sentences[c1], tag)
                    c3 += 1

            sentenceCount[c1] = (c2, c3)
            c1 += 1
            c2 = 0
            c3 = 0
        return sense, sentenceCount

    def getSimilarities(self, sentsyns):
        """
        elaborates the similarity between all the
        sentences

        :param sentsyns: dictionary of synsets of each sentence
        :return: dictionary with the clustered sentences
        """
        count1 = 0
        clusteredsentences = {}
        while count1 < len(sentsyns):
            values = []
            count2 = 0
            while count2 < len(sentsyns):
                #taking the first synset of the synset-list of sentence A
                for i, synsetA in enumerate(sentsyns[count1]):
                    v = [0.0] * len(sentsyns[count1])
                    similarityranks = []
                    #taking the first synset of the synset-list of sentence B
                    for j, synsetB in enumerate(sentsyns[count2]):
                        if synsetB is not None and synsetA is not None:
                            #get wup_similarity of the two synsets
                            similarity = wn.synset(synsetA.name()).wup_similarity(wn.synset(synsetB.name()))
                        else:
                            similarity = None
                        if similarity is not None:
                            #saving in list
                            similarityranks.append(similarity)
                        else:
                            similarityranks.append(0.0)
                    similarityranks = sorted(similarityranks, reverse=True)
                    v[i] = similarityranks
                    #saving the two compared sentences and their similarity-value
                    values.append((count1 + 1, count2 + 1, v[i]))
                count2 += 1
            clusteredsentences[count1 + 1] = values
            count1 += 1
        return clusteredsentences

    def firstclustering(self, senses, sentences, sentenceCount):
        """
        creates a first clustering of all sentences

        :param senses: dictionary with the synsets
        :param sentences: list of sentences
        :param sentenceCount: dictionary with sentence counts
        :return: clustered sentences in a dictionary and dicitionary with all sentences and their synsets
        """
        sentsyns = []
        sentenceandsentsyns = {}
        count = 0
        for sentence in sentences:
            length = (sentenceCount[count])[1]
            items = list(itertools.islice(senses, length))
            values = []
            for item in items:
                values.append(senses[item])
                del senses[item]
            count += 1
            if len(values) != 0:
                sentsyns.append(values)
            sentenceandsentsyns[count] =(sentence, values) # {1: [synset1, synset2, synset3, ...], 2: [...]}
        clustered = dict(self.getSimilarities(sentsyns))

        return clustered, sentenceandsentsyns

    def getClusteredSentences(self, newdict):
        """
        further clustering of all sentences

        :param newdict: dictionary of sentences and values
        :return: dictionary with the final value for the compared sentences
        """
        count = 0
        keys = newdict.keys()
        c1 = 1
        c2 = 0
        verynewdict = {}
        while count < len(newdict):
            while c1 < len(newdict):
                values = []
                for key in keys: #(sentence1, sentence2)
                    if key[0] == c1: #sentence1
                        values.append(newdict[key]) #appending the similarity-value
                if len(values) != 0:
                    maxvalue = max(values) #getting the maximum value
                else:
                    maxvalue = 0
                for item in newdict.items(): #((sentence1, sentence2), value)
                    if item[1] == maxvalue and item[0][0] == c1: #item[1] = value, item[0][0] = sentence1
                        c2 = item[0][1] #get sentence 2
                if (c2, c1) in newdict.keys():
                    del newdict[(c2, c1)] #delete duplicate from newdict
                verynewdict[(c1, c2)] = maxvalue
                c1 += 1
            count += 1
        return verynewdict

    def getSimilarSentences(self, clusters):
        """
        elaborating the similarity between the sentences

        :param clusters: dictionary of the sentences
        :return: dictionary with the clustered sentences
        """
        newdict = {}
        c = 1

        while c <= len(clusters):
            b = 2
            while b <= len(clusters):
                a = 0
                d = 1
                sent1 = clusters[c]
                sent2 = clusters[b]
                array1 = []
                if c != b:
                    while d < len(sent1):
                        if sent1[d][1] == b:
                            for element in sent1[d][2]:
                                array1.append(element)
                        d += 1
                    array1 = np.array(array1) #creating numpy-array for further processing
                    array2 = []
                    while a < len(sent2):
                        if sent2[a][1] == c:
                            for element in sent2[a][2]:
                                array2.append(element)
                        a += 1
                    array2 = np.array(array2)
                    #normalizes the arrays
                    a1 = np.linalg.norm(array1)
                    a2 = np.linalg.norm(array2)
                    #calculates the dot-product of the two normalized arrays
                    dotproduct = dot(a1, a2)
                    c1 = len(array1)
                    c2 = len(array2)
                    sigm = (c1 + c2) / 1.8
                    similarity = dotproduct / sigm
                    sents = (c, b)
                    newdict[sents] = similarity
                d += 1
                b += 1
            c += 1
        anotherdict = self.getClusteredSentences(newdict)
        return anotherdict

    def getSummary(self,finaldict, sentencesandsensynts):
        """

        creates the summary and saves it in a file

        :param finaldict: dictionary with the values of the compared sentences
        :param sentencesandsensynts: sentences and their synsets
        :return:
        """
        sentences = []
        file = open('summary_wordnet.txt', 'w')
        file.write("This is your generated summary: \n\n")
        #sorting dictionary for highest score first
        finaldict = {k: v for k,v in sorted(finaldict.items(), key=lambda item: item[1])}
        for key,value in finaldict.items():
            if key[1] not in sentences:
                sentences.append(key[1])

        for key2, value2 in sentencesandsensynts.items():
            if key2 in sentences:
                file.write(value2[0] + "\n")

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