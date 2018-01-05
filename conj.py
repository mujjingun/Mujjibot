#! /usr/bin/env python3

from konlpy.tag import Kkma
import textwrap

kkma = Kkma()

pos_dict = {
  'NNG': 'Noun',
  'NNP': 'Proper Noun',
  'NNB': 'Dependent Noun',
  'NNM': 'Counter',
  'NR': 'Numbers',
  'NP': 'Pronoun',
  
  'VV': 'Action Verb',
  'VA': 'Adjective',
  'VXV': 'Auxiliary Verb',
  'VXA': 'Auxiliary Adjective',
  'VCP': 'Copula',
  'VCN': 'Negative Copula',
  
  'MDT': 'Noun Modifier',
  'MDN': 'Number Noun Modifier',
  'MAG': 'Adverb',
  'MAC': 'Conjunctive Adverb',
  
  'IC': 'Interjection',
  
  'JKS': 'Subject Marker',
  'JKC': 'Complement Marker',
  'JKG': 'Noun Modifier Marker',
  'JKO': 'Object Marker',
  'JKM': 'Adverbial Marker',
  'JKI': 'Vocative Marker',
  'JKQ': 'Quotation Marker',
  'JX': 'Auxiliary Particle',
  'JC': 'Conjuctive Particle',
  
  'EPH': 'Honorific Verb Ending',
  'EPT': 'Tense Verb Ending',
  'EPP': 'Politeness Verb Ending',
  'EFN': 'Declarative Sentence Ending',
  'EFQ': 'Interrogative Sentence Ending',
  'EFO': 'Imperative Sentence Ending',
  'EFA': 'Propositive Sentence Ending',
  'EFI': 'Interjective Sentence Ending',
  'EFR': 'Honorific Sentence Ending',
  'ECE': 'Equivalent Sentence Conjunction',
  'ECD': 'Dependent Sentence Conjunction',
  'ECS': 'Auxiliary Sentence Conjunction',
  'ETN': 'Noun-making Verb Ending',
  'ETD': 'Noun Modifier Verb Ending',
  
  'XPN': 'Nominal Prefix',
  'XPV': 'Verbial Prefix',
  'XSN': 'Noun-Deriving Suffix',
  'XSV': 'Verb-Deriving Suffix',
  'XSA': 'Adjective-Deriving Suffix',
  'XR': 'Root',
  
  'UN': 'Unknown',
  
  'OL': 'Not Korean',
  'OH': 'Hanja',
  'ON': 'Numbers',
}

def conj(c, e, cmd):
  if len(cmd.split()) < 2:
    c.privmsg(e.target, "conj: retrieve conjugation info. Usage: conj <word>")
    return
  S = cmd.split(None, 1)[1]
  l = kkma.pos(S)
  fmt = " + ".join("'{}' ({})".format(a, pos_dict[b]) for a, b in l if not b.startswith('S')) 
  output = '"{}" is: {}'.format(S, fmt)
  
  for i in textwrap.wrap(output, 256):
    c.privmsg(e.target, i)
  
  
  
  
  
  
  
  
  
  