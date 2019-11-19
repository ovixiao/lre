# -*- coding: utf-8 -*-
"""
作为配置信息的存储、传递和获取
"""
from __future__ import unicode_literals

import six


@six.python_2_unicode_compatible
class Config(object):
    """
    配置参数
    """

    def __init__(self, **kwargs):
        # 默认 char，字符级别
        self.word_level = kwargs.get('word_level', 'char')
        # 文本的最大长度，默认值为 5000，不建议太大，影响性能且没意义
        self.max_text_len = kwargs.get('max_text_len', 5000)
        # 语言，默认为中文，暂时也只有中文
        self.language = kwargs.get('language', 'zh')
        # 强制 concept 命中后的结果长度设置为 1, 默认为 True
        self.force_concept_size_one = kwargs.get('force_concept_size_one', True)
