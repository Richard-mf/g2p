# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : g2px.py
# Time       ：4/7/24 3:11 PM
# Author     ：min.fang
# version    ：
# Description：
"""
import re
from builtins import str as unicode
import unicodedata
from nltk.tokenize import TweetTokenizer
from nltk import pos_tag
word_tokenize = TweetTokenizer().tokenize
from .g2p import G2p
from .expand import normalize_numbers


class G2px(G2p):
  def __init__(self, has_bios=False):
    super().__init__()
    self.has_bios = has_bios

  def __call__(self, text):
    # preprocessing
    text = unicode(text)
    text = normalize_numbers(text)
    text = ''.join(char for char in unicodedata.normalize('NFD', text)
                   if unicodedata.category(char) != 'Mn')  # Strip accents
    text = text.lower()
    text = re.sub("[^ a-z'.,?!\-]", "", text)
    text = text.replace("i.e.", "that is")
    text = text.replace("e.g.", "for example")

    # tokenization
    words = word_tokenize(text)
    tokens = pos_tag(words)  # tuples of (word, tag)

    # steps
    prons = []
    for word, pos in tokens:
      if re.search("[a-z]", word) is None:
        pron = [word]

      elif word in self.homograph2features:  # Check homograph
        pron1, pron2, pos1 = self.homograph2features[word]
        if pos.startswith(pos1):
          pron = pron1
        else:
          pron = pron2
      elif word in self.cmu:  # lookup CMU dict
        pron = self.cmu[word][0]
      else:  # predict for oov
        pron = self.predict(word)

      if self.has_bios:
        if len(pron) == 1:
          if not pron[0].startswith('S_'): # 修正cmudict 出现"S_"现象
            pron[0] = "S_"+pron[0] \
              if pron[0] not in [',', '.', '!', '?'] else pron[0]
        else:
          pron = [f'B_{x}' if i == 0 else f'I_{x}'
                  for i, x in enumerate(pron)]

      prons.extend(pron)
      prons.extend([" "])

    return prons[:-1]
