"""阶段2校验逻辑：CSS选择器、盒模型、选择器拖拽、文本样式（匹配default_levels.json）"""
import cssutils
import re
import logging
import json  # 统一导入，避免方法内重复导入
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 全局禁用cssutils日志（彻底避免日志相关错误）
cssutils.log.enabled = False

class Stage2Validator:
    # 缓存CSS解析器（避免重复初始化）
    _css_parser = None

    @classmethod
    def _init_css_parser(cls):
        """初始化CSS解析器（修复日志设置+单例缓存）"""
        if cls._css_parser is None:
            # 核心修复1：禁用cssutils所有日志（替代错误的logging.WARNING）
            cssutils.log.enabled = False
            cls._css_parser = cssutils.CSSParser()
        return cls._css_parser

    @staticmethod
    def _init_selenium():
        """初始化无头浏览器（增强容错+优化配置）"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')  # 兼容Windows环境
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 屏蔽Chrome日志
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(10)  # 设置超时，避免卡死
            return driver
        except Exception as e:
            logging.error(f"浏览器初始化失败：{e}")
            return None

    @staticmethod
    def validate(level_id, html_code, css_code):
        """阶段2统一校验入口（匹配JSON：2-1/2-2/2-3/2-4）"""
        # 核心适配：返回msg字段（兼容api.py）
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
                'msg': '阶段2关卡ID错误',  # 改回msg
                'error_type': '系统错误',
                'score': 0
            }

    @staticmethod
    def validate_2_1(html_code, css_code):
        """关卡2-1：CSS选择器基础校验（核心修复：过滤注释节点+增强容错）"""
        # 1. 初始化解析器+解析CSS
        parser = Stage2Validator._init_css_parser()
        try:
            stylesheet = parser.parseString(css_code)
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'CSS语法错误：{str(e)[:50]}',  # 改回msg
                'error_type': 'CSS语法错误',
                'score': 0
            }

        # 核心修复2：过滤仅样式规则节点（排除注释、媒体查询等无selectorText的节点）
        style_rules = [
            rule for rule in stylesheet
            if rule.type == cssutils.css.CSSRule.STYLE_RULE  # 仅保留样式规则
        ]

        # 初始化得分和错误列表（支持部分得分，而非全0/全100）
        total_score = 100
        error_list = []
        score_deduction = 25  # 每个错误扣25分

        # 2. 检查h1元素选择器
        h1_rules = [r for r in style_rules if r.selectorText and 'h1' in r.selectorText]
        if not h1_rules:
            error_list.append('缺少h1元素选择器（需为<h1>标签设置样式）')
            total_score -= score_deduction
        else:
            h1_color = None
            for rule in h1_rules:
                for prop in rule.style:
                    if prop.name == 'color':
                        h1_color = prop.value.strip().lower()
            if h1_color != 'red':
                error_list.append('h1元素color属性错误（要求：red，初始代码误写为rede）')
                total_score -= score_deduction

        # 3. 检查.intro类选择器
        intro_rules = [r for r in style_rules if r.selectorText and '.intro' in r.selectorText]
        if not intro_rules:
            error_list.append('类选择器.intro错误（缺少.，需匹配class="intro"）')
            total_score -= score_deduction
        else:
            intro_color = None
            for rule in intro_rules:
                for prop in rule.style:
                    if prop.name == 'color':
                        intro_color = prop.value.strip().lower()
            if intro_color != 'blue':
                error_list.append('.intro类选择器color属性应设置为blue')
                total_score -= score_deduction

        # 4. 检查#title ID选择器
        title_rules = [r for r in style_rules if r.selectorText and '#title' in r.selectorText]
        if not title_rules:
            error_list.append('ID选择器#title错误（缺少#，需匹配id="title"）')
            total_score -= score_deduction
        else:
            title_align = None
            for rule in title_rules:
                for prop in rule.style:
                    if prop.name == 'text-align':
                        title_align = prop.value.strip().lower()
            if title_align != 'center':
                error_list.append('#title ID选择器text-align应设置为center')
                total_score -= score_deduction

        # 5. 检查.box选择器
        box_rules = [r for r in style_rules if r.selectorText and '.box' in r.selectorText]
        if not box_rules:
            error_list.append('类选择器.box误写为.boxx（需匹配class="box"）')
            total_score -= score_deduction

        # 最终结果
        is_passed = len(error_list) == 0
        return {
            'is_passed': is_passed,
            'msg': 'CSS选择器全部正确！匹配2-1要求～' if is_passed else f'错误：{" | ".join(error_list)}',  # 改回msg
            'error_type': None if is_passed else '选择器错误',
            'score': max(total_score, 0)  # 确保分数≥0
        }

    @staticmethod
    def validate_2_2(html_code, css_code):
        """关卡2-2：CSS盒模型校验（修复：元素存在性检查+样式判断兼容）"""
        driver = Stage2Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': '无法启动浏览器，无法校验盒模型样式',
                'error_type': '环境错误',
                'score': 0
            }

        total_score = 100
        error_list = []
        score_deduction = 34  # 3个检查项，每项扣34分（避免小数）

        try:
            # 修复1：HTML代码编码处理（避免特殊字符导致URL解析错误）
            import urllib.parse
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            encoded_html = urllib.parse.quote(full_html, safe='')  # 编码特殊字符
            driver.get(f"data:text/html;charset=utf-8,{encoded_html}")

            # 修复2：等待元素加载（最多等待5秒，轮询检查.box元素）
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            try:
                # 等待.box元素出现，超时5秒
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'box'))
                )
                box_exists = True
            except:
                # 重试：直接查询（兼容旧版Selenium）
                box_exists = driver.execute_script("return !!document.querySelector('.box');")
                if not box_exists:
                    error_list.append('未找到.box元素，请检查HTML结构中是否包含class="box"的元素')
                    total_score = 0

            if box_exists:
                # 1. 检查padding（15px内部间距）
                box_padding = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const pad = getComputedStyle(box);
                    return pad.paddingTop + '|' + pad.paddingRight + '|' + pad.paddingBottom + '|' + pad.paddingLeft;
                """)
                if '15px' not in box_padding:
                    error_list.append('.box的padding未设置为15px（要求：内部间距15px）')
                    total_score -= score_deduction

                # 2. 检查border（2px灰色实线，兼容#ccc的多种RGB表示）
                box_border = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const border = getComputedStyle(box);
                    return {
                        width: border.borderWidth,
                        style: border.borderStyle,
                        color: border.borderColor.toLowerCase()
                    };
                """)
                # 兼容#ccc的RGB：rgb(204,204,204) / rgb(192,192,192) / #ccc
                valid_gray_colors = ['rgb(204, 204, 204)', 'rgb(192, 192, 192)', '#ccc', '#cccccc']
                if (box_border['width'] != '2px' or
                        box_border['style'] != 'solid' or
                        box_border['color'] not in valid_gray_colors):
                    error_list.append('.box的border错误（要求：2px solid #ccc）')
                    total_score -= score_deduction

                # 3. 检查margin（20px外部间距）
                box_margin = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const margin = getComputedStyle(box);
                    return margin.marginTop + '|' + margin.marginRight + '|' + margin.marginBottom + '|' + margin.marginLeft;
                """)
                if '20px' not in box_margin:
                    error_list.append('.box的margin未设置为20px（要求：外部间距20px）')
                    total_score -= score_deduction

        except Exception as e:
            logging.error(f"盒模型校验异常：{e}")
            return {
                'is_passed': False,
                'msg': f'盒模型校验异常：{str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

        # 最终结果
        is_passed = len(error_list) == 0
        return {
            'is_passed': is_passed,
            'msg': 'CSS盒模型设置正确！匹配2-2要求～' if is_passed else f'错误：{" | ".join(error_list)}',
            'error_type': None if is_passed else '盒模型设置错误',
            'score': max(total_score, 0)
        }

    @staticmethod
    def validate_2_3(html_code, css_code):
        """关卡2-3：CSS选择器拖拽题（增强容错+合理得分）"""
        # 拖拽题：css_code存储前端传入的匹配结果JSON
        try:
            drag_result = json.loads(css_code) if css_code.strip() else {}
        except json.JSONDecodeError:
            return {
                'is_passed': False,
                'msg': '拖拽结果格式错误，请传入合法JSON',  # 改回msg
                'error_type': '格式错误',
                'score': 0
            }

        # 正确匹配映射（来自JSON的extra_config）
        correct_mapping = {
            'target1': 'drag2',
            'target2': 'drag1',
            'target3': 'drag3'
        }
        # 校验匹配结果（支持部分得分）
        wrong_count = 0
        wrong_mapping = []
        for target, correct_drag in correct_mapping.items():
            user_drag = drag_result.get(target, '')
            if user_drag != correct_drag:
                wrong_count += 1
                wrong_mapping.append(f'{target}应匹配{correct_drag}（你选了{user_drag}）')

        # 总分15分（JSON中score=15），每个正确项得5分
        total_score = 15 - (wrong_count * 5)
        is_passed = wrong_count == 0

        return {
            'is_passed': is_passed,
            'msg': '拖拽匹配正确！完全符合2-3要求～' if is_passed else f'错误：{" | ".join(wrong_mapping)}',  # 改回msg
            'error_type': None if is_passed else '匹配错误',
            'score': max(total_score, 0)
        }

    @staticmethod
    def validate_2_4(html_code, css_code):
        """关卡2-4：CSS文本样式校验（修复：lineHeight判断+hover样式检查+元素存在性）"""
        driver = Stage2Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': '无法启动浏览器，无法校验文本样式',  # 改回msg
                'error_type': '环境错误',
                'score': 0
            }

        total_score = 100
        error_list = []
        score_deduction = 20  # 5个检查项，每项扣20分

        try:
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{full_html}")

            # 检查核心元素是否存在
            article_exists = driver.execute_script("return !!document.querySelector('.article');")
            if not article_exists:
                error_list.append('未找到.article元素，请检查HTML结构')
                total_score = 0
            else:
                # 1. 检查h2标题样式（居中+#2c3e50）
                h2_style = driver.execute_script("""
                    const h2 = document.querySelector('.article h2');
                    if (!h2) return { textAlign: 'none', color: 'none' };
                    const style = getComputedStyle(h2);
                    return {
                        textAlign: style.textAlign,
                        color: style.color
                    };
                """)
                if h2_style['textAlign'] != 'center' or h2_style['color'] != 'rgb(44, 62, 80)':
                    error_list.append('h2标题样式错误（要求：text-align:center + color:#2c3e50）')
                    total_score -= score_deduction

                # 2. 检查段落样式（#333 + font-size16px）
                p_style = driver.execute_script("""
                    const p = document.querySelector('.article p');
                    if (!p) return { color: 'none', fontSize: 'none' };
                    const style = getComputedStyle(p);
                    return {
                        color: style.color,
                        fontSize: style.fontSize
                    };
                """)
                if p_style['color'] != 'rgb(51, 51, 51)' or p_style['fontSize'] != '16px':
                    error_list.append('段落样式错误（要求：color:#333 + font-size:16px）')
                    total_score -= score_deduction

                # 3. 检查段落line-height（修复：直接解析CSS规则，而非计算值）
                parser = Stage2Validator._init_css_parser()
                style_sheet = parser.parseString(css_code)
                p_rules = [r for r in style_sheet if r.type == cssutils.css.CSSRule.STYLE_RULE and
                           r.selectorText and 'p' in r.selectorText]
                line_height_correct = False
                for rule in p_rules:
                    for prop in rule.style:
                        if prop.name == 'line-height' and prop.value.strip() == '1.6':
                            line_height_correct = True
                            break
                if not line_height_correct:
                    error_list.append('段落line-height应设置为1.6')
                    total_score -= score_deduction

                # 4. 检查链接基础样式（#3498db + 无下划线）
                a_style = driver.execute_script("""
                    const a = document.querySelector('.article a');
                    if (!a) return { color: 'none', textDecoration: 'none' };
                    const style = getComputedStyle(a);
                    return {
                        color: style.color,
                        textDecoration: style.textDecorationLine
                    };
                """)
                if a_style['color'] != 'rgb(52, 152, 219)' or a_style['textDecoration'] != 'none':
                    error_list.append('链接样式错误（要求：color:#3498db + text-decoration:none）')
                    total_score -= score_deduction

                # 5. 检查链接hover样式（修复：解析CSS规则，而非模拟事件）
                a_hover_correct = False
                hover_rules = [r for r in style_sheet if r.type == cssutils.css.CSSRule.STYLE_RULE and
                              r.selectorText and 'a:hover' in r.selectorText]
                for rule in hover_rules:
                    for prop in rule.style:
                        if prop.name == 'color' and prop.value.strip().lower() == 'red':
                            a_hover_correct = True
                            break
                if not a_hover_correct:
                    error_list.append('链接hover样式错误（要求：color:red）')
                    total_score -= score_deduction

        except Exception as e:
            logging.error(f"文本样式校验异常：{e}")
            return {
                'is_passed': False,
                'msg': f'文本样式校验异常：{str(e)[:50]}',  # 改回msg
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

        # 最终结果
        is_passed = len(error_list) == 0
        return {
            'is_passed': is_passed,
            'msg': '文本样式美化完成！匹配2-4要求～' if is_passed else f'错误：{" | ".join(error_list)}',  # 改回msg
            'error_type': None if is_passed else '文本样式错误',
            'score': max(total_score, 0)
        }