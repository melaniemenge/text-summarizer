#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Melanie Menge
# date: 19.03.2020
# description: Commandline interface for the summarizer

import time
from colored_logs.logger import Logger, LogType
from summarizer_ranking import summarizer
from summarizer_wordnetclustering import summarizerWordnet
log = Logger(ID='summarizing')
s = summarizer()
s2 = summarizerWordnet()
desicion = input("Do You want to use Wordnet or Ranking? (w/r)")
userinput = input("Please enter a txt-file, an url or a text to summarize: ")
if desicion == "r":
    sentcount = input("How many sentences do you want to summarize? ")
    language = input("Language: ")

log.start_process('This is taking a while')
if userinput[:4] == "http":
    if desicion == "r":
        sentences = s.webscraper(userinput)
    else:
        sentences = s2.webscraper(userinput)
elif userinput[-4:] == ".txt":
    if desicion == "r":
        sentences = s.filehandler(userinput)
    else:
        sentences = s2.filehandler(userinput)
else:
    if desicion == "r":
        sentences = s.texthandler(userinput)
    else:
        sentences = s2.texthandler(userinput)
if desicion == "r":
    if s.getErrors() == 0:
        formattedsentences = s.splitText(sentences)
        dict = s.frequency(formattedsentences, language)
        if s.getErrors() == 0:
            rating = s.rating(formattedsentences, dict)
            avg = s.average(rating)
            if sentcount == "" or sentcount == "\n":
                sentcount = 100
                s.summary(formattedsentences, rating, avg, sentcount)
            else:
                s.summary(formattedsentences, rating, avg, sentcount)
        if s.getErrors() == 0:
            duration_float_seconds = log.stop_process(
                log_type=LogType.Success,
                values='Successfully finished task'
            )
            print("Your text has been summarized and is saved in the file 'summary.txt'!")
        else:
            duration_float_seconds = log.stop_process(
                log_type=LogType.Fail,
                values='task failed'
            )
            print("Something went wrong. ErrorMessage: %s" % (s.getErrorMessage()))
    else:
        duration_float_seconds = log.stop_process(
            log_type=LogType.Fail,
            values='task failed'
        )
        print("Something's wrong with your input. ErrorMessage: %s" % (s.getErrorMessage()))
else:
    if s2.getErrors() == 0:
        formattedsentences = s2.splitData(sentences)
        senses, sentenceCount = s2.wsd(formattedsentences)
        clustered, sentencesandsensynts = s2.firstclustering(senses, formattedsentences, sentenceCount)
        somedict = s2.getSimilarSentences(clustered)
        s2.getSummary(somedict,sentencesandsensynts)
        duration_float_seconds = log.stop_process(
            log_type=LogType.Success,
            values='Successfully finished task'
        )
        print("Your text has been summarized and is saved in the file 'summary.txt'!")
    else:
        duration_float_seconds = log.stop_process(
            log_type=LogType.Fail,
            values='task failed'
        )
        print("Something's wrong with your input. ErrorMessage: %s" % (s.getErrorMessage()))
