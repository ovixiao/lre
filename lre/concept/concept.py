# -*- coding: utf-8 -*-
"""
概念对象
"""
from __future__ import unicode_literals

from ..arg import *
from ..filter import *
from ..result import Results
from ..rule import *
from ..syntax import SyntaxType


class Concept(object):
    """
    概念对象是规则的集合, 可以一定程度标定客观物理世界的一些通用规范. 例如, 我们规则中会大量使用到 "手机" 这个概念,
    我们可以建立一个 "Phone" 的概念, 对应给它赋予一些规则来表征.

        concept_name = Phone
        rules = [
            $kw("mobilephone"),
            $kw("phone"),
            $seq("mobile", "phone"),
            $ord(@d5, "my", "phone"),
            ...
        ]
    """

    def __init__(self, config, name, concept_mgr, syntax_parse_result):
        """
        初始化一个 Concept 对象
        :param config: 包含配置信息的对象
        :param name: 概念名称
        :param concept_mgr: 用于存储概念的 manager
        :param syntax_parse_result: 通过语法解析后的结果, 保存了规则/过滤/概念过滤
        """
        self.config = config
        self.name = name
        self.concept_mgr = concept_mgr
        if len(syntax_parse_result.rules_filters) == 0:
            raise ValueError('concept has one rule or filter at least', syntax_parse_result)
        self.syntax_parse_result = syntax_parse_result
        self.rules_filters = self.build()

    def match(self, text):
        """
        匹配操作, 该概念能匹配到什么结果
        :param text: 待匹配的文本 Text 对象
        :return: 返回匹配到的结果, 会使用 global_rules 进行过滤
        """
        results = Results()
        for rule_or_filter in self.rules_filters:
            results.add(rule_or_filter.match(text))

        # 修改每个 Result 的 bias
        if self.config.force_concept_size_one:
            for result in results:
                # 相同的段落/句子, 则 bias 设置为end_index.i_word - beg_index.i_word - 1
                if result.beg_index.i_para == result.end_index.i_para \
                        and result.beg_index.i_sent == result.end_index.i_sent:
                    result.bias = result.end_index.i_word - result.beg_index.i_word
                else:  # 不在一个段落/句子中, 则直接设置为总长度 - 1, 保证其长度直接为 1
                    result.bias = result.end_index.i_word - 1

        return results

    def build(self):
        """
        通过提供的 syntax_parse_result 生成对应的 rule/filter/concept 对象队列, 属于某个 concept
        """

        # 用于映射的规则名称 -> 对象
        rule_map = {
            'arg': ArgRule,
            'bag': BagRule,
            'or': OrRule,
            'ord': OrdRule,
            'seq': SeqRule,
        }

        def build_one(match_result):
            """
            使用 match_result 生成一个 rule/filter/concept 对象
            :param match_result: 一个匹配后的结果
            :return: 返回生成的对象
            """
            if match_result.syntax_type == SyntaxType.keyword:
                keyword_arg = KeywordArg(self.config, match_result.keyword)
                return keyword_arg
            elif match_result.syntax_type == SyntaxType.rule:
                rule_cls = rule_map[match_result.rule_name]
                # 生成 args 对象
                args = []
                for arg in match_result.args:
                    args.append(build_one(arg))
                rule = rule_cls(self.config, *args)
                return rule
            elif match_result.syntax_type == SyntaxType.concept:
                concept_arg = ConceptArg(
                    self.config,
                    match_result.concept_name,
                    self.concept_mgr,
                )
                return concept_arg
            elif match_result.syntax_type == SyntaxType.rule_range:
                rule_range_arg = RuleRangeArg(
                    self.config,
                    match_result.unit,
                    match_result.n,
                )
                return rule_range_arg
            elif match_result.syntax_type == SyntaxType.filter_range:
                filter_range_arg = FilterRangeArg(
                    self.config,
                    match_result.forward_unit,
                    match_result.forward_n,
                    match_result.is_overlap,
                    match_result.backward_unit,
                    match_result.backward_n,
                )
                return filter_range_arg
            elif match_result.syntax_type == SyntaxType.rule_filter:
                # 生成 args 对象
                args = []
                for arg in match_result.args:
                    args.append(build_one(arg))
                rule_filter = RuleFilter(self.config, *args)
                return rule_filter
            elif match_result.syntax_type == SyntaxType.concept_filter:
                # 生成 args 对象
                args = []
                for arg in match_result.args:
                    args.append(build_one(arg))
                concept_filter = ConceptFilter(self.config, *args)
                return concept_filter
            else:
                raise ValueError('invalid syntax_type')

        rules_filters = []
        for match_result in self.syntax_parse_result.rules_filters:
            rule_filter = build_one(match_result)
            rules_filters.append(rule_filter)
        return rules_filters
