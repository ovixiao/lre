# -*- coding: utf-8 -*-
"""
处理中文的库。提供分句子，分词等功能。
"""
from __future__ import unicode_literals

import re

import jieba.posseg as pseg
import six


@six.python_2_unicode_compatible
class NlpZh(object):
    __re_sent = re.compile('[!。！…?？]')

    def __init__(self, config):
        self.config = config

    def text2para(self, text):
        """
        从文本切分成为段落
        :param text: 输入的文本整体，段落以 \n 作为分割
        :return: 返回段落的列表
        """
        return text.split('\n')

    def para2sent(self, paragraph):
        """
        从段落切分句子
        :param paragraph: 输入的段落文本，段落以 \n 作为分割，仅支持一个 \n
        :return: 返回句子的列表
        """
        # 不需要标点符号
        sentences = self.__class__.__re_sent.split(paragraph)
        return sentences

    def sent2word(self, sentence):
        """
        从句子切分成词
        :param sentence: 输入的句子文本
        :return: 返回词的列表
        """
        words = pseg.cut(sentence)
        # 注意！非英语的拉丁语会出现部分切分成为标点（x），部分会变成英文（eng）
        for word, pos in words:
            if pos == 'x':  # 标点不要（包含全半角空格）
                continue
            elif pos == 'eng':  # 英文
                yield word.lower()
            else:  # 中文
                if self.config.word_level == 'char':
                    for ch in word:
                        ch = ch
                        yield ch
                elif self.config.word_level == 'word':
                    yield word
                else:  # 非法 config
                    raise ValueError('invalid_config_word_level', self.config.word_level)
