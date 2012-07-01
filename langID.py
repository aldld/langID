#!/usr/bin/env python
# coding=utf-8
# Machine Learning language identification (document classification) program
# Implements a bag of words model with Naive Bayes Classifier
# Designed for use with languages which use the Latin alphabet.

import sys
import codecs
import math

import langlib

SMOOTHING_PARAM = 1 # Smoothing parameter for Laplace smoothing

 # Dictionary of language objects
languages = {}
langlib.loadLanguages(languages)

def train():
    """ Training mode. Assumes all training exercises have never been seen before. """
    
    for lang in languages.iterkeys():
        # Read in documents so that UTF-8 encoding is handled properly
        f = codecs.open('trainingTexts/' + languages[lang].fileName, encoding='utf-8')
        texts = f.read().split('====') # Individual documents are separated by ====
        f.close()
        
        for text in texts:
            processed = langlib.processText(text)
            
            # Convert processed into a Document representing a bag of words
            document = langlib.Document()
            previousWord = ''
            for word in processed:
                if word == previousWord:
                    document.words[word] += 1
                else:
                    document.words[word] = 1
                previousWord = word
            
            # Update the language's vocabulary and write to disk
            languages[lang].vocabUpdate(document)
            languages[lang].write()
            
            languages[lang].textCount += 1
            langlib.totalTextCount += 1
        
    # Update the language list file
    langlib.updateLangList(languages)

def classify(fileName):
    """ Classify mode. Identifies the language of the text specified in fileName """
    f = codecs.open(fileName, 'r', encoding='utf-8')
    text = f.read()
    f.close()
    
    processed = langlib.processText(text)
    
    # Convert processed into a Document represnting a bag of words
    document = langlib.Document()
    previousWord = ''
    for word in processed:
        if word == previousWord:
            document.words[word] += 1
        else:
            document.words[word] = 1
        previousWord = word
    
    # Calculate the posterior probability of each language given the input
    langProbs = {}
    
    # Sum over all languages P(l) * Product over all words in document of P(word|l)
    # Using Laplace smoothing
    # IT IS PROBABLY POSSIBLE TO REMOVE EVIDENCE since it is simply a constant which
    # all probabilities are divided by
    """
    evidence = 0
    for l in languages.iterkeys():
        langProb = languages[l].textCount / float(langlib.totalTextCount)
        product = 1
        for word in document.words:
            if word in languages[l].vocab:
                product *= float(languages[l].vocab[word] + SMOOTHING_PARAM)
                product /= float(languages[l].wordCount + SMOOTHING_PARAM * languages[l].uniqueWordCount)
            else:
                product *= float(SMOOTHING_PARAM)
                product /= float(languages[l].wordCount + SMOOTHING_PARAM * languages[l].uniqueWordCount)
        evidence += langProb * product
    """
        
    for lang in languages.iterkeys():
        prior = languages[lang].textCount / float(langlib.totalTextCount)
        priorExponent = math.floor(math.log(prior, 10))
        priorSignificand = prior / (10 ** priorExponent)
        prior = [priorSignificand, priorExponent] # Scientific notation [significand, exponent]
        
        # Product over all words in document of P(word|lang) using Laplace smoothing
        likelihood = [1, 0] # Scientific notation [significand, exponent]
        denominator = float(languages[lang].wordCount + SMOOTHING_PARAM * languages[lang].uniqueWordCount)
        denomExponent = math.floor(math.log(denominator, 10))
        denomSignificand = denominator / (10 ** denomExponent)
        for word in document.words:
            if word in languages[lang].vocab:
                probability = float(languages[lang].vocab[word] + SMOOTHING_PARAM)
                
                #probExponent = math.floor(math.log(probability, 10))
                #probSignificand = probability / (10 ** probExponent)
            else:
                probability = float(SMOOTHING_PARAM)
                
            probExponent = math.floor(math.log(probability, 10))
            probSignificand = probability / (10 ** probExponent)
            
            # Divide the probability by the denominator which applies to all words in a given language
            probSignificand /= denomSignificand
            probExponent -= denomExponent
            
            # Because numbers get very tiny, work in scientific notation
            # significand * (10 ** exponent)
            #probExponent = math.floor(math.log(probability, 10))
            #probSignificand = probability / (10 ** probExponent)
            #print probSignificand, probExponent
            likelihood[0] *= probSignificand
            likelihood[1] += probExponent
        
        langProbs[lang] = [prior[0] * likelihood[0], prior[1] + likelihood[1]] # Scientific notation
        #langProbs[lang] = prior * likelihood / evidence # May not be necessary to use evidence
        
        # Normalize so that significand < 10
        normalizerExponent = math.floor(math.log(langProbs[lang][0], 10))
        langProbs[lang][0] /= 10 ** normalizerExponent
        langProbs[lang][1] += normalizerExponent
   
    for lang in langProbs:
        print lang, langProbs[lang]

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == '-t': # Training mode
            train()
        else: # Classify mode
            classify(sys.argv[1])
    else:
        print 'Use option -t for training mode.'
    
if __name__ == '__main__':
    main()

