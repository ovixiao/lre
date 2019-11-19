# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import unittest

import six

from lre import Config, Model, Text

if six.PY2:
    from codecs import open

config = Config(force_concept_size_one=False)
config_concept_size_one = Config(force_concept_size_one=True)


class TestCase(unittest.TestCase):
    """
    测试 case
    """

    def test_load_text(self):
        """
        测试读取文本
        """
        text_file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'test_data/text.txt'
        )
        with open(text_file_path, encoding='utf-8') as f:
            for line in f:
                text = Text(config, line)
                self.assertIsInstance(text, Text)

    def test_rules(self):
        """
        测试规则, concept 长度不强制为 1
        """
        rule_dir_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'test_data/rules'
        )
        model = Model.train(config, rule_dir_path)

        text_file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'test_data/text.txt'
        )
        with open(text_file_path, encoding='utf-8') as f:
            text = Text(config, f.read())
            self.assertIsInstance(text, Text)
            results_iter = model.match(text)
            for concept_name, results in results_iter.items():
                if concept_name == '安装好':
                    self.assertEqual(len(results), 2)
                elif concept_name == '好':
                    self.assertEqual(len(results), 2)
                else:
                    raise ValueError('invalid concept name', concept_name, results)

    def test_concept_size_one(self):
        """
        测试规则, concept 长度强制为 1
        """
        rule_dir_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'test_data/rules'
        )
        model = Model.train(config_concept_size_one, rule_dir_path)

        text_file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'test_data/text.txt'
        )
        with open(text_file_path, encoding='utf-8') as f:
            text = Text(config_concept_size_one, f.read())
            self.assertIsInstance(text, Text)
            results_iter = model.match(text)
            for concept_name, results in results_iter.items():
                if concept_name == '安装好':
                    self.assertEqual(len(results), 2)
                elif concept_name == '好':
                    self.assertEqual(len(results), 2)
                elif concept_name == '快递好':
                    self.assertEqual(len(results), 1)
                else:
                    raise ValueError('invalid concept name')


if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestCase('test_load_text'))
    test_suite.addTest(TestCase('test_rules'))
    test_suite.addTest(TestCase('test_concept_size_one'))

    unittest.TextTestRunner(verbosity=2).run(test_suite)
