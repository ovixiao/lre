# -*- coding: utf-8 -*-
"""
表示语法处理类型的一个枚举类
"""
from __future__ import unicode_literals

from enum import Enum


class SyntaxType(Enum):
    """
    支持的类型
    """
    comment = 1
    rule = 2
    concept = 3
    keyword = 4
    rule_range = 5
    filter_range = 6
    rule_filter = 7
    concept_filter = 8
