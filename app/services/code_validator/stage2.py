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
                'msg': 'Stage 2 level ID error',  # 英文替换
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
                'msg': f'CSS syntax error: {str(e)[:50]}',  # 英文替换
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
            error_list.append('Missing h1 element selector (need to set styles for the <h1> tag)')  # 英文替换
            total_score -= score_deduction
        else:
            h1_color = None
            for rule in h1_rules:
                for prop in rule.style:
                    if prop.name == 'color':
                        h1_color = prop.value.strip().lower()
            if h1_color != 'red':
                error_list.append('Incorrect color property for h1 element (required: red, the initial code was mistakenly written as rede)')  # 英文替换
                total_score -= score_deduction

        # 3. 检查.intro类选择器
        intro_rules = [r for r in style_rules if r.selectorText and '.intro' in r.selectorText]
        if not intro_rules:
            error_list.append('Incorrect .intro class selector (missing ., need to match class="intro")')  # 英文替换
            total_score -= score_deduction
        else:
            intro_color = None
            for rule in intro_rules:
                for prop in rule.style:
                    if prop.name == 'color':
                        intro_color = prop.value.strip().lower()
            if intro_color != 'blue':
                error_list.append('The color property of the .intro class selector should be set to blue')  # 英文替换
                total_score -= score_deduction

        # 4. 检查#title ID选择器
        title_rules = [r for r in style_rules if r.selectorText and '#title' in r.selectorText]
        if not title_rules:
            error_list.append('Incorrect #title ID selector (missing #, need to match id="title")')  # 英文替换
            total_score -= score_deduction
        else:
            title_align = None
            for rule in title_rules:
                for prop in rule.style:
                    if prop.name == 'text-align':
                        title_align = prop.value.strip().lower()
            if title_align != 'center':
                error_list.append('The text-align property of the #title ID selector should be set to center')  # 英文替换
                total_score -= score_deduction

        # 5. 检查.box选择器
        box_rules = [r for r in style_rules if r.selectorText and '.box' in r.selectorText]
        if not box_rules:
            error_list.append('The .box class selector was mistakenly written as .boxx (need to match class="box")')  # 英文替换
            total_score -= score_deduction

        # 最终结果
        is_passed = len(error_list) == 0
        return {
            'is_passed': is_passed,
            'msg': 'All CSS selectors are correct! Meet the requirements of 2-1～' if is_passed else f'Errors: {" | ".join(error_list)}',  # 英文替换
            'error_type': None if is_passed else '选择器错误',
            'score': max(total_score, 0)  # 确保分数≥0
        }

    @staticmethod
    def validate_2_2(html_code, css_code):
        """关卡2-2：CSS盒模型校验（重新设计后100%正确版）"""
        driver = Stage2Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': 'Failed to start the browser, unable to validate box model styles',  # 英文替换
                'error_type': '环境错误',
                'score': 0
            }

        total_score = 100
        error_list = []
        score_deduction = 20  # 5个检查项，每项扣20分

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
                    error_list.append('.box element not found, please check if the HTML structure contains an element with class="box"')  # 英文替换
                    total_score = 0

            if box_exists:
                # 1. 检查box-sizing（必须为border-box，确保宽度包含border/padding）
                box_box_sizing = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const sizing = getComputedStyle(box).boxSizing;
                    return sizing.toLowerCase();
                """)
                if box_box_sizing != 'border-box':
                    error_list.append('box-sizing of .box is not set to border-box (required to keep width 200px)')
                    total_score -= score_deduction

                # 2. 检查padding（15px统一内部间距）
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

                # 3. 检查border（2px灰色实线#ccc）
                box_border = driver.execute_script("""
                    const box = document.querySelector('.box');
                    const border = getComputedStyle(box);
                    return {
                        width: border.borderWidth,
                        style: border.borderStyle,
                        color: border.borderColor.toLowerCase().replace(/\\s+/g, '')
                    };
                """)
                # 兼容#ccc的RGB表示：rgb(204,204,204) / #ccc / #cccccc
                valid_gray_colors = ['rgb(204,204,204)', '#ccc', '#cccccc']
                if (box_border['width'] != '2px' or
                        box_border['style'] != 'solid' or
                        box_border['color'] not in valid_gray_colors):
                    error_list.append('Incorrect border for .box (required: 2px solid #ccc)')
                    total_score -= score_deduction

                # 4. 检查margin（仅右侧/底部20px间距：margin-right=20px + margin-bottom=20px）
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

                # 5. 检查宽度（固定200px，即使有border/padding）
                box_width = driver.execute_script("""
                    const box = document.querySelector('.box');
                    return box.offsetWidth; // 实际渲染宽度
                """)
                if not (199 <= box_width <= 201):  # 允许±1px误差
                    error_list.append('The actual width of .box is not 200px (check box-sizing/border/padding settings)')
                    total_score -= score_deduction

                # 6. 检查容器flex-wrap（可选，增强体验，不扣分仅提示）
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
                'msg': f'Box model validation exception: {str(e)[:50]}',  # 英文替换
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

        # 最终结果
        is_passed = len([err for err in error_list if not err.startswith('Tips:')]) == 0
        return {
            'is_passed': is_passed,
            'msg': 'CSS box model settings are correct! Meet the requirements of 2-2～' if is_passed else f'Errors: {" | ".join(error_list)}',
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
                'msg': 'Incorrect format of drag-and-drop results, please pass a valid JSON',  # 英文替换
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
                wrong_mapping.append(f'{target} should match {correct_drag} (you selected {user_drag})')  # 英文替换

        # 总分15分（JSON中score=15），每个正确项得5分
        total_score = 15 - (wrong_count * 5)
        is_passed = wrong_count == 0

        return {
            'is_passed': is_passed,
            'msg': 'Drag-and-drop matching is correct! Fully meet the requirements of 2-3～' if is_passed else f'Errors: {" | ".join(wrong_mapping)}',  # 英文替换
            'error_type': None if is_passed else '匹配错误',
            'score': max(total_score, 0)
        }

    @staticmethod
    def validate_2_4(html_code, css_code):
        """关卡2-4：CSS文本样式校验（完整修正：选择器限定+兼容处理+精准判断）"""
        driver = Stage2Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': 'Failed to start the browser, unable to validate text styles',  # 英文替换
                'error_type': '环境错误',
                'score': 0
            }

        total_score = 100
        error_list = []
        score_deduction = 20  # 5个检查项，每项扣20分

        try:
            # 拼接完整HTML并加载（编码处理避免特殊字符问题）
            import urllib.parse
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            encoded_html = urllib.parse.quote(full_html, safe='')
            driver.get(f"data:text/html;charset=utf-8,{encoded_html}")

            # 1. 核心检查：.article元素是否存在
            article_exists = driver.execute_script("return !!document.querySelector('.article');")
            if not article_exists:
                error_list.append('.article element not found, please check if the HTML structure contains a container with class="article"')  # 英文替换
                total_score = 0
            else:
                # 2. 检查.article h2标题样式（居中 + #2c3e50）
                h2_style = driver.execute_script("""
                        const h2 = document.querySelector('.article h2');
                        if (!h2) return { textAlign: 'missing', color: 'missing' };
                        const style = getComputedStyle(h2);
                        // 统一颜色格式：去除空格并转小写
                        const color = style.color.replace(/\\s+/g, '').toLowerCase();
                        return {
                            textAlign: style.textAlign.toLowerCase(),
                            color: color
                        };
                    """)
                # #2c3e50 对应的RGB值（去空格）：rgb(44,62,80)
                valid_h2_colors = ['rgb(44,62,80)', '#2c3e50', '#2C3E50']
                if h2_style['textAlign'] == 'missing':
                    error_list.append('Missing .article h2 selector (need to set styles for h2 under .article)')  # 英文替换
                    total_score -= score_deduction
                elif h2_style['textAlign'] != 'center' or h2_style['color'] not in valid_h2_colors:
                    error_list.append('Incorrect .article h2 styles (required: text-align:center + color:#2c3e50)')  # 英文替换
                    total_score -= score_deduction

                # 3. 检查.article p段落样式（#333 + font-size16px + line-height1.6）
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
                # #333 对应的RGB值：rgb(51,51,51)
                valid_p_colors = ['rgb(51,51,51)', '#333', '#333333']
                if p_style['color'] == 'missing':
                    error_list.append('Missing .article p selector (need to set styles for p under .article)')  # 英文替换
                    total_score -= score_deduction
                else:
                    # 检查颜色和字号
                    if p_style['color'] not in valid_p_colors or p_style['fontSize'] != '16px':
                        error_list.append('Incorrect .article p styles (required: color:#333 + font-size:16px)')  # 英文替换
                        total_score -= score_deduction
                    # 检查line-height（优先校验CSS规则，兜底校验计算值）
                    parser = Stage2Validator._init_css_parser()
                    style_sheet = parser.parseString(css_code)
                    p_rules = [r for r in style_sheet if r.type == cssutils.css.CSSRule.STYLE_RULE and
                               r.selectorText and '.article p' in r.selectorText]
                    line_height_correct = False
                    for rule in p_rules:
                        for prop in rule.style:
                            if prop.name == 'line-height' and prop.value.strip() == '1.6':
                                line_height_correct = True
                                break
                    # 兜底：如果CSS规则没写，但计算值接近1.6（比如1.6em/160%）也判定正确
                    if not line_height_correct:
                        computed_line_height = p_style['lineHeight']
                        # 1.6对应的计算值可能是25.6px（16px*1.6），兼容数值判断
                        if not (computed_line_height == '1.6' or computed_line_height == '25.6px'):
                            error_list.append('The line-height of .article p should be set to 1.6')  # 英文替换
                            total_score -= score_deduction

                # 4. 检查.article a链接基础样式（#3498db + 无下划线）
                a_style = driver.execute_script("""
                        const a = document.querySelector('.article a');
                        if (!a) return { color: 'missing', textDecoration: 'missing' };
                        const style = getComputedStyle(a);
                        const color = style.color.replace(/\\s+/g, '').toLowerCase();
                        // 兼容不同浏览器的textDecoration属性
                        const textDecoration = style.textDecoration || style.textDecorationLine;
                        return {
                            color: color,
                            textDecoration: textDecoration.toLowerCase()
                        };
                    """)
                # #3498db 对应的RGB值：rgb(52,152,219)
                valid_a_colors = ['rgb(52,152,219)', '#3498db', '#3498DB']
                if a_style['color'] == 'missing':
                    error_list.append('Missing .article a selector (need to set styles for a under .article)')  # 英文替换
                    total_score -= score_deduction
                elif a_style['color'] not in valid_a_colors or a_style['textDecoration'] != 'none':
                    error_list.append('Incorrect .article a styles (required: color:#3498db + text-decoration:none)')  # 英文替换
                    total_score -= score_deduction

                # 5. 检查.article a:hover样式（color:red）
                a_hover_correct = False
                # 解析CSS规则：必须是.article a:hover
                hover_rules = [r for r in style_sheet if r.type == cssutils.css.CSSRule.STYLE_RULE and
                               r.selectorText and '.article a:hover' in r.selectorText]
                for rule in hover_rules:
                    for prop in rule.style:
                        if prop.name == 'color' and prop.value.strip().lower() == 'red':
                            a_hover_correct = True
                            break
                if not a_hover_correct:
                    error_list.append('Incorrect .article a:hover styles (required: color:red)')  # 英文替换
                    total_score -= score_deduction

        except Exception as e:
            logging.error(f"文本样式校验异常：{e}")
            return {
                'is_passed': False,
                'msg': f'Text style validation exception: {str(e)[:50]}',  # 英文替换
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

        # 最终结果处理
        is_passed = len(error_list) == 0
        # 去重错误提示（避免重复扣分）
        error_list = list(set(error_list))
        total_score = max(total_score, 0)

        return {
            'is_passed': is_passed,
            'msg': 'Text style beautification completed! Meet the requirements of 2-4～' if is_passed else f'Errors: {" | ".join(error_list)}',  # 英文替换
            'error_type': None if is_passed else '文本样式错误',
            'score': total_score
        }
