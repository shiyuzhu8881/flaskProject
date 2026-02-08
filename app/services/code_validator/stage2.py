"""阶段2校验逻辑：CSS选择器、盒模型、选择器拖拽、文本样式（匹配default_levels.json）"""
# 替换cssutils为tinycss2 + 兼容封装
import tinycss2
import re
import logging
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tinycss2 import parse_stylesheet, parse_component_value_list
from tinycss2.ast import QualifiedRule, Declaration, Comment, AtRule

# 无需禁用日志（tinycss2无日志输出）

# 兼容cssutils的CSSRule.STYLE_RULE常量（保持代码逻辑不变）
CSSRule_STYLE_RULE = 1

class CSSUtilsCompat:
    """tinycss2封装层，完全兼容原cssutils的使用方式"""
    @staticmethod
    def parseString(css_code):
        """解析CSS字符串，返回兼容cssutils的样式表对象"""
        # 解析CSS为tinycss2节点，跳过注释/空白
        nodes = parse_stylesheet(
            css_code,
            skip_comments=True,
            skip_whitespace=True
        )
        # 封装为兼容对象
        return StylesheetCompat(nodes)

class StylesheetCompat:
    """兼容cssutils的Stylesheet对象"""
    def __init__(self, nodes):
        self.nodes = nodes
        # 过滤仅样式规则（对应cssutils的STYLE_RULE）
        self.style_rules = [
            RuleCompat(node) for node in nodes
            if isinstance(node, QualifiedRule)
        ]

    def __iter__(self):
        """兼容原代码的for rule in stylesheet遍历"""
        for rule in self.style_rules:
            yield rule

class RuleCompat:
    """兼容cssutils的StyleRule对象"""
    def __init__(self, qualified_rule):
        self.node = qualified_rule
        self.type = CSSRule_STYLE_RULE  # 模拟cssutils的rule.type
        # 解析选择器文本（兼容原selectorText）
        self.selectorText = self._get_selector_text()
        # 解析样式属性（兼容原rule.style）
        self.style = self._parse_style_declarations()

    def _get_selector_text(self):
        """提取选择器文本（如h1、.intro、#title）"""
        if not self.node.prelude:
            return ""
        # 拼接选择器节点为字符串
        selector_parts = []
        for part in self.node.prelude:
            if part.type == 'ident' or part.type == 'hash' or part.type == 'dot' or part.type == 'space' or part.type == 'colon':
                selector_parts.append(part.value if hasattr(part, 'value') else part.type)
        # 清理空格，返回纯选择器文本
        selector = ''.join(selector_parts).replace('space', ' ').strip()
        return selector

    def _parse_style_declarations(self):
        """解析样式声明，返回兼容原rule.style的对象"""
        declarations = []
        # 解析声明块
        if self.node.content:
            # 解析组件值列表为声明
            decl_nodes = parse_component_value_list(self.node.content)
            for node in decl_nodes:
                if isinstance(node, Declaration):
                    # 封装为兼容的Property对象
                    prop = PropertyCompat(node.name, node.value)
                    declarations.append(prop)
        # 返回兼容的StyleCompat对象
        return StyleCompat(declarations)

class StyleCompat:
    """兼容cssutils的Style对象（遍历属性用）"""
    def __init__(self, declarations):
        self.declarations = declarations

    def __iter__(self):
        """兼容原代码的for prop in rule.style遍历"""
        for decl in self.declarations:
            yield decl

class PropertyCompat:
    """兼容cssutils的Property对象（name/value属性）"""
    def __init__(self, name, value_nodes):
        self.name = name
        # 拼接值节点为字符串（如red、15px、center）
        self.value = ''.join([
            node.value if hasattr(node, 'value') else ''
            for node in value_nodes
            if node.type not in ['whitespace', 'comment']
        ]).strip().lower()

class Stage2Validator:
    # 缓存兼容解析器（替代原cssutils解析器）
    _css_parser = None

    @classmethod
    def _init_css_parser(cls):
        """初始化兼容解析器（替换原cssutils解析器）"""
        if cls._css_parser is None:
            cls._css_parser = CSSUtilsCompat()  # 使用兼容层
        return cls._css_parser

    @staticmethod
    def _init_selenium():
        """初始化无头浏览器（逻辑不变）"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(10)
            return driver
        except Exception as e:
            logging.error(f"浏览器初始化失败：{e}")
            return None

    @staticmethod
    def validate(level_id, html_code, css_code):
        """阶段2统一校验入口（逻辑不变）"""
        if level_id == '2-1':
            return Stage2Validator.validate_2_1(html_code, css_code)
        elif level_id == '2-2':
            return Stage2Validator.validate_2_2(html_code, css_code)
        elif level_id == '2-3':
            return Stage2Validator.validate_2_3(html_code, css_code)
        elif level_id == '2-4':
            return Stage2Validator.validate_2_4(html_code, css_code)
        else:
            return {
                'is_passed': False,
                'msg': 'Stage 2 level ID error',
                'error_type': '系统错误',
                'score': 0
            }

    @staticmethod
    def validate_2_1(html_code, css_code):
        """关卡2-1：CSS选择器基础校验（仅替换解析器，逻辑完全不变）"""
        parser = Stage2Validator._init_css_parser()
        try:
            # 改用兼容层解析CSS（调用方式和原cssutils一致）
            stylesheet = parser.parseString(css_code)
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'CSS syntax error: {str(e)[:50]}',
                'error_type': 'CSS语法错误',
                'score': 0
            }

        # 过滤样式规则（逻辑不变）
        style_rules = [
            rule for rule in stylesheet
            if rule.type == CSSRule_STYLE_RULE
        ]

        total_score = 100
        error_list = []
        score_deduction = 25

        # 检查h1元素选择器（逻辑不变）
        h1_rules = [r for r in style_rules if r.selectorText and 'h1' in r.selectorText]
        if not h1_rules:
            error_list.append('Missing h1 element selector (need to set styles for the <h1> tag)')
            total_score -= score_deduction
        else:
            h1_color = None
            for rule in h1_rules:
                for prop in rule.style:
                    if prop.name == 'color':
                        h1_color = prop.value.strip().lower()
            if h1_color != 'red':
                error_list.append('Incorrect color property for h1 element (required: red, the initial code was mistakenly written as rede)')
                total_score -= score_deduction

        # 检查.intro类选择器（逻辑不变）
        intro_rules = [r for r in style_rules if r.selectorText and '.intro' in r.selectorText]
        if not intro_rules:
            error_list.append('Incorrect .intro class selector (missing ., need to match class="intro")')
            total_score -= score_deduction
        else:
            intro_color = None
            for rule in intro_rules:
                for prop in rule.style:
                    if prop.name == 'color':
                        intro_color = prop.value.strip().lower()
            if intro_color != 'blue':
                error_list.append('The color property of the .intro class selector should be set to blue')
                total_score -= score_deduction

        # 检查#title ID选择器（逻辑不变）
        title_rules = [r for r in style_rules if r.selectorText and '#title' in r.selectorText]
        if not title_rules:
            error_list.append('Incorrect #title ID selector (missing #, need to match id="title")')
            total_score -= score_deduction
        else:
            title_align = None
            for rule in title_rules:
                for prop in rule.style:
                    if prop.name == 'text-align':
                        title_align = prop.value.strip().lower()
            if title_align != 'center':
                error_list.append('The text-align property of the #title ID selector should be set to center')
                total_score -= score_deduction

        # 检查.box选择器（逻辑不变）
        box_rules = [r for r in style_rules if r.selectorText and '.box' in r.selectorText]
        if not box_rules:
            error_list.append('The .box class selector was mistakenly written as .boxx (need to match class="box")')
            total_score -= score_deduction

        is_passed = len(error_list) == 0
        return {
            'is_passed': is_passed,
            'msg': 'All CSS selectors are correct! Meet the requirements of 2-1～' if is_passed else f'Errors: {" | ".join(error_list)}',
            'error_type': None if is_passed else '选择器错误',
            'score': max(total_score, 0)
        }

    @staticmethod
    def validate_2_2(html_code, css_code):
        """关卡2-2：CSS盒模型校验（逻辑完全不变）"""
        driver = Stage2Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': 'Failed to start the browser, unable to validate box model styles',
                'error_type': '环境错误',
                'score': 0
            }

        total_score = 100
        error_list = []
        score_deduction = 20

        try:
            import urllib.parse
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            encoded_html = urllib.parse.quote(full_html, safe='')
            driver.get(f"data:text/html;charset=utf-8,{encoded_html}")

            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'box'))
                )
                box_exists = True
            except:
                box_exists = driver.execute_script("return !!document.querySelector('.box');")
                if not box_exists:
                    error_list.append('.box element not found, please check if the HTML structure contains an element with class="box"')
                    total_score = 0

            if box_exists:
                # 检查box-sizing
                box_box_sizing = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const sizing = getComputedStyle(box).boxSizing;
                    return sizing.toLowerCase();
                """)
                if box_box_sizing != 'border-box':
                    error_list.append('box-sizing of .box is not set to border-box (required to keep width 200px)')
                    total_score -= score_deduction

                # 检查padding
                box_padding = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const pad = getComputedStyle(box);
                    return {
                        top: pad.paddingTop,
                        right: pad.paddingRight,
                        bottom: pad.paddingBottom,
                        left: pad.paddingLeft
                    };
                """)
                if not (box_padding['top'] == '15px' and box_padding['right'] == '15px' and
                        box_padding['bottom'] == '15px' and box_padding['left'] == '15px'):
                    error_list.append('The padding of .box is not set to 15px (required: 15px uniform internal spacing)')
                    total_score -= score_deduction

                # 检查border
                box_border = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const border = getComputedStyle(box);
                    return {
                        width: border.borderWidth,
                        style: border.borderStyle,
                        color: border.borderColor.toLowerCase().replace(/\\s+/g, '')
                    };
                """)
                valid_gray_colors = ['rgb(204,204,204)', '#ccc', '#cccccc']
                if (box_border['width'] != '2px' or
                        box_border['style'] != 'solid' or
                        box_border['color'] not in valid_gray_colors):
                    error_list.append('Incorrect border for .box (required: 2px solid #ccc)')
                    total_score -= score_deduction

                # 检查margin
                box_margin = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const margin = getComputedStyle(box);
                    return {
                        right: margin.marginRight,
                        bottom: margin.marginBottom
                    };
                """)
                if box_margin['right'] != '20px' or box_margin['bottom'] != '20px':
                    error_list.append('Incorrect margin for .box (required: 20px spacing on right and bottom only)')
                    total_score -= score_deduction

                # 检查宽度
                box_width = driver.execute_script("""
                    const box = document.querySelector('.box');
                    return box.offsetWidth;
                """)
                if not (199 <= box_width <= 201):
                    error_list.append('The actual width of .box is not 200px (check box-sizing/border/padding settings)')
                    total_score -= score_deduction

                # 检查容器flex-wrap（提示）
                container_flex_wrap = driver.execute_script("""
                    const container = document.querySelector('.container');
                    if (!container) return '';
                    return getComputedStyle(container).flexWrap;
                """)
                if container_flex_wrap != 'wrap' and total_score > 0:
                    error_list.append('Tips: Add flex-wrap: wrap to .container for better multi-box layout (no score deduction)')

        except Exception as e:
            logging.error(f"盒模型校验异常：{e}")
            return {
                'is_passed': False,
                'msg': f'Box model validation exception: {str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

        is_passed = len([err for err in error_list if not err.startswith('Tips:')]) == 0
        return {
            'is_passed': is_passed,
            'msg': 'CSS box model settings are correct! Meet the requirements of 2-2～' if is_passed else f'Errors: {" | ".join(error_list)}',
            'error_type': None if is_passed else '盒模型设置错误',
            'score': max(total_score, 0)
        }

    @staticmethod
    def validate_2_3(html_code, css_code):
        """关卡2-3：CSS选择器拖拽题（逻辑完全不变）"""
        try:
            drag_result = json.loads(css_code) if css_code.strip() else {}
        except json.JSONDecodeError:
            return {
                'is_passed': False,
                'msg': 'Incorrect format of drag-and-drop results, please pass a valid JSON',
                'error_type': '格式错误',
                'score': 0
            }

        correct_mapping = {
            'target1': 'drag2',
            'target2': 'drag1',
            'target3': 'drag3'
        }
        wrong_count = 0
        wrong_mapping = []
        for target, correct_drag in correct_mapping.items():
            user_drag = drag_result.get(target, '')
            if user_drag != correct_drag:
                wrong_count += 1
                wrong_mapping.append(f'{target} should match {correct_drag} (you selected {user_drag})')

        total_score = 15 - (wrong_count * 5)
        is_passed = wrong_count == 0

        return {
            'is_passed': is_passed,
            'msg': 'Drag-and-drop matching is correct! Fully meet the requirements of 2-3～' if is_passed else f'Errors: {" | ".join(wrong_mapping)}',
            'error_type': None if is_passed else '匹配错误',
            'score': max(total_score, 0)
        }

    @staticmethod
    def validate_2_4(html_code, css_code):
        """关卡2-4：CSS文本样式校验（仅替换解析器，逻辑完全不变）"""
        driver = Stage2Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': 'Failed to start the browser, unable to validate text styles',
                'error_type': '环境错误',
                'score': 0
            }

        total_score = 100
        error_list = []
        score_deduction = 20

        try:
            import urllib.parse
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            encoded_html = urllib.parse.quote(full_html, safe='')
            driver.get(f"data:text/html;charset=utf-8,{encoded_html}")

            # 检查.article元素是否存在
            article_exists = driver.execute_script("return !!document.querySelector('.article');")
            if not article_exists:
                error_list.append('.article element not found, please check if the HTML structure contains a container with class="article"')
                total_score = 0
            else:
                # 检查.article h2标题样式
                h2_style = driver.execute_script("""
                        const h2 = document.querySelector('.article h2');
                        if (!h2) return { textAlign: 'missing', color: 'missing' };
                        const style = getComputedStyle(h2);
                        const color = style.color.replace(/\\s+/g, '').toLowerCase();
                        return {
                            textAlign: style.textAlign.toLowerCase(),
                            color: color
                        };
                    """)
                valid_h2_colors = ['rgb(44,62,80)', '#2c3e50', '#2C3E50']
                if h2_style['textAlign'] == 'missing':
                    error_list.append('Missing .article h2 selector (need to set styles for h2 under .article)')
                    total_score -= score_deduction
                elif h2_style['textAlign'] != 'center' or h2_style['color'] not in valid_h2_colors:
                    error_list.append('Incorrect .article h2 styles (required: text-align:center + color:#2c3e50)')
                    total_score -= score_deduction

                # 检查.article p段落样式
                p_style = driver.execute_script("""
                        const p = document.querySelector('.article p');
                        if (!p) return { color: 'missing', fontSize: 'missing', lineHeight: 'missing' };
                        const style = getComputedStyle(p);
                        const color = style.color.replace(/\\s+/g, '').toLowerCase();
                        return {
                            color: color,
                            fontSize: style.fontSize,
                            lineHeight: style.lineHeight
                        };
                    """)
                valid_p_colors = ['rgb(51,51,51)', '#333', '#333333']
                if p_style['color'] == 'missing':
                    error_list.append('Missing .article p selector (need to set styles for p under .article)')
                    total_score -= score_deduction
                else:
                    if p_style['color'] not in valid_p_colors or p_style['fontSize'] != '16px':
                        error_list.append('Incorrect .article p styles (required: color:#333 + font-size:16px)')
                        total_score -= score_deduction
                    # 检查line-height（改用兼容解析器）
                    parser = Stage2Validator._init_css_parser()
                    style_sheet = parser.parseString(css_code)
                    p_rules = [r for r in style_sheet if r.type == CSSRule_STYLE_RULE and
                               r.selectorText and '.article p' in r.selectorText]
                    line_height_correct = False
                    for rule in p_rules:
                        for prop in rule.style:
                            if prop.name == 'line-height' and prop.value.strip() == '1.6':
                                line_height_correct = True
                                break
                    if not line_height_correct:
                        computed_line_height = p_style['lineHeight']
                        if not (computed_line_height == '1.6' or computed_line_height == '25.6px'):
                            error_list.append('The line-height of .article p should be set to 1.6')
                            total_score -= score_deduction

                # 检查.article a链接基础样式
                a_style = driver.execute_script("""
                        const a = document.querySelector('.article a');
                        if (!a) return { color: 'missing', textDecoration: 'missing' };
                        const style = getComputedStyle(a);
                        const color = style.color.replace(/\\s+/g, '').toLowerCase();
                        const textDecoration = style.textDecoration || style.textDecorationLine;
                        return {
                            color: color,
                            textDecoration: textDecoration.toLowerCase()
                        };
                    """)
                valid_a_colors = ['rgb(52,152,219)', '#3498db', '#3498DB']
                if a_style['color'] == 'missing':
                    error_list.append('Missing .article a selector (need to set styles for a under .article)')
                    total_score -= score_deduction
                elif a_style['color'] not in valid_a_colors or a_style['textDecoration'] != 'none':
                    error_list.append('Incorrect .article a styles (required: color:#3498db + text-decoration:none)')
                    total_score -= score_deduction

                # 检查.article a:hover样式
                a_hover_correct = False
                # 改用兼容解析器解析
                hover_rules = [r for r in style_sheet if r.type == CSSRule_STYLE_RULE and
                               r.selectorText and '.article a:hover' in r.selectorText]
                for rule in hover_rules:
                    for prop in rule.style:
                        if prop.name == 'color' and prop.value.strip().lower() == 'red':
                            a_hover_correct = True
                            break
                if not a_hover_correct:
                    error_list.append('Incorrect .article a:hover styles (required: color:red)')
                    total_score -= score_deduction

        except Exception as e:
            logging.error(f"文本样式校验异常：{e}")
            return {
                'is_passed': False,
                'msg': f'Text style validation exception: {str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

        is_passed = len(error_list) == 0
        error_list = list(set(error_list))
        total_score = max(total_score, 0)

        return {
            'is_passed': is_passed,
            'msg': 'Text style beautification completed! Meet the requirements of 2-4～' if is_passed else f'Errors: {" | ".join(error_list)}',
            'error_type': None if is_passed else '文本样式错误',
            'score': total_score
        }
