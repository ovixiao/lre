# -*- coding: utf-8 -*-
"""
处理各种语言的库，主要是实现分段落、句子、词的功能
"""
from __future__ import unicode_literals

from .nlp_zh import NlpZh


class Nlp(object):

    def __init__(self, config):
        self.config = config
        if self.config.language == 'zh':
            self.nlp = NlpZh(config)
        else:
            raise ValueError('invalid_language', config.language)

    def text2para(self, text):
        """
        从文本切分成为段落, 会依据 config 的 language 来切分
        :param text: 输入的文本整体，段落以 \n 作为分割
        :return: 返回段落的列表
        """
        return self.nlp.text2para(text[:self.config.max_text_len])

    def para2sent(self, paragraph):
        """
        从段落切分句子，会依据 config 的 language 来切分
        :param paragraph: 输入的段落文本，段落以 \n 作为分割，仅支持一个 \n
        :return: 返回句子的列表
        """
        return self.nlp.para2sent(paragraph)

    def sent2word(self, sentence):
        """
        从句子切分成词，会依据 config 的 language 来切分
        :param sentence: 输入的句子文本
        :return: 返回词的列表
        """
        return self.nlp.sent2word(sentence)
