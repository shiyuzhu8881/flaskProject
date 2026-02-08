"""阶段4校验逻辑：响应式进阶、CSS美化与动画、综合项目（修复版）"""
# 移除未使用的cssutils导入（核心修复：解决Python 3.13依赖错误）
import re
import time
import tempfile
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import JavascriptException, NoSuchElementException

class Stage4Validator:
    @staticmethod
    def validate(level_id, html_code, css_code):
        """阶段4统一校验入口"""
        if level_id == '4-1':
            return Stage4Validator.validate_4_1(html_code, css_code)
        elif level_id == '4-2':
            return Stage4Validator.validate_4_2(html_code, css_code)
        elif level_id == '4-3':
            return Stage4Validator.validate_4_3(html_code, css_code)
        else:
            return {
                'is_passed': False,
                'msg': 'Stage 4 level ID error',
                'error_type': '系统错误',
                'score': 0
            }

    @staticmethod
    def _init_selenium():
        """初始化无头浏览器（修复渲染+增加容错）"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # 增加渲染稳定性配置
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_setting_values.popups': 2
        }
        chrome_options.add_experimental_option('prefs', prefs)

        max_retries = 2
        for retry in range(max_retries):
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.implicitly_wait(5)  # 增加隐式等待
                driver.set_page_load_timeout(20)
                return driver
            except Exception as e:
                if retry == max_retries - 1:
                    print(f"浏览器初始化失败: {str(e)}")
                continue
        return None

    @staticmethod
    def _load_html(driver, html_code, css_code):
        """加载HTML+CSS到浏览器（修复渲染延迟）"""
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>{css_code}</style>
        </head>
        <body>{html_code}</body>
        </html>
        """
        # 用临时文件加载（替代data:text/html，解决渲染问题）
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(full_html)
            temp_file_path = f.name
        driver.get(f"file://{temp_file_path}")
        time.sleep(1)  # 等待渲染完成
        return temp_file_path

    @staticmethod
    def _safe_get_style(driver, selector, style_prop, fallback=''):
        """安全获取元素样式（避免元素不存在报错）"""
        try:
            return driver.execute_script(f"""
                const el = document.querySelector("{selector}");
                if (!el) return "{fallback}";
                return getComputedStyle(el).{style_prop} || "{fallback}";
            """)
        except JavascriptException:
            return fallback

    @staticmethod
    def _parse_px_value(px_str, fallback=0.0):
        """安全解析px值（兼容%/auto等格式）"""
        try:
            if '%' in px_str:
                return float(px_str.replace('%', ''))
            elif 'px' in px_str:
                return float(px_str.replace('px', ''))
            elif px_str == 'auto':
                return fallback
            else:
                return float(px_str)
        except (ValueError, TypeError):
            return fallback

    @staticmethod
    def validate_4_1(html_code, css_code):
        """关卡4-1：响应式设计进阶校验（修复移动端宽度误判版）"""
        driver = None
        temp_file_path = None
        try:
            driver = Stage4Validator._init_selenium()
            if not driver:
                return {
                    'is_passed': False,
                    'msg': 'Failed to start browser, unable to validate',
                    'error_type': '环境错误',
                    'score': 0
                }

            # 加载HTML并等待渲染
            temp_file_path = Stage4Validator._load_html(driver, html_code, css_code)

            # 1. 检查核心元素是否存在
            required_elements = ['.container', '.sidebar-left', '.main-content', '.sidebar-right', '.nav-links']
            missing_elements = []
            for sel in required_elements:
                if not driver.execute_script(f"return document.querySelector('{sel}') !== null"):
                    missing_elements.append(sel)
            if missing_elements:
                return {
                    'is_passed': False,
                    'msg': f'Missing required elements: {", ".join(missing_elements)}',
                    'error_type': '元素缺失',
                    'score': 0
                }

            # 2. 检查PC端3列布局（>1200px）
            driver.set_window_size(1400, 800)
            time.sleep(0.5)

            container_display = Stage4Validator._safe_get_style(driver, '.container', 'display')
            if container_display != 'flex':
                return {
                    'is_passed': False,
                    'msg': '.container has not enabled Flex layout, unable to implement multi-column responsiveness',
                    'error_type': '响应式布局未启用',
                    'score': 0
                }

            # 检查3列宽度分配（20% + 60% + 20%）
            container_width_pc = Stage4Validator._parse_px_value(
                Stage4Validator._safe_get_style(driver, '.container', 'width'),
                driver.execute_script("return document.querySelector('.container').offsetWidth")
            )
            main_width_pc = Stage4Validator._parse_px_value(
                Stage4Validator._safe_get_style(driver, '.main-content', 'width')
            )

            if container_width_pc > 0:
                main_ratio = main_width_pc / container_width_pc
                if not (0.55 <= main_ratio <= 0.65):
                    return {
                        'is_passed': False,
                        'msg': f'The width of the main content area on PC should account for 60% (current: {main_ratio:.2%})',
                        'error_type': 'PC端布局比例错误',
                        'score': 0
                    }

            # 3. 检查平板端2列布局（768-1200px）
            driver.set_window_size(1000, 800)
            time.sleep(0.5)

            sidebar_left_display = Stage4Validator._safe_get_style(driver, '.sidebar-left', 'display')
            if sidebar_left_display != 'none':
                return {
                    'is_passed': False,
                    'msg': 'The left sidebar .sidebar-left should be hidden on tablet (768-1200px)',
                    'error_type': '平板端布局错误',
                    'score': 0
                }

            # 主内容区与右侧边栏比例（70% + 30%）
            container_width_tablet = Stage4Validator._parse_px_value(
                Stage4Validator._safe_get_style(driver, '.container', 'width'),
                driver.execute_script("return document.querySelector('.container').offsetWidth")
            )
            main_width_tablet = Stage4Validator._parse_px_value(
                Stage4Validator._safe_get_style(driver, '.main-content', 'width')
            )

            if container_width_tablet > 0:
                main_ratio_tablet = main_width_tablet / container_width_tablet
                if not (0.65 <= main_ratio_tablet <= 0.75):
                    return {
                        'is_passed': False,
                        'msg': f'The width of the main content area on tablet should account for 70% (current: {main_ratio_tablet:.2%})',
                        'error_type': '平板端布局比例错误',
                        'score': 0
                    }

            # 4. 检查移动端1列布局（<768px）
            driver.set_window_size(700, 800)
            time.sleep(0.5)

            container_flex_direction = Stage4Validator._safe_get_style(driver, '.container', 'flexDirection')
            if container_flex_direction != 'column':
                return {
                    'is_passed': False,
                    'msg': 'Flex-direction: column should be set on mobile (<768px) to implement stacked layout',
                    'error_type': '移动端布局错误',
                    'score': 0
                }

            # 修复核心：移动端宽度校验（重新获取移动端容器宽度+兼容多种100%实现方式）
            # 1. 重新获取移动端容器和主内容区的实际渲染宽度（offsetWidth）
            container_width_mobile = driver.execute_script("return document.querySelector('.container').offsetWidth")
            main_width_mobile_actual = driver.execute_script(
                "return document.querySelector('.main-content').offsetWidth")
            # 2. 获取样式中的width值（用于兼容100%字符串）
            main_width_mobile_style = Stage4Validator._safe_get_style(driver, '.main-content', 'width')

            # 调试输出（方便排查）
            print(
                f"【移动端宽度调试】容器实际宽度：{container_width_mobile}px，主内容区实际宽度：{main_width_mobile_actual}px，样式width值：{main_width_mobile_style}")

            # 3. 放宽判断条件：兼容100%字符串、flex:1实现的100%（比例95%-105%）
            is_width_valid = False
            if '100%' in main_width_mobile_style:
                is_width_valid = True
            elif container_width_mobile > 0:
                main_ratio_mobile = main_width_mobile_actual / container_width_mobile
                if 0.95 <= main_ratio_mobile <= 1.05:  # 容错±5%
                    is_width_valid = True

            if not is_width_valid:
                return {
                    'is_passed': False,
                    'msg': f'The width of the main content area on mobile should be set to 100% (current ratio: {main_width_mobile_actual}/{container_width_mobile} = {main_width_mobile_actual / container_width_mobile:.2%})',
                    'error_type': '移动端布局宽度错误',
                    'score': 0
                }

            # 5. 检查导航栏移动端适配（隐藏第4、5个链接）
            nav_link_4_display = Stage4Validator._safe_get_style(driver, '.nav-links a:nth-child(4)', 'display', 'none')
            nav_link_5_display = Stage4Validator._safe_get_style(driver, '.nav-links a:nth-child(5)', 'display', 'none')
            if nav_link_4_display != 'none' or nav_link_5_display != 'none':
                return {
                    'is_passed': False,
                    'msg': 'The 4th and 5th navigation links (Tags, About) should be hidden on mobile',
                    'error_type': '导航栏响应式错误',
                    'score': 0
                }

            # 所有校验通过
            return {
                'is_passed': True,
                'msg': 'Advanced responsive layout completed! Perfect adaptation for PC/tablet/mobile, excellent user experience～',
                'error_type': None,
                'score': 100
            }
        except Exception as e:
            error_msg = f'Responsive validation exception: {str(e)[:50]}'
            print(f"4-1校验异常: {str(e)}")
            return {
                'is_passed': False,
                'msg': error_msg,
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            # 清理临时文件和浏览器
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    @staticmethod
    def validate_4_2(html_code, css_code):
        """关卡4-2：CSS美化与动画校验（终极修复版：hover触发+CSS代码双重校验）"""
        driver = None
        temp_file_path = None
        try:
            driver = Stage4Validator._init_selenium()
            if not driver:
                return {
                    'is_passed': False,
                    'msg': 'Failed to start browser, unable to validate',
                    'error_type': '环境错误',
                    'score': 0
                }

            # 加载HTML并等待渲染
            temp_file_path = Stage4Validator._load_html(driver, html_code, css_code)

            # 检查核心元素
            if not driver.execute_script("return document.querySelector('.card') !== null"):
                return {
                    'is_passed': False,
                    'msg': '.card element not found',
                    'error_type': '元素缺失',
                    'score': 0
                }
            if not driver.execute_script("return document.querySelector('.card-btn') !== null"):
                return {
                    'is_passed': False,
                    'msg': '.card-btn element not found',
                    'error_type': '元素缺失',
                    'score': 0
                }

            # 1. 检查卡片渐变背景（兼容十六进制和RGB格式）
            card_bg = Stage4Validator._safe_get_style(driver, '.card', 'backgroundImage')
            print(f"【渐变背景调试】浏览器返回的backgroundImage值：{card_bg}")

            # 定义目标色值的两种格式（十六进制小写 + RGB）
            target_colors = {
                '3498db': 'rgb(52, 152, 219)',
                '2980b9': 'rgb(41, 128, 185)'
            }
            has_gradient = 'linear-gradient' in card_bg
            has_color1 = (target_colors['3498db'] in card_bg) or ('3498db' in card_bg.lower())
            has_color2 = (target_colors['2980b9'] in card_bg) or ('2980b9' in card_bg.lower())

            if not (has_gradient and has_color1 and has_color2):
                return {
                    'is_passed': False,
                    'msg': 'The card has no gradient background, please add background: linear-gradient(to right, #3498db, #2980b9)',
                    'error_type': '渐变背景错误',
                    'score': 0
                }

            # 2. 检查卡片圆角
            card_radius = Stage4Validator._safe_get_style(driver, '.card', 'borderRadius')
            radius_value = Stage4Validator._parse_px_value(card_radius)
            if not (7 <= radius_value <= 9):  # 容错±1px
                return {
                    'is_passed': False,
                    'msg': f'The card has incorrect rounded corners (got {radius_value}px, required 8px)',
                    'error_type': '圆角设置错误',
                    'score': 0
                }

            # 3. 检查卡片阴影
            card_shadow = Stage4Validator._safe_get_style(driver, '.card', 'boxShadow')
            if 'rgba(0, 0, 0, 0.1)' not in card_shadow and 'rgba(0,0,0,0.1)' not in card_shadow:
                return {
                    'is_passed': False,
                    'msg': 'Incorrect card shadow effect, please add box-shadow: 0 2px 10px rgba(0,0,0,0.1)',
                    'error_type': '阴影设置错误',
                    'score': 0
                }

            # 4. 检查卡片hover上浮效果（终极修复：多事件触发+CSS代码兜底）
            # ===== 步骤1：强制触发hover状态（多事件+多次触发）=====
            driver.execute_script("""
                const card = document.querySelector('.card');
                // 强制移除所有hover相关样式缓存
                card.style.transition = 'none'; // 临时关闭过渡，立即生效
                // 触发所有hover相关事件
                const events = ['mouseenter', 'mouseover', 'pointerover'];
                events.forEach(event => {
                    card.dispatchEvent(new MouseEvent(event, { 
                        bubbles: true, 
                        cancelable: true,
                        view: window,
                        target: card
                    }));
                });
                // 强制重绘元素
                card.offsetHeight; // 触发重绘
            """)
            time.sleep(0.8)  # 进一步延长等待时间，确保样式生效

            # ===== 步骤2：获取渲染后的transform值 =====
            card_transform = Stage4Validator._safe_get_style(driver, '.card', 'transform', 'none')
            print(f"【卡片hover调试】渲染后的transform值：{card_transform}")

            # ===== 步骤3：解析transform值（兼容所有格式）=====
            translateY_value = 0.0
            # 兼容translateY字符串
            if 'translateY' in card_transform:
                translateY_match = re.search(r'translateY\((-?\d+\.?\d*)px\)', card_transform)
                if translateY_match:
                    translateY_value = float(translateY_match.group(1))
            # 兼容matrix/matrix3d格式
            elif 'matrix' in card_transform and card_transform != 'none':
                transform_values = re.findall(r'\((.*?)\)', card_transform)[0].split(',')
                if len(transform_values) >= 6:  # matrix
                    translateY_value = Stage4Validator._parse_px_value(transform_values[5].strip(), 0)
                elif len(transform_values) >= 13:  # matrix3d
                    translateY_value = Stage4Validator._parse_px_value(transform_values[13].strip(), 0)

            # ===== 步骤4：CSS代码兜底校验（关键：即使渲染异常，代码正确也通过）=====
            css_has_hover_translate = False
            # 正则匹配.card:hover中的translateY(-5px)（容错：±1px，空格，小数）
            hover_pattern = r'\.card\s*:\s*hover\s*\{[^}]*transform\s*:\s*[^;]*translateY\(\s*-?(\d+\.?\d*)\s*px\s*\)[^;]*[;}]'
            css_match = re.search(hover_pattern, css_code, re.IGNORECASE | re.DOTALL)
            if css_match:
                css_translate_value = float(css_match.group(1))
                # 校验CSS代码中的值是否在4-6px之间（向上为负）
                if 4 <= abs(css_translate_value) <= 6:
                    css_has_hover_translate = True
                    print(f"【CSS代码兜底】检测到.card:hover中包含translateY({css_translate_value}px)，符合要求")

            # ===== 最终上浮效果判定（渲染值有效 或 CSS代码有效 即可）=====
            is_float_valid = (-6.0 <= translateY_value <= -4.0) or css_has_hover_translate
            if not is_float_valid:
                return {
                    'is_passed': False,
                    'msg': f'The card hover does not achieve the 5px upward floating effect (got {translateY_value}px, expected -5px ±1px). CSS code check: {"passed" if css_has_hover_translate else "failed"}',
                    'error_type': 'hover上浮效果错误',
                    'score': 0
                }

            # 5. 检查按钮hover动画
            driver.execute_script("""
                const btn = document.querySelector('.card-btn');
                btn.style.transition = 'none';
                const events = ['mouseenter', 'mouseover'];
                events.forEach(event => {
                    btn.dispatchEvent(new MouseEvent(event, { bubbles: true }));
                });
                btn.offsetHeight; // 强制重绘
            """)
            time.sleep(0.3)

            btn_bg = Stage4Validator._safe_get_style(driver, '.card-btn', 'backgroundColor')
            # 兼容rgb/rgba格式（容错：允许小范围色值偏差）
            btn_bg_valid = False
            if 'rgb(241, 196, 15)' in btn_bg or 'rgba(241, 196, 15' in btn_bg:
                btn_bg_valid = True
            # CSS代码兜底校验按钮背景色
            btn_css_pattern = r'\.card-btn\s*:\s*hover\s*\{[^}]*background(?:-color)?\s*:\s*[^;]*#f1c40f[^;]*[;}]'
            if re.search(btn_css_pattern, css_code, re.IGNORECASE | re.DOTALL):
                btn_bg_valid = True

            if not btn_bg_valid:
                return {
                    'is_passed': False,
                    'msg': f'Incorrect background color for button hover (got {btn_bg}, required #f1c40f)',
                    'error_type': '按钮hover背景色错误',
                    'score': 0
                }

            # 检查按钮缩放（CSS代码兜底）
            btn_transform = Stage4Validator._safe_get_style(driver, '.card-btn', 'transform', 'none')
            scale_value = 1.0
            if 'scale' in btn_transform:
                scale_match = re.search(r'scale\(\s*(\d+\.?\d*)\s*\)', btn_transform)
                if scale_match:
                    scale_value = float(scale_match.group(1))
            # CSS代码兜底
            btn_scale_pattern = r'\.card-btn\s*:\s*hover\s*\{[^}]*transform\s*:\s*[^;]*scale\(\s*(1\.0[456]|\d+\.?\d*)\s*\)[^;]*[;}]'
            css_has_btn_scale = re.search(btn_scale_pattern, css_code, re.IGNORECASE | re.DOTALL) is not None

            is_scale_valid = (scale_value >= 1.04) or css_has_btn_scale
            if not is_scale_valid:
                return {
                    'is_passed': False,
                    'msg': f'The button hover does not achieve the 1.05 scaling effect (got {scale_value})',
                    'error_type': '按钮hover缩放效果错误',
                    'score': 0
                }

            # 6. 检查过渡动画（CSS代码兜底）
            card_transition_valid = '0.3s' in Stage4Validator._safe_get_style(driver, '.card', 'transition')
            btn_transition_valid = '0.3s' in Stage4Validator._safe_get_style(driver, '.card-btn', 'transition')
            # CSS代码兜底
            css_transition_pattern = r'\.(card|card-btn)\s*\{[^}]*transition\s*:\s*[^;]*0\.3s[^;]*[;}]'
            css_has_transition = re.search(css_transition_pattern, css_code, re.IGNORECASE | re.DOTALL) is not None

            if not (card_transition_valid and btn_transition_valid) and not css_has_transition:
                return {
                    'is_passed': False,
                    'msg': 'Cards and buttons have no transition animation, please add transition: all 0.3s ease',
                    'error_type': '过渡动画错误',
                    'score': 0
                }

            # 所有校验通过
            return {
                'is_passed': True,
                'msg': 'CSS beautification and animation effects are perfect! Gradients, shadows, and hover animations all meet requirements, excellent visual experience～',
                'error_type': None,
                'score': 100
            }
        except Exception as e:
            error_msg = f'Beautification and animation validation exception: {str(e)[:50]}'
            print(f"4-2校验异常: {str(e)}")
            return {
                'is_passed': False,
                'msg': error_msg,
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            # 清理资源
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    @staticmethod
    def validate_4_3(html_code, css_code):
        """关卡4-3：综合项目（个人博客首页）校验（最终优化版）"""
        driver = None
        temp_file_path = None
        try:
            driver = Stage4Validator._init_selenium()
            if not driver:
                return {
                    'is_passed': False,
                    'msg': 'Failed to start browser, unable to validate',
                    'error_type': '环境错误',
                    'score': 0
                }

            # 加载HTML并等待渲染
            temp_file_path = Stage4Validator._load_html(driver, html_code, css_code)

            # 综合项目采用评分制（0-100分）
            score = 0
            feedback = []

            # 1. 语义化HTML结构（20分）- 优化：放宽header判断（允许header包裹nav）
            semantic_tags = ['header', 'nav', 'main', 'aside', 'footer', 'article']
            missing_semantic = []
            for tag in semantic_tags:
                if not driver.execute_script(f"return document.querySelector('{tag}') !== null"):
                    missing_semantic.append(tag)
            if not missing_semantic:
                score += 20
                feedback.append('Complete semantic structure (20 points)')
            else:
                score += max(0, 20 - len(missing_semantic) * 4)
                feedback.append(
                    f'Missing semantic tags: {", ".join(missing_semantic)} ({max(0, 20 - len(missing_semantic) * 4)} points)')

            # 2. Flex+Grid混合布局（25分）- 保持不变
            has_flex = False
            has_grid = False
            try:
                all_displays = driver.execute_script("""
                    return Array.from(document.getElementsByTagName('*')).map(el => getComputedStyle(el).display);
                """)
                has_flex = 'flex' in all_displays
                has_grid = 'grid' in all_displays
            except:
                pass

            if has_flex and has_grid:
                score += 15
                feedback.append('Correct use of Flex+Grid hybrid layout (15 points)')
            else:
                score += (10 if has_flex or has_grid else 0)
                feedback.append(
                    f'{"Only Flex" if has_flex else "Only Grid" if has_grid else "No Flex/Grid"} ({10 if has_flex or has_grid else 0} points)')

            # 3. 主内容区居中（10分）- 优化：兼容多种居中方式
            main_center = False
            try:
                main_center = driver.execute_script("""
                    const main = document.querySelector('main') || document.querySelector('.article-list') || document.body;
                    const style = getComputedStyle(main);
                    // 兼容margin:auto、text-align:center、父容器居中三种方式
                    const ml = parseInt(style.marginLeft);
                    const mr = parseInt(style.marginRight);
                    const parent = main.parentElement;
                    const parentStyle = getComputedStyle(parent);
                    const isMarginAuto = (ml === mr && ml >= 0);
                    const isTextAlignCenter = style.textAlign === 'center';
                    const isParentCentered = parentStyle.marginLeft === 'auto' && parentStyle.marginRight === 'auto';
                    return isMarginAuto || isTextAlignCenter || isParentCentered;
                """)
            except:
                pass
            if main_center:
                score += 10
                feedback.append('Main content area horizontally centered (10 points)')
            else:
                feedback.append('Main content area not horizontally centered (0 points)')

            # 4. 响应式适配（25分）- 优化：兼容Grid/Flex响应式，放宽PC端宽度判断
            pc_valid = False
            mobile_valid = False
            try:
                # PC端：放宽判断（>1100px即可，兼容max-width:1200px）
                driver.set_window_size(1400, 800)
                time.sleep(0.5)
                pc_valid = driver.execute_script("""
                    const container = document.querySelector('.container') || document.body;
                    return container.offsetWidth > 1100; // 从1200→1100
                """)

                # 移动端：兼容Grid/Flex/Block响应式
                driver.set_window_size(700, 800)
                time.sleep(0.5)
                mobile_valid = driver.execute_script("""
                    const container = document.querySelector('.container') || document.body;
                    const style = getComputedStyle(container);
                    // 兼容flex-column、grid 1fr、display:block三种情况
                    return style.flexDirection === 'column' || 
                           style.gridTemplateColumns === '1fr' || 
                           style.display === 'block' ||
                           (style.gridTemplateColumns && style.gridTemplateColumns.indexOf('1fr') > -1);
                """)
            except:
                pass

            if pc_valid and mobile_valid:
                score += 25
                feedback.append('Perfect responsive adaptation (25 points)')
            elif pc_valid or mobile_valid:
                score += 15
                feedback.append(f'{"Only PC" if pc_valid else "Only mobile"} adaptation correct (15 points)')
            else:
                feedback.append('Responsive adaptation not implemented (0 points)')

            # 5. CSS美化与动画（20分）- 保持不变
            has_beautiful = False
            has_animation = False
            try:
                has_beautiful = driver.execute_script("""
                    return Array.from(document.getElementsByTagName('*')).some(el => {
                        const style = getComputedStyle(el);
                        return style.backgroundImage !== 'none' || style.boxShadow !== 'none' || style.borderRadius !== '0px';
                    });
                """)
                has_animation = driver.execute_script("""
                    return Array.from(document.getElementsByTagName('*')).some(el => {
                        const style = getComputedStyle(el);
                        return style.transition !== 'none' || style.animation !== 'none';
                    });
                """)
            except:
                pass

            if has_beautiful and has_animation:
                score += 20
                feedback.append('Excellent CSS beautification and animation (20 points)')
            elif has_beautiful or has_animation:
                score += 10
                feedback.append(f'{"Only beautification" if has_beautiful else "Only animation"} (10 points)')
            else:
                feedback.append('No CSS beautification/animation (0 points)')

            # 6. 文本样式可读性（10分）- 优化：放宽颜色判断，兼容更多合规颜色
            text_valid = False
            try:
                text_valid = driver.execute_script("""
                    const p = document.querySelector('p') || document.querySelector('.post h2') || document.querySelector('div');
                    if (!p) return false;
                    const fs = parseInt(getComputedStyle(p).fontSize);
                    const lh = parseFloat(getComputedStyle(p).lineHeight);
                    const color = getComputedStyle(p).color;
                    // 优化：颜色只要不是纯白/纯黑即可，字号14-20px，行高1.4-1.9
                    return fs >=14 && fs <=20 && lh >=1.4 && lh <=1.9 && 
                           color !== 'rgb(255,255,255)' && color !== 'rgb(0,0,0)' &&
                           color !== '#ffffff' && color !== '#000000';
                """)
            except:
                pass
            if text_valid:
                score += 10
                feedback.append('Excellent text readability (10 points)')
            else:
                feedback.append('Poor text readability (0 points)')

            # 最终判定
            is_passed = score >= 60
            final_msg = f'Comprehensive project score: {score} points! {"Passed!" if is_passed else "Not up to standard!"}\nScoring details: ' + ' | '.join(
                feedback)

            return {
                'is_passed': is_passed,
                'msg': final_msg,
                'error_type': None if is_passed else '综合项目未达标',
                'score': score
            }
        except Exception as e:
            error_msg = f'Comprehensive project validation exception: {str(e)[:50]}'
            print(f"4-3校验异常: {str(e)}")
            return {
                'is_passed': False,
                'msg': error_msg,
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            # 清理资源
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            if driver:
                try:
                    driver.quit()
                except:
                    pass

# 测试入口（可选）
if __name__ == '__main__':
    def test_validation(level, html_file, css_file):
        import os
        if not os.path.exists(html_file) or not os.path.exists(css_file):
            print(f"[{level}] 测试文件缺失：{html_file} / {css_file}")
            return
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()
            with open(css_file, 'r', encoding='utf-8') as f:
                css = f.read()
            result = Stage4Validator.validate(level, html, css)
            print(f"\n[{level}] 校验结果：")
            print(f"  是否通过：{result['is_passed']}")
            print(f"  提示信息：{result['msg']}")
            print(f"  错误类型：{result['error_type']}")
            print(f"  得分：{result['score']}")
        except Exception as e:
            print(f"[{level}] 测试失败：{str(e)}")

    # test_validation('4-1', '4-1.html', '4-1.css')
    # test_validation('4-2', '4-2.html', '4-2.css')
    # test_validation('4-3', '4-3.html', '4-3.css')
