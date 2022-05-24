# text-summarizer
This text summariser will summarise an input text (raw text or file) and save it into a new file. 

# Methods
This summarizer uses two different approaches to summarize a text; ranking and wordnet.

## Ranking method 
With the ranking approach the text is being split into it's sentences and then each sentence is rated based on the frequency of its words.
Then with the help of a threshold all sentences which were best-rated are being put into the summary.

## Wordnet method
When using the wordnet method not the frequency of words in a senctence are being ranked but the semantics behind the sentences. 
Wordnet is a lexical database in which nouns, verbs, adjectives and adverbs are divided into groups of cognitive synonyms called synsets. Synsets are linked by conceptual semantic and lexical relationships. All this together results in a network of semantically related words and concepts. These synsets are needed to get a score based on the meaning of a word in a sentence, to create a summary based on the best rated sentences.

# Usage
Run the CLI script as follows:
```python
$ python3 src/CLI.py
```
Then follow the instructions for the ranking method:
```python
Do You want to use Wordnet or Ranking? (w/r) r
Please enter a txt-file, an url or a text to summarize: xyz.txt
How many sentences do you want to summarize? 7 
Language: english
```
or for the wordnet method:
```python
Do You want to use Wordnet or Ranking? (w/r)w
Please enter a txt-file, an url or a text to summarize: xyz.txt
```

you then get a success message:
```python
SUCCESS | summarizing | ✔ Successfully finished task ~3s       ◴ 11:28:34
Your text has been summarized and is saved in the file 'summary.txt'!
```
or an error message:
```python
FAIL | summarizing | ✘ task failed ~           ◴ 11:37:48
Something went wrong. ErrorMessage: Wrong language selection!
```