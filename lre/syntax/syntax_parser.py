# -*- coding: utf-8 -*-
"""
支持的语法类型分为如下几类：
1. 注释。内容无意义，仅用于规则编写者观看使用
2. 规则。有明确意义的规则，以 $ 作为首字符
3. 概念。规则和过滤的集合，以 % 作为首字符
4. 过滤。过滤是反向操作的规则集合，以 ! 作为首字符
5. 关键词。作为最基础的词的概念，以 " 包裹作为匹配原理
6. 范围。表示匹配的范围，以 @ 作为首字符
"""
from __future__ import unicode_literals

import re

import six

from .syntax_result import SyntaxMatchResult, SyntaxParseResult
from .syntax_type import SyntaxType
from ..nlp import Nlp


@six.python_2_unicode_compatible
class SyntaxParser(object):
    # 匹配注释的正则
    re_comment = re.compile(r'#([^\n]*)(\n|$)')
    # 匹配规则的正则
    re_rule = re.compile(r'\$(\w+)[\t\r\n ]*\(')
    # 匹配概念的正则
    re_concept = re.compile(r'%([\w-]+)[\n\t ]*[),]')
    # 匹配关键词的正则
    re_keyword = re.compile(r'"(([^"\t\n ]|(?<=\\)")+)(?<!\\)"[\n\t ]*[),]')
    # 匹配规则范围的正则
    re_rule_range = re.compile(r'@([dwspt])(\d*)[\t\n ]*,')
    # 匹配过滤器范围的正则
    re_filter_range = re.compile(r'@\[{sp}({ut}\d*|0){sp},{sp}(\d+){sp},{sp}({ut}\d*|0){sp}\]{sp},'.format(
        ut=r'[dwspt]',  # 单位
        sp=r'[ \t\n\r]*',  # 空格
    ))
    # 匹配规则过滤的正则
    re_rule_filter = re.compile(r'!filt\(')
    # 匹配概念过滤的正则
    re_concept_filter = re.compile(r'!cfilt\(')

    def __init__(self, config):
        self.config = config
        self.nlp = Nlp(config)

    def match_comment(self, text, index):
        """
        依据 text[index] 判断是否是注释，评论语法分析，以 # 开始的当前行部分全为注释
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返匹配对象, 不成功返回 None
        """
        if text[index] == '#':
            m = self.__class__.re_comment.match(text, index)
            if m:
                comment = m.group(0)
                beg_index, end_index = m.span(0)
                return SyntaxMatchResult(SyntaxType.comment, beg_index, end_index, comment=comment)
            else:
                raise ValueError('invalid comment', text[index:])

    def match_rule(self, text, index):
        """
        规则的语法匹配，依据 text[index] 判断是否是规则
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返匹配对象, 不成功返回 None
        """
        if text[index] == '$':
            m = self.__class__.re_rule.match(text, index)
            if m:
                rule_name = m.group(1)
                beg_index, arg_index = m.span(0)
                return SyntaxMatchResult(SyntaxType.rule, beg_index, arg_index, rule_name=rule_name)
            else:
                raise ValueError('invalid rule', text[index:])

    def match_concept(self, text, index):
        """
        概念的语法匹配，依据 text[index] 判断是否是概念，概念使用 % 下划线起始来标定，概念名称只能使用：

            1. 阿拉伯数字
            2. 英文字母（大小写敏感）
            3. 下划线
            4. 横线

        例如:

            * %MacbookPro
            * %macbook_pro
            * %MACBOOK_PRO

        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回匹配对象, 不成功返回 None
        """
        if text[index] == '%':
            m = self.__class__.re_concept.match(text, index)
            if m:
                concept_name = m.group(1)
                beg_index, end_index = m.span(0)
                # 修订 index，不要 ), 带来的 index
                end_index -= 1
                return SyntaxMatchResult(SyntaxType.concept, beg_index, end_index, concept_name=concept_name)
            else:
                raise ValueError('invalid concept', text[index:])

    def match_keyword(self, text, index):
        """
        关键词的语法匹配，依据 text[index] 判断是否是关键词。如若匹配上返回匹配对象。
        关键词使用 " 囊括来标定，对于要表达的双引号，使用 \ 进行转义，例如：

            * "ABC", 表示关键词 ABC
            * "A\"BC", 表示关键词 A"BC

        关键词中不许出现：

            * 空格
            * 制表符，即 \t
            * 换行，即 \n
            * 无转义的双引号，"ab"c" 这种会报错

        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回匹配对象, 不成功返回 None
        """
        if text[index] == '"':  # 双引号
            m = self.__class__.re_keyword.match(text, index)
            if m:
                keyword = m.group(1)
                beg_index, end_index = m.span(0)
                # 修订 index，不要 ), 带来的 index
                end_index -= 1
                # 将用户输入词的粒度和分词器统一
                keyword = list(self.nlp.sent2word(keyword))
                return SyntaxMatchResult(SyntaxType.keyword, beg_index, end_index, keyword=keyword)
            else:  # 以引号开头，但是匹配不上
                raise ValueError('invalid keyword', text[index:])

    def match_rule_range(self, text, index):
        """
        范围限制器使用 @ 来标定, 具体的范围指令包括:

        | *单位* | *注释*       | *示例*                            |
        | ----- | ------------ | -------------------------------- |
        | d     | 不跨句子的范围 | 若参数为1，则@d即可，若n为6则为：@d6  |
        | w     | 跨句子的范围   | 参数若为1，则@w即可，若n为8则为：@w8 |
        | s     | 句子          | 参数若为1，则@s即可，若n为7则为：@s7 |
        | p     | 段落          | 参数若为1，则@p即可，若n为5则为：@p5 |
        | t     | 整文          | 没有参数，表示全文，@t              |

        依据 text[index] 判断是否是范围
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回匹配对象, 不成功返回 None
        """
        if text[index] == '@' and text[index + 1] != '[':
            m = self.__class__.re_rule_range.match(text, index)
            if m:
                unit, n = m.groups()
                n = 1 if n == '' else int(n)
                beg_index, end_index = m.span(0)
                # 校准 index，不要 , 对应的 index
                end_index -= 1
                return SyntaxMatchResult(SyntaxType.rule_range, beg_index, end_index, unit=unit, n=n)
            else:
                raise ValueError('invalid range syntax', text[index:])

    def match_filter_range(self, text, index):
        """
        用于过滤器中的范围标定，其格式为：

            @[前向范围, 重叠标志位, 后向范围]

        其中，前向、后向范围均支持『单位 + 数值』的方案，其类似于 rule range
        如果不作过滤则标记为 0 即可，重叠标志位仅支持 1 / 0，分别表示过滤和不过滤

        | *单位* | *注释*       | *示例*                            |
        | ----- | ------------ | --------------------------------- |
        | d     | 不跨句子的范围 | 若参数为1，则 d 即可，若n为6则为：d6 |
        | w     | 跨句子的范围   | 参数若为1，则 w 即可，若n为8则为：w8 |
        | s     | 句子          | 参数若为1，则 s 即可，若n为7则为：s7 |
        | p     | 段落          | 参数若为1，则 p 即可，若n为5则为：p5 |
        | t     | 整文          | 没有参数，表示全文，t              |

        依据 text[index] 判断是否是范围
        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回匹配对象, 不成功返回 None
        """
        if text.startswith('@[', index):
            m = self.__class__.re_filter_range.match(text, index)
            if m:
                beg_index, end_index = m.span(0)
                # 校准 index，不要 , 带来的 index
                end_index -= 1
                # 前向范围
                forward = m.group(1)
                if forward == '0':  # 如果为 0 表示不作过滤
                    forward_unit = None
                    forward_n = 0
                else:  # 过滤
                    forward_unit = forward[0]
                    if forward[1:]:  # 单位 + 数值
                        forward_n = int(forward[1:])
                    else:  # 纯单位
                        forward_n = 1

                # 重叠标志位
                is_overlap = bool(int(m.group(2)))

                # 后向范围
                backward = m.group(3)
                if backward == '0':  # 如果为 0 表示不作过滤
                    backward_unit = None
                    backward_n = 0
                else:  # 过滤
                    backward_unit = backward[0]
                    if backward[1:]:  # 单位 + 数值
                        backward_n = int(backward[1:])
                    else:  # 纯单位
                        backward_n = 1

                return SyntaxMatchResult(
                    SyntaxType.filter_range,
                    beg_index,
                    end_index,
                    forward_unit=forward_unit,
                    forward_n=forward_n,
                    is_overlap=is_overlap,
                    backward_unit=backward_unit,
                    backward_n=backward_n
                )
            else:
                raise ValueError('invalid filter_range_arg', text[index:])

    def match_rule_filter(self, text, index):
        """
        规则过滤器的语法规则为:

            !filt(目标规则, 限制范围 1, 限制规则 1, ...)

        其中,
            * 目标规则是指要被过滤的规则
            * 限制范围: 表示对目标规则进行限制的限制范围, 其修饰的是紧邻其后的限制规则
            * 限制规则: 表示对目标规则进行限制的规则, 其一定要配合限制范围一起操作

        限制范围/限制规则是成对出现, 当只有其中一个时为 "非法语法", 会报错处理.
        限制范围/限制规则可以多个出现, 表示对目标规则的限制 (串行). 例如:

            !filt($seq(@d4, "turn", "on"),
                  @[d3, 0, 0], $or("not", "can't", "won't", "wouldn't")
            )

        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回匹配对象, 不成功返回 None
        """
        if text.startswith('!f', index):
            m = self.__class__.re_rule_filter.match(text, index)
            if m:
                beg_index, arg_index = m.span(0)
                return SyntaxMatchResult(SyntaxType.rule_filter, beg_index, arg_index)
            else:
                raise ValueError('invalid rule_filter', text[index:])

    def match_concept_filter(self, text, index):
        """
        概念过滤器的语法规则为:

            !cfilt(限制范围, 限制规则)

        其中,
            * 限制范围：表示对目标规则进行限制的限制范围，其修饰的是紧邻其后的限制规则
            * 限制规则：表示对目标规则进行限制的规则，其一定要配合限制范围一起操作

        限制范围、限制规则是成对出现，当只有其中一个时为『非法语法』会报错处理。例如：

            !cfilt(
                @[d3, 0, 0],
                $or("not", "can't", "won't", "wouldn't")
            )

        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 匹配成功返回匹配对象, 不成功返回 None
        """
        if text.startswith('!c', index):
            m = self.__class__.re_concept_filter.match(text, index)
            if m:
                beg_index, arg_index = m.span(0)
                return SyntaxMatchResult(SyntaxType.concept_filter, beg_index, arg_index)
            else:
                raise ValueError('invalid concept_filter', text[index:])

    @staticmethod
    def ignore_space(text, index):
        """
        忽略 "空" 字符, 空字符为:

            * 空格
            * 制表符
            * 换行符

        :param text: 全文本
        :param index: 待判断的字符的索引号
        :return: 返回不是 "空" 字符的索引
        """
        while index < len(text):
            if text[index] in '\t\n\r ':
                index += 1
                continue
            break
        return index

    def parse_args(self, text, index=0):
        """
        语法分析的参数解析
        :param text: 待分析的规则文本
        :param index: 开始分析的规则文本的下标
        :return: 返回分析出的结果对象和下一次分析的索引位置
        """
        match_func_list = (
            self.match_keyword,
            self.match_rule,
            self.match_rule_range,
            self.match_rule_filter,
            self.match_concept,
            self.match_concept_filter,
            self.match_filter_range,
            self.match_comment,
        )
        args = []
        while index < len(text):
            index = self.ignore_space(text, index)
            if text[index] == ')':  # 当前规则、过滤结束
                return args, index + 1
            elif text[index] == ',':  # 还未结束，还有后续参数
                index += 1
                continue

            for match_func in match_func_list:
                result = match_func(text, index)
                if result:  # 有匹配到结果
                    # 注释，直接忽略即可
                    if result.syntax_type == SyntaxType.comment:
                        index = result.end_index
                    elif result.syntax_type in (
                            SyntaxType.keyword,
                            SyntaxType.concept,
                            SyntaxType.rule_range,
                            SyntaxType.filter_range,
                    ):
                        args.append(result)
                        index = result.end_index
                    elif result.syntax_type in (
                            SyntaxType.rule,
                            SyntaxType.rule_filter,
                            SyntaxType.concept_filter,
                    ):
                        arg_index = result.end_index
                        curr_args, curr_end_index = self.parse_args(text, arg_index)
                        result.update(curr_args, curr_end_index)
                        args.append(result)
                        index = curr_end_index
                    else:
                        raise ValueError('invalid argument', text[index:])
                    break  # 命中则退出，语法之间互斥，不会一条语法对应多个匹配
            else:
                raise ValueError('unknown argument', text[index:])
        else:
            raise ValueError('incomplete argument', text[index:])

    def parse(self, text):
        """
        语法分析的入口位置
        :param text: 待分析的文本
        :return: 返回规则、过滤的列表以及概念过滤的列表
        """
        index = 0
        rules_filters = []
        text = text.strip()
        while index < len(text):
            index = self.ignore_space(text, index)

            # 注释
            result = self.match_comment(text, index)
            if result:
                index += result.end_index
                continue

            # 规则或过滤
            result = self.match_rule(text, index)
            if result:
                index = result.end_index
                args, index = self.parse_args(text, index)
                result.update(args, index)
                rules_filters.append(result)
                continue

            # 概念过滤
            result = self.match_concept_filter(text, index)
            if result:
                index = result.end_index
                args, index = self.parse_args(text, index)
                result.update(args, index)
                rules_filters.append(result)
                continue

            raise ValueError('invalid rule', text[index:])

        return SyntaxParseResult(rules_filters)
