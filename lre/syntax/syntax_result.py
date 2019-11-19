# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

import six


@six.python_2_unicode_compatible
class SyntaxMatchResult(object):
    """
    用来存储语法分析后的结果的部分
    """

    def __init__(self, syntax_type, beg_index, end_index, **kwargs):
        """
        存储被 SyntaxParser 命中的结果
        :param syntax_type: 当前结果所属的类型
        :param beg_index: 命中部分的起始索引
        :param end_index: 命中部分的结束索引
        :param kwargs: 用于存储 syntax_type 相关的一些参数
        """
        self.syntax_type = syntax_type
        self.beg_index = beg_index
        self.end_index = end_index
        self.__dict__.update(kwargs)

    def __str__(self):
        kwargs = copy.copy(self.__dict__)
        del kwargs['syntax_type']
        del kwargs['beg_index']
        del kwargs['end_index']
        return '{syntax_type}(beg_index={beg_index}, end_index={end_index}, {kwargs})'.format(
            syntax_type=self.syntax_type,
            beg_index=self.beg_index,
            end_index=self.end_index,
            kwargs=', '.join(['{}={}'.format(*x) for x in kwargs.items()]),
        )

    def __repr__(self):
        return self.__str__()

    def update(self, args, end_index):
        """
        更新当前查找到的结果，为结果添加上对应的参数列表和新的结束索引号
        :param args: 被添加的参数列表
        :param end_index: 新的结束索引号
        """
        self.args = args
        self.end_index = end_index


class SyntaxParseResult(object):
    """
    用于存储解析结果的对象
    """

    def __init__(self, rules_filters):
        """
        :param rules_filters: 规则或过滤队列
        """
        self.rules_filters = rules_filters

    def __str__(self):
        return 'SyntaxParseResult(rules_filter={0})'.format(
            self.rules_filters,
        )
