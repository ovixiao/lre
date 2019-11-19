# -*- coding: utf-8 -*-
"""
提供一个示例
"""
from __future__ import unicode_literals

import six

from lre import Config, Model

if six.PY2:
    from codecs import open


def make_config():
    """
    需要增加一个配置信息的对象, 现在支持的字段就这4个:
        1. max_text_length: 在不同的机器上输入文本的最长截断长度不定, 默认值是 5000 个字符 (unicode)
        2. word_level: 是否使用字级别的分词, 默认为 char
        4. language: 语言, 默认为简体中文 zh, 暂时只支持中文
        5. force_concept_size_one: 是否强制将 concept 的长度设置为 1, 默认为 True
    """
    config = Config(
        max_text_length=5000,
        word_level='char',
        language='zh',
        force_concept_size_one=True,
    )
    return config


def train(config, rule_dir_path):
    """
    训练模型
    :param config: config 对象
    :param rule_dir_path: 规则文件的路径
    :return: 返回训练好的模型
    """
    model = Model.train(config, rule_dir_path)
    return model


def match(model, text_path):
    """
    模型匹配
    :param model: 模型对象
    :param text_path: 文本路径
    """
    with open(text_path, encoding='utf-8') as f:
        text = f.read()

    results_iter = model.match(text)
    for concept_name, results in results_iter.items():
        six.print_('Concept Name:', concept_name)
        for result in results:
            six.print_('> ', result)
        six.print_('------------------------------')


if __name__ == '__main__':
    rule_dir_path = 'test_data/rules'
    text_path = 'test_data/text.txt'
    config = make_config()
    model = train(config, rule_dir_path)
    match(model, text_path)
