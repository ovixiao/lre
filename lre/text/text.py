# -*- coding: utf-8 -*-
"""
用于处理、存储、管理文本的对象
"""
from __future__ import unicode_literals

from collections import defaultdict

import six

from .index import Index
from ..nlp import Nlp
from ..result import Result, Results


@six.python_2_unicode_compatible
class Text(object):
    """
    文档对象, 所有文档生成为文档对象后再进行处理.
    为了提高效率会生成两个关键词及其 Term 对象的映射表:
    """

    def __init__(self, config, text):
        """
        :param config: 存储配置信息的对象
        :param text: 原始文本, 包含如下信息：
                         1. 段落使用 \n 分割
                         2. 句子使用标点符号分割
        """
        self.config = config
        self.nlp = Nlp(config)
        self.word_map, self.word_list = self.cut(text)

    def cut(self, text):
        """
        切分文本, 切分成段落-句子-词的结构
        :param text: 待切分的文本
        :return: 返回切分后的段落-句子-词的结构, 存储的格式为：
            paragrapshs = [sentence_1, sentence_2, ...]
            sentence_n = [word_1, word_2, ...]
            word_n = (paragraph_index, sentence_index, word_index, word)
        """
        word_list = []
        word_map = defaultdict(Results)
        if text:
            offset = 0
            for i_para, paragraph in enumerate(self.nlp.text2para(text)):
                for i_sent, sentence in enumerate(self.nlp.para2sent(paragraph)):
                    for i_word, word in enumerate(self.nlp.sent2word(sentence)):
                        index = Index(i_para, i_sent, i_word, offset)
                        offset += 1
                        # 初始状态下 bias = 0
                        word_list.append(word)
                        result = Result(self.config, word_list, index, index, 0)
                        word_map[word].add(result)
        return word_map, word_list

    def empty(self):
        """
        是否是空 Text
        """
        return len(self.word_list) == 0

    def __str__(self):
        if self.empty():
            return 'Text(empty)'
        else:
            return 'Text({0})'.format(' '.join([str(x) for x in self.word_list]))

    def __eq__(self, other):
        return self.word_list == other.word_list

    def __len__(self):
        return len(self.word_list)

    @property
    def beg_index(self):
        """
        文本的起始 index
        """
        if self.empty():
            return Index(9999, 9999, 9999, 0)
        else:
            return self.word_list[0].index

    @property
    def end_index(self):
        """
        文本的结束 index
        """
        if self.empty():
            return Index(-1, -1, -1, 0)
        else:
            return self.word_list[-1].index
