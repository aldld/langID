#!/usr/bin/env python
# coding=utf-8

import string
import codecs

# Total number of texts learned from in all languages
totalTextCount = 0

class Language:
    def __init__(self, code, name, fileName, textCount):
        self.code = code
        self.name = name
        self.fileName = fileName
        self.textCount = int(textCount)

        self.wordCount = 0
        self.uniqueWordCount = 0

        # Language bag of words vocab['word'] = number of occurences of word
        self.vocab = {}
    
    def write(self):
        """ Save vocabulary to the language file and update lang_list.txt. """
        vocabFile = codecs.open('languages/' + self.fileName, 'w', encoding='utf-8')
        vocabFile.write('\n'.join([word + ' ' + str(self.vocab[word]) for word in self.vocab.iterkeys()]))
        vocabFile.close()
    
    def vocabUpdate(self, document):
        """ Updates the language's vocabulary to reflect a given document """
        for word in document.words.iterkeys():
            if word in self.vocab:
                self.vocab[word] += document.words[word]
            else:
                self.vocab[word] = document.words[word]

class Document:
    def __init__(self):
        self.words = {}
        self.wordCount = 0

def loadLanguages(languages):
    """ Loads language vocabularies from files into languages dictionary """
    global totalTextCount

    langListFile = open('languages/lang_list.txt', 'r')

    # Load language medata
    for line in langListFile:
        data = line.strip().split(' ')
        if len(data) != 4: continue
        
        language = Language(data[0], data[1], data[2], data[3])
        totalTextCount += language.textCount

        # Load language vocabulary
        vocabFile = codecs.open('languages/' + language.fileName, 'r', encoding='utf-8')
        for line in vocabFile:
            data = line.strip().split(' ')
            if len(data) != 2: continue

            language.vocab[data[0]] = int(data[1])

            language.wordCount += language.vocab[data[0]]
            language.uniqueWordCount += 1
        vocabFile.close()

        languages[language.code] = language
    
    langListFile.close()

def updateLangList(languages):
    """ Updates lang_list.txt """
    text = '' # Text to be written to lang_list.txt
    for lang in languages.itervalues():
        text += ' '.join([lang.code, lang.name, lang.fileName, str(lang.textCount)]) + '\n'
    langListFile = open('languages/lang_list.txt', 'w')
    langListFile.write(text)
    langListFile.close()

def processText(text):
    """ Strip punctuation from text, convert all words to lowercase,
        split words (separated by spaces) into a sorted list.
        Return values into wordList. """
    translateTable = dict((ord(char), None) for char in string.punctuation)
    wordList =  unicode(text).strip() \
        .translate(translateTable) \
        .translate({ord('\n'): ord(' ')}) \
        .lower() \
        .split(' ')

    # Remove words consisting only of whitespace
    for word in reversed(wordList):
        if not word.strip():
            wordList.remove(word)
    # Remove words containing numerals
    for word in reversed(wordList):
        for digit in string.digits:
            if digit in word:
                wordList.remove(word)
                break

    # Sort now to improve efficiency when writing the list later.
    return sorted(wordList)

