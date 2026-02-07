"""阶段1校验逻辑：HTML基础结构、语义化标签、文本与媒体标签"""
from lxml import etree
import re

class Stage1Validator:
    @staticmethod
    def validate(level_id, html_code, css_code):
        """阶段1统一校验入口"""
        if level_id == '1-1':
            return Stage1Validator.validate_1_1(html_code)
        elif level_id == '1-2':
            return Stage1Validator.validate_1_2(html_code)
        elif level_id == '1-3':
            return Stage1Validator.validate_1_3(html_code)
        elif level_id == '1-4':  # 新增：匹配JSON中的1-4选择题
            return Stage1Validator.validate_1_4(html_code, css_code)
        else:
            return {
                'is_passed': False,
                'msg': '阶段1关卡ID错误',
                'error_type': '系统错误',
                'score': 0
            }

    @staticmethod
    def validate_1_1(html_code):
        """关卡1-1：HTML基础结构校验（匹配JSON task：补全核心标签+闭合）"""
        # 1. 检查HTML5文档声明（JSON hint要求）
        if '<!DOCTYPE html>' not in html_code:
            return {
                'is_passed': False,
                'msg': '缺少HTML5文档声明<!DOCTYPE html>，必须放在页面最顶部',
                'error_type': '文档声明缺失',
                'score': 0
            }

        # 2. 检查核心标签（html/head/body）存在且闭合（JSON task核心要求）
        required_tags = [('html', '</html'), ('head', '</head'), ('body', '</body>')]
        for open_tag, close_tag in required_tags:
            # 检查标签存在（兼容带属性的情况，如<html lang="en">）
            open_pattern = re.compile(f'<{open_tag}\\b', re.IGNORECASE)
            if not open_pattern.search(html_code):
                return {
                    'is_passed': False,
                    'msg': f'缺少核心标签<{open_tag}>，请添加并闭合',
                    'error_type': f'{open_tag}标签缺失',
                    'score': 0
                }
            # 检查标签闭合
            if not re.search(close_tag, html_code, re.IGNORECASE):
                return {
                    'is_passed': False,
                    'msg': f'<{open_tag}>标签未闭合，请添加{close_tag}',
                    'error_type': f'{open_tag}标签未闭合',
                    'score': 0
                }

        # 3. 检查标签嵌套关系（head/body必须在html内，JSON hint要求）
        try:
            parser = etree.HTMLParser(recover=True)
            tree = etree.HTML(html_code, parser=parser)
            html_elem = tree.xpath('//html')[0]
            if not tree.xpath('//html/head'):
                return {
                    'is_passed': False,
                    'msg': '<head>标签必须嵌套在<html>标签内部',
                    'error_type': '标签嵌套错误',
                    'score': 0
                }
            if not tree.xpath('//html/body'):
                return {
                    'is_passed': False,
                    'msg': '<body>标签必须嵌套在<html>标签内部',
                    'error_type': '标签嵌套错误',
                    'score': 0
                }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'HTML结构异常：{str(e)[:50]}',
                'error_type': '结构异常',
                'score': 0
            }

        # 所有校验通过
        return {
            'is_passed': True,
            'msg': 'HTML基础结构完全正确！核心标签齐全且闭合，嵌套关系合规～',
            'error_type': None,
            'score': 100
        }

    @staticmethod
    def validate_1_2(html_code):
        """关卡1-2：HTML语义化标签校验（匹配JSON task：替换div为语义标签+删除冗余class）"""
        # 1. 检查是否包含所有必要的语义化标签（header/nav/main/footer，JSON task要求）
        required_semantic_tags = ['header', 'nav', 'main', 'footer']
        missing_tags = []
        for tag in required_semantic_tags:
            tag_pattern = re.compile(f'<{tag}\\b', re.IGNORECASE)
            if not tag_pattern.search(html_code):
                missing_tags.append(tag)
        if missing_tags:
            return {
                'is_passed': False,
                'msg': f'缺少语义化标签：{", ".join(missing_tags)}，请替换对应的<div>标签',
                'error_type': '语义化标签缺失',
                'score': 0
            }

        # 2. 检查是否保留冗余div（class为header/nav/main/footer，JSON task要求删除）
        redundant_div_patterns = [
            r'div\s+class=["\']header["\']',
            r'div\s+class=["\']nav["\']',
            r'div\s+class=["\']main["\']',
            r'div\s+class=["\']footer["\']'
        ]
        for pattern in redundant_div_patterns:
            if re.search(pattern, html_code, re.IGNORECASE):
                class_name = re.findall(r'class=["\'](.*?)["\']', pattern)[0]
                return {
                    'is_passed': False,
                    'msg': f'请删除冗余的<div class="{class_name}">标签，已用语义化标签替代',
                    'error_type': '冗余div标签未删除',
                    'score': 0
                }

        # 3. 检查语义化标签嵌套合理性（main不应嵌套在header/nav/footer内，JSON hint要求）
        try:
            parser = etree.HTMLParser(recover=True)
            tree = etree.HTML(html_code, parser=parser)
            if tree.xpath('//header/main | //nav/main | //footer/main'):
                return {
                    'is_passed': False,
                    'msg': '<main>标签是核心内容区，不应嵌套在<header>、<nav>或<footer>内',
                    'error_type': '语义化标签嵌套错误',
                    'score': 0
                }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'语义化标签结构异常：{str(e)[:50]}',
                'error_type': '结构异常',
                'score': 0
            }

        # 所有校验通过
        return {
            'is_passed': True,
            'msg': '语义化重构完成！页面结构更清晰，符合JSON要求～',
            'error_type': None,
            'score': 100
        }

    @staticmethod
    def validate_1_3(html_code):
        """关卡1-3：HTML文本与媒体标签校验（匹配JSON task：添加h1-h3/p/img/a+完整属性）"""
        h1_tags = re.findall(r'<h1\b[^>]*>', html_code, re.IGNORECASE)
        if not h1_tags:
            return {
                'is_passed': False,
                'msg': '缺少最高层级标题<h1>（要求：My Travel Blog）',
                'error_type': 'h1标签缺失',
                'score': 0
            }
        if len(h1_tags) > 1:
            return {
                'is_passed': False,
                'msg': f'检测到{len(h1_tags)}个<h1>标签，JSON要求页面仅1个<h1>',
                'error_type': 'h1标签重复',
                'score': 0
            }

        h2_tags = re.findall(r'<h2\b[^>]*>', html_code, re.IGNORECASE)
        if not h2_tags:
            return {
                'is_passed': False,
                'msg': '缺少二级标题<h2>（要求：Trip to Yunnan）',
                'error_type': 'h2标签缺失',
                'score': 0
            }

        # 2. 检查p标签（包裹指定文本，JSON task要求）
        p_pattern = re.compile(r'<p\b[^>]*>.*?Yunnan is a beautiful place with snow-capped mountains, lakes, and ancient cities.*?</p>', re.DOTALL | re.IGNORECASE)
        if not p_pattern.search(html_code):
            return {
                'is_passed': False,
                'msg': '缺少<p>标签或文本内容错误，请包裹指定描述文本',
                'error_type': 'p标签缺失/内容错误',
                'score': 0
            }

        # 3. 检查img标签（src/alt属性完整，JSON task要求）
        img_tags = re.findall(r'<img\b[^>]*>', html_code, re.IGNORECASE)
        if not img_tags:
            return {
                'is_passed': False,
                'msg': '缺少图片标签<img>，请添加src="https://picsum.photos/800/400"和alt="Yunnan Scenery"',
                'error_type': 'img标签缺失',
                'score': 0
            }
        for img_tag in img_tags:
            if not re.search(r'src=["\']https://picsum.photos/800/400["\']', img_tag, re.IGNORECASE):
                return {
                    'is_passed': False,
                    'msg': '<img>标签src属性错误，需设置为https://picsum.photos/800/400',
                    'error_type': 'img缺少src属性',
                    'score': 0
                }
            if not re.search(r'alt=["\']Yunnan Scenery["\']', img_tag, re.IGNORECASE):
                return {
                    'is_passed': False,
                    'msg': '<img>标签alt属性错误，需设置为Yunnan Scenery',
                    'error_type': 'img缺少alt属性',
                    'score': 0
                }

        # 4. 检查a标签（href/文本完整，JSON task要求）
        a_tags = re.findall(r'<a\b[^>]*>', html_code, re.IGNORECASE)
        if not a_tags:
            return {
                'is_passed': False,
                'msg': '缺少链接标签<a>，请添加文本"View More Photos"和href="https://example.com/yunnan"',
                'error_type': 'a标签缺失',
                'score': 0
            }
        for a_tag in a_tags:
            if not re.search(r'href=["\']https://example.com/yunnan["\']', a_tag, re.IGNORECASE):
                return {
                    'is_passed': False,
                    'msg': '<a>标签href属性错误，需设置为https://example.com/yunnan',
                    'error_type': 'a缺少href属性',
                    'score': 0
                }
            if not re.search(r'>View More Photos<', html_code, re.IGNORECASE):
                return {
                    'is_passed': False,
                    'msg': '<a>标签文本错误，需设置为View More Photos',
                    'error_type': 'a标签文本错误',
                    'score': 0
                }

        # 所有校验通过
        return {
            'is_passed': True,
            'msg': '文本与媒体标签使用规范！完全匹配JSON要求～',
            'error_type': None,
            'score': 100
        }

    @staticmethod
    def validate_1_4(html_code, css_code):
        """关卡1-4：语义化标签选择题（匹配JSON 1-4）"""
        if not css_code:
            return {
                'is_passed': False,
                'msg': '未选择答案，请选择<main>标签的正确描述',
                'error_type': '未答题',
                'score': 0
            }
        correct_answer = 'B'  # JSON中correct_answer为B
        if css_code.strip() == correct_answer:
            return {
                'is_passed': True,
                'msg': '回答正确！<main>是页面核心内容区，建议仅一个',
                'error_type': None,
                'score': 10  # JSON中score为10
            }
        else:
            return {
                'is_passed': False,
                'msg': f'回答错误，正确答案是B（<main>用于包裹页面核心内容）',
                'error_type': '答案错误',
                'score': 0
            }