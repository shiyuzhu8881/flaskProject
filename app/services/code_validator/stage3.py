"""阶段3校验逻辑：Flexbox、Grid、浮动布局（匹配default_levels.json）"""
import cssutils
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Stage3Validator:
    @staticmethod
    def validate(level_id, html_code, css_code):
        """阶段3统一校验入口（匹配JSON：3-1/3-2/3-3）"""
        if level_id == '3-1':
            return Stage3Validator.validate_3_1(html_code, css_code)
        elif level_id == '3-2':
            return Stage3Validator.validate_3_2(html_code, css_code)
        elif level_id == '3-3':
            return Stage3Validator.validate_3_3(html_code, css_code)
        else:
            return {
                'is_passed': False,
                'msg': '阶段3关卡ID错误',
                'error_type': '系统错误',
                'score': 0
            }

    @staticmethod
    def _init_selenium():
        """初始化无头浏览器"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            return None

    @staticmethod
    def validate_3_1(html_code, css_code):
        """关卡3-1：Flexbox基础布局（匹配JSON task：导航栏水平居中+15px间距+移动端换行）"""
        driver = Stage3Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': '无法启动浏览器，无法校验Flex布局',
                'error_type': '环境错误',
                'score': 0
            }

        try:
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{full_html}")

            # 1. 检查Flex布局启用（JSON task要求）
            nav_display = driver.execute_script("""
                return getComputedStyle(document.querySelector('.nav-container')).display;
            """)
            if nav_display != 'flex':
                return {
                    'is_passed': False,
                    'msg': '.nav-container未启用Flex布局（JSON要求：display:flex）',
                    'error_type': 'Flex布局未启用',
                    'score': 0
                }

            # 2. 检查水平居中（justify-content: center，JSON task要求）
            justify_content = driver.execute_script("""
                return getComputedStyle(document.querySelector('.nav-container')).justifyContent;
            """)
            if justify_content != 'center':
                return {
                    'is_passed': False,
                    'msg': '导航栏链接未水平居中（JSON要求：justify-content:center）',
                    'error_type': 'Flex水平对齐错误',
                    'score': 0
                }

            # 3. 检查垂直居中（align-items: center，JSON task要求）
            align_items = driver.execute_script("""
                return getComputedStyle(document.querySelector('.nav-container')).alignItems;
            """)
            if align_items != 'center':
                return {
                    'is_passed': False,
                    'msg': '导航栏链接未垂直居中（JSON要求：align-items:center）',
                    'error_type': 'Flex垂直对齐错误',
                    'score': 0
                }

            # 4. 检查链接间距（gap:15px，JSON task要求）
            gap = driver.execute_script("""
                return getComputedStyle(document.querySelector('.nav-container')).gap;
            """)
            if gap != '15px':
                return {
                    'is_passed': False,
                    'msg': '导航栏链接间距错误（JSON要求：gap:15px）',
                    'error_type': 'Flex间距错误',
                    'score': 0
                }

            # 5. 检查移动端自动换行（<768px，JSON task要求）
            driver.set_window_size(700, 600)
            flex_wrap = driver.execute_script("""
                return getComputedStyle(document.querySelector('.nav-container')).flexWrap;
            """)
            if flex_wrap != 'wrap':
                return {
                    'is_passed': False,
                    'msg': '移动端导航栏未自动换行（JSON要求：flex-wrap:wrap）',
                    'error_type': 'Flex响应式错误',
                    'score': 0
                }

            return {
                'is_passed': True,
                'msg': 'Flexbox导航栏布局完美！匹配JSON 3-1要求～',
                'error_type': None,
                'score': 100
            }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'Flexbox校验异常：{str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

    @staticmethod
    def validate_3_2(html_code, css_code):
        """关卡3-2：Grid复杂布局（匹配JSON task：3列/2列/1列响应式+15px间距+垂直居中）"""
        driver = Stage3Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': '无法启动浏览器，无法校验Grid布局',
                'error_type': '环境错误',
                'score': 0
            }

        try:
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{full_html}")

            # 1. 检查Grid布局启用（JSON task要求）
            grid_display = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-container')).display;
            """)
            if grid_display != 'grid':
                return {
                    'is_passed': False,
                    'msg': '.card-container未启用Grid布局（JSON要求：display:grid）',
                    'error_type': 'Grid布局未启用',
                    'score': 0
                }

            # 2. 检查PC端3列等宽（>1200px，JSON task要求）
            driver.set_window_size(1400, 800)
            grid_columns = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-container')).gridTemplateColumns;
            """)
            if not (grid_columns == '1fr 1fr 1fr' or grid_columns == '33.333% 33.333% 33.333%'):
                return {
                    'is_passed': False,
                    'msg': 'PC端未实现3列等宽（JSON要求：grid-template-columns: repeat(3, 1fr)）',
                    'error_type': 'Grid列数错误',
                    'score': 0
                }

            # 3. 检查卡片间距（15px，JSON task要求）
            gap = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-container')).gap;
            """)
            if gap != '15px':
                return {
                    'is_passed': False,
                    'msg': '卡片间距错误（JSON要求：gap:15px）',
                    'error_type': 'Grid间距错误',
                    'score': 0
                }

            # 4. 检查平板端2列（768-1200px，JSON task要求）
            driver.set_window_size(1000, 800)
            tablet_columns = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-container')).gridTemplateColumns;
            """)
            if not (tablet_columns == '1fr 1fr' or tablet_columns == '50% 50%'):
                return {
                    'is_passed': False,
                    'msg': '平板端未实现2列布局（JSON要求：768-1200px显示2列）',
                    'error_type': 'Grid平板端响应式错误',
                    'score': 0
                }

            # 5. 检查移动端1列（<768px，JSON task要求）
            driver.set_window_size(700, 800)
            mobile_columns = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-container')).gridTemplateColumns;
            """)
            if not (mobile_columns == '1fr' or mobile_columns == '100%'):
                return {
                    'is_passed': False,
                    'msg': '移动端未实现1列布局（JSON要求：<768px显示1列）',
                    'error_type': 'Grid移动端响应式错误',
                    'score': 0
                }

            return {
                'is_passed': True,
                'msg': 'Grid响应式卡片布局完成！匹配JSON 3-2要求～',
                'error_type': None,
                'score': 100
            }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'Grid布局校验异常：{str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()

    @staticmethod
    def validate_3_3(html_code, css_code):
        """关卡3-3：Float&清除浮动（匹配JSON task：左图右文+10px间距+清除浮动）"""
        driver = Stage3Validator._init_selenium()
        if not driver:
            return {
                'is_passed': False,
                'msg': '无法启动浏览器，无法校验浮动布局',
                'error_type': '环境错误',
                'score': 0
            }

        try:
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{full_html}")

            # 1. 检查图片左浮动（JSON task要求）
            img_float = driver.execute_script("""
                return getComputedStyle(document.querySelector('.article-img')).float;
            """)
            if img_float != 'left':
                return {
                    'is_passed': False,
                    'msg': '图片未设置左浮动（JSON要求：float:left）',
                    'error_type': '浮动设置错误',
                    'score': 0
                }

            # 2. 检查图片与文本间距（10px，JSON task要求）
            img_margin = driver.execute_script("""
                return getComputedStyle(document.querySelector('.article-img')).marginRight;
            """)
            if img_margin != '10px':
                return {
                    'is_passed': False,
                    'msg': '图片与文本间距错误（JSON要求：margin-right:10px）',
                    'error_type': '浮动元素间距错误',
                    'score': 0
                }

            # 3. 检查清除浮动（修复父容器高度塌陷，JSON task要求）
            parent_height = driver.execute_script("""
                return document.querySelector('.article-container').offsetHeight;
            """)
            img_height = driver.execute_script("""
                return parseInt(getComputedStyle(document.querySelector('.article-img')).height);
            """)
            if parent_height <= img_height:
                return {
                    'is_passed': False,
                    'msg': '父容器高度塌陷（JSON要求：清除浮动，如overflow:hidden）',
                    'error_type': '浮动未清除',
                    'score': 0
                }

            return {
                'is_passed': True,
                'msg': '浮动布局实现成功！匹配JSON 3-3要求～',
                'error_type': None,
                'score': 100
            }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'浮动布局校验异常：{str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            driver.quit()