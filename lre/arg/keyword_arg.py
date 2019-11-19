# -*- coding: utf-8 -*-
"""
关键词参数, 该参数的性能将会直接影响整个代码的运行效率
"""
from __future__ import unicode_literals

import six

from ..result import Results
from ..rule import SeqRule
from .rule_range_arg import s_range_arg


class SingleKeywordArg(object):
    """
    关键词参数, 仅能匹配一个单词。用作内部使用
    """

    def __init__(self, word):
        """
        初始化 SingleKeywordArg 对象
        :param word: 待匹配的关键词
        """
        self.word = word

    def match(self, text):
        """
        匹配对象进行文本的关键词匹配.
        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象, 如果不存在返回空的 Results
        """
        results = text.word_map.get(self.word)

        if results is None:  # 没有结果返回空
            return Results()
        else:
            return results


@six.python_2_unicode_compatible
class KeywordArg(object):
    """
    关键词参数, 匹配一个单词. 单词会通过分词操作.
    """

    def __init__(self, config, words):
        """
        初始化 KeywordArg 对象
        :param config: 存储配置信息的对象
        :param words: 待匹配的关键词列表, 其粒度由外部代码来把控
        """
        if len(words) == 0:
            raise ValueError('KeywordArg needs ONE word at least', words)

        # 存储 SingleKeywordArg 对象
        self.words = []
        for word in words:
            self.words.append(SingleKeywordArg(word))
        self.config = config

    def __str__(self):
        return 'KeywordArg(words=[{0}])'.format(
            ', '.join([x.word for x in self.words]),
        )

    def match(self, text):
        """
        匹配对象进行文本的关键词匹配.
        :param text: 待匹配的 Text 对象
        :return: 返回查找到的 Results 对象, 如果不存在返回空的 Results
        """
        if len(self.words) == 1:
            return self.words[0].match(text)
        else:  # self.words > 1 的情况
            seq_rule = SeqRule(self.config, s_range_arg, *self.words)
            return seq_rule.match(text)
