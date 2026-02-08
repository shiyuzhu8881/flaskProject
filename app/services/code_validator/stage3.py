"""阶段3校验逻辑：Flexbox、Grid、浮动布局（最终修复版）"""
import re
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, JavascriptException, TimeoutException

class Stage3Validator:
    @staticmethod
    def validate(level_id, html_code, css_code):
        """阶段3统一校验入口"""
        if level_id not in ['3-1', '3-2', '3-3']:
            return {
                'is_passed': False,
                'msg': 'Stage 3 level ID error (only support 3-1/3-2/3-3)',
                'error_type': '系统错误',
                'score': 0
            }

        driver = Stage3Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': 'Failed to start the browser, unable to validate layout',
                'error_type': '环境错误',
                'score': 0
            }

        try:
            # 核心修复1：简化HTML拼接，不提取body（避免标签丢失）
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
            # 核心修复2：使用临时文件加载（替代data:text/html，解决渲染延迟）
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(full_html)
                temp_file_path = f.name
            driver.get(f"file://{temp_file_path}")
            # 核心修复3：延长渲染等待时间（关键！）
            time.sleep(1)
            driver.implicitly_wait(3)

            validate_func = {
                '3-1': Stage3Validator.validate_3_1,
                '3-2': Stage3Validator.validate_3_2,
                '3-3': Stage3Validator.validate_3_3
            }[level_id]
            result = validate_func(driver)

            # 删除临时文件
            os.unlink(temp_file_path)
            return result

        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'Validation exception: {str(e)[:100]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            try:
                driver.quit()
            except:
                pass

    @staticmethod
    def _init_selenium():
        """初始化无头浏览器（修复渲染问题）"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        # 核心修复4：启用图片加载（避免布局渲染异常）
        # chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript-harmony-shipping')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_setting_values.popups': 2
        }
        chrome_options.add_experimental_option('prefs', prefs)

        max_retries = 3
        for retry in range(max_retries):
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.implicitly_wait(5)
                driver.set_page_load_timeout(20)
                driver.set_script_timeout(10)
                return driver
            except Exception as e:
                if retry == max_retries - 1:
                    print(f"浏览器初始化失败: {str(e)}")
                continue
        return None

    @staticmethod
    def _set_viewport_size(driver, width, height):
        """精准设置视口尺寸"""
        driver.set_window_size(width + 15, height + 15)
        driver.execute_script(f"""
            document.documentElement.style.width = '{width}px';
            document.documentElement.style.height = '{height}px';
            window.innerWidth = {width};
            window.innerHeight = {height};
            document.body.offsetHeight;
        """)
        time.sleep(0.5)

    @staticmethod
    def _camel_to_kebab(prop_name):
        """驼峰式转连字符"""
        if not prop_name:
            return ''
        return re.sub(r'(?<!^)(?=[A-Z])', '-', prop_name).lower()

    @staticmethod
    def _get_computed_style(driver, selector, property_name, fallback=''):
        """安全获取元素样式"""
        try:
            kebab_prop = Stage3Validator._camel_to_kebab(property_name)
            base_props = [property_name, kebab_prop]
            webkit_props = [f'-webkit-{p}' for p in base_props]
            all_props = base_props + webkit_props
            unique_props = list(set(all_props))
            props_json = json.dumps(unique_props)

            escaped_selector = selector.replace('"', '\\"').replace("'", "\\'")
            js = f"""
                const el = document.querySelector("{escaped_selector}");
                if (!el) return "";
                const style = getComputedStyle(el);
                const props = {props_json};
                for (const prop of props) {{
                    let value = style.getPropertyValue(prop) || style[prop];
                    if (value) return value.trim();
                }}
                return "";
            """
            result = driver.execute_script(js).strip()
            return result if result else fallback
        except Exception:
            return fallback

    @staticmethod
    def _check_element_exists(driver, selector):
        """核心修复5：降低元素检查门槛（只检查存在性，不检查可见性）"""
        try:
            escaped_selector = selector.replace('"', '\\"').replace("'", "\\'")
            return driver.execute_script(f"""
                const el = document.querySelector("{escaped_selector}");
                return el !== null; // 只检查元素是否存在，不检查可见性
            """)
        except:
            return False

    @staticmethod
    def _parse_px_value(px_str):
        """解析px值为数字"""
        try:
            if not px_str or 'px' not in px_str:
                return 0.0
            num_str = re.search(r'-?\d+(\.\d+)?', px_str).group()
            return float(num_str)
        except:
            return 0.0

    @staticmethod
    def validate_3_1(driver):
        """3-1 Flex导航栏校验（核心修复：调整逻辑顺序+降低校验门槛）"""
        total_score = 100
        error_list = []
        score_deduction = 20

        # 1. 检查元素是否存在（仅检查存在性）
        if not Stage3Validator._check_element_exists(driver, '.nav-container'):
            return {
                'is_passed': False,
                'msg': '.nav-container element not found in HTML',
                'error_type': '元素缺失',
                'score': 0
            }

        # 2. 检查Flex布局启用（优先检查，即使元素尺寸为0也能检测）
        nav_display = Stage3Validator._get_computed_style(driver, '.nav-container', 'display')
        valid_display = ['flex', '-webkit-flex']
        if nav_display not in valid_display:
            error_list.append('.nav-container has not enabled Flex layout (display: flex required)')
            total_score -= score_deduction

        # 3. 检查水平居中（使用连字符属性名，兼容更多情况）
        justify_content = Stage3Validator._get_computed_style(driver, '.nav-container', 'justify-content')
        valid_justify = ['center', '-webkit-center']
        if not any(v in justify_content for v in valid_justify):
            error_list.append('Navigation bar links are not horizontally centered (justify-content: center required)')
            total_score -= score_deduction

        # 4. 检查垂直居中
        align_items = Stage3Validator._get_computed_style(driver, '.nav-container', 'align-items')
        valid_align = ['center', '-webkit-center']
        if not any(v in align_items for v in valid_align):
            error_list.append('Navigation bar links are not vertically centered (align-items: center required)')
            total_score -= score_deduction

        # 5. 检查链接间距（容错±2px）
        gap = Stage3Validator._get_computed_style(driver, '.nav-container', 'gap')
        gap_value = Stage3Validator._parse_px_value(gap)
        link_margin = driver.execute_script("""
            const links = document.querySelectorAll('.nav-link');
            if (links.length < 2) return '0px';
            return getComputedStyle(links[0]).marginRight || getComputedStyle(links[0]).marginLeft;
        """)
        margin_value = Stage3Validator._parse_px_value(link_margin)
        if not (13 <= gap_value <= 17) and not (13 <= margin_value <= 17):
            error_list.append('Incorrect spacing between navigation bar links (gap: 15px required)')
            total_score -= score_deduction

        # 6. 检查移动端换行（简化检查逻辑）
        original_size = driver.get_window_size()
        try:
            Stage3Validator._set_viewport_size(driver, 700, 600)
            flex_wrap = Stage3Validator._get_computed_style(driver, '.nav-container', 'flex-wrap')
            valid_wrap = ['wrap', '-webkit-wrap']
            if flex_wrap not in valid_wrap:
                # 兜底检查：只检查CSS规则，不依赖渲染
                has_wrap_in_css = driver.execute_script("""
                    const sheets = document.styleSheets;
                    for (let sheet of sheets) {
                        try {
                            for (let rule of sheet.cssRules) {
                                if (rule.type === CSSRule.MEDIA_RULE && rule.media.mediaText.includes('max-width: 768px')) {
                                    for (let subRule of rule.cssRules) {
                                        if (subRule.selectorText && subRule.selectorText.includes('.nav-container') && 
                                            (subRule.style.flexWrap === 'wrap' || subRule.style.flexWrap === '-webkit-wrap')) {
                                            return true;
                                        }
                                    }
                                }
                            }
                        } catch (e) { continue; }
                    }
                    return false;
                """)
                if not has_wrap_in_css:
                    error_list.append('Mobile navigation bar does not wrap automatically (flex-wrap: wrap required in @media <768px)')
                    total_score -= score_deduction
        finally:
            driver.set_window_size(original_size['width'], original_size['height'])

        is_passed = len(error_list) == 0
        total_score = max(total_score, 0)
        return {
            'is_passed': is_passed,
            'msg': 'Flexbox navigation bar layout validation passed!' if is_passed else f'Errors: {" | ".join(error_list)}',
            'error_type': None if is_passed else 'Flex布局错误',
            'score': total_score
        }

    @staticmethod
    def validate_3_2(driver):
        """3-2 Grid卡片布局校验（终极修复版：按列数校验，兼容所有值格式）"""
        if not Stage3Validator._check_element_exists(driver, '.card-container'):
            return {'is_passed': False, 'msg': '.card-container element not found in HTML', 'error_type': '元素缺失',
                    'score': 0}

        # 1. 检查Grid布局启用
        grid_display = Stage3Validator._get_computed_style(driver, '.card-container', 'display')
        if grid_display not in ['grid', '-webkit-grid']:
            return {'is_passed': False, 'msg': '.card-container has not enabled Grid layout',
                    'error_type': 'Grid布局未启用', 'score': 0}

        # 2. 检查垂直居中
        align_items = Stage3Validator._get_computed_style(driver, '.card-container', 'align-items')
        if align_items not in ['center', '-webkit-center']:
            return {'is_passed': False, 'msg': 'Card content is not vertically centered',
                    'error_type': 'Grid垂直对齐错误', 'score': 0}

        # 3. 检查间距（容错±1px）
        gap = Stage3Validator._get_computed_style(driver, '.card-container', 'gap')
        gap_value = Stage3Validator._parse_px_value(gap)
        if not (14 <= gap_value <= 16):
            return {'is_passed': False, 'msg': f'Incorrect card spacing (gap: {gap_value}px, required 15px ±1px)',
                    'error_type': 'Grid间距错误', 'score': 0}

        # 4. 检查响应式列数（终极修复：统计列数，兼容所有值格式）
        original_size = driver.get_window_size()
        try:
            # 辅助函数：统计grid列数
            def get_grid_col_count(driver, selector):
                col_str = Stage3Validator._get_computed_style(driver, selector, 'grid-template-columns')
                # 拆分列值并过滤空值（处理多个空格的情况）
                col_list = [col.strip() for col in col_str.split() if col.strip()]
                return len(col_list), col_str

            # PC端（>1200px）：3列校验
            Stage3Validator._set_viewport_size(driver, 1400, 800)
            time.sleep(1)
            pc_col_count, pc_col_str = get_grid_col_count(driver, '.card-container')
            print(f"【调试】PC端列数：{pc_col_count}，列值：{pc_col_str}")
            if pc_col_count != 3:
                return {
                    'is_passed': False,
                    'msg': f'3 equal columns are not implemented on PC (got {pc_col_count} columns, value: {pc_col_str})',
                    'error_type': 'Grid列数错误',
                    'score': 0
                }

            # 平板端（768-1200px）：2列校验
            Stage3Validator._set_viewport_size(driver, 1000, 800)
            time.sleep(1)
            tablet_col_count, tablet_col_str = get_grid_col_count(driver, '.card-container')
            print(f"【调试】平板端列数：{tablet_col_count}，列值：{tablet_col_str}")
            if tablet_col_count != 2:
                return {
                    'is_passed': False,
                    'msg': f'2-column layout is not implemented on tablet (got {tablet_col_count} columns, value: {tablet_col_str})',
                    'error_type': 'Grid平板端响应式错误',
                    'score': 0
                }

            # 移动端（<768px）：1列校验
            Stage3Validator._set_viewport_size(driver, 700, 800)
            time.sleep(1)
            mobile_col_count, mobile_col_str = get_grid_col_count(driver, '.card-container')
            print(f"【调试】移动端列数：{mobile_col_count}，列值：{mobile_col_str}")
            if mobile_col_count != 1:
                return {
                    'is_passed': False,
                    'msg': f'1-column layout is not implemented on mobile (got {mobile_col_count} columns, value: {mobile_col_str})',
                    'error_type': 'Grid移动端响应式错误',
                    'score': 0
                }
        finally:
            driver.set_window_size(original_size['width'], original_size['height'])

        return {'is_passed': True, 'msg': 'Grid responsive card layout validation passed!', 'error_type': None,
                'score': 100}

    @staticmethod
    def validate_3_3(driver):
        """3-3 浮动布局校验"""
        required_elements = ['.article-container', '.article-img']
        if not all(Stage3Validator._check_element_exists(driver, sel) for sel in required_elements):
            return {'is_passed': False, 'msg': '.article-container or .article-img element not found in HTML', 'error_type': '元素缺失', 'score': 0}

        img_float = Stage3Validator._get_computed_style(driver, '.article-img', 'float')
        if img_float != 'left':
            return {'is_passed': False, 'msg': 'Image is not set to float left', 'error_type': '浮动设置错误', 'score': 0}

        img_width = Stage3Validator._get_computed_style(driver, '.article-img', 'width')
        width_num = Stage3Validator._parse_px_value(img_width)
        if not (299 <= width_num <= 301):
            return {'is_passed': False, 'msg': f'Image width is {width_num}px (required 300px ±1px)', 'error_type': '浮动元素宽度错误', 'score': 0}

        img_margin_right = Stage3Validator._get_computed_style(driver, '.article-img', 'margin-right')
        margin_num = Stage3Validator._parse_px_value(img_margin_right)
        if not (9 <= margin_num <= 11):
            return {'is_passed': False, 'msg': f'Image margin-right is {margin_num}px (required 10px ±1px)', 'error_type': '浮动元素间距错误', 'score': 0}

        parent_overflow = Stage3Validator._get_computed_style(driver, '.article-container', 'overflow')
        has_clearfix = driver.execute_script("""
            const el = document.querySelector('.article-container');
            const style = getComputedStyle(el, '::after');
            return style.display === 'block' && (style.clear === 'both' || style.clear === 'left');
        """)
        parent_height = driver.execute_script("return document.querySelector('.article-container').offsetHeight || 0")
        img_height = driver.execute_script("return document.querySelector('.article-img').offsetHeight || 0")

        is_clear_fix = (
            parent_overflow in ['hidden', 'auto', 'scroll'] or
            has_clearfix or
            parent_height > img_height + 5
        )
        if not is_clear_fix:
            return {'is_passed': False, 'msg': 'Parent container height collapse (float not cleared)', 'error_type': '浮动未清除', 'score': 0}

        return {'is_passed': True, 'msg': 'Float layout validation passed!', 'error_type': None, 'score': 100}

if __name__ == '__main__':
    """测试入口"""
    import os
    def test_validation(level, html_file, css_file):
        if not os.path.exists(html_file) or not os.path.exists(css_file):
            print(f"[{level}] 测试文件缺失：{html_file} / {css_file}")
            return
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()
            with open(css_file, 'r', encoding='utf-8') as f:
                css = f.read()
            result = Stage3Validator.validate(level, html, css)
            print(f"\n[{level}] 校验结果：")
            print(f"  是否通过：{result['is_passed']}")
            print(f"  提示信息：{result['msg']}")
            print(f"  错误类型：{result['error_type']}")
            print(f"  得分：{result['score']}")
        except Exception as e:
            print(f"[{level}] 测试失败：{str(e)}")

    test_validation('3-1', '3-1.html', '3-1.css')
    test_validation('3-2', '3-2.html', '3-2.css')
    test_validation('3-3', '3-3.html', '3-3.css')
