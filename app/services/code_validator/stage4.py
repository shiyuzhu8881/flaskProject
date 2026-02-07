"""阶段4校验逻辑：响应式进阶、CSS美化与动画、综合项目"""
import cssutils
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
                'msg': '阶段4关卡ID错误',
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
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    @staticmethod
    def validate_4_1(html_code, css_code):
        """关卡4-1：响应式设计进阶校验"""
        driver = None
        try:
            driver = Stage4Validator._init_selenium()
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{full_html}")

            # 1. 检查PC端3列布局（>1200px）
            driver.set_window_size(1400, 800)
            container_display = driver.execute_script("""
                return getComputedStyle(document.querySelector('.container')).display;
            """)
            if container_display != 'flex':
                return {
                    'is_passed': False,
                    'msg': '容器.container未启用Flex布局，无法实现多列响应式',
                    'error_type': '响应式布局未启用',
                    'score': 0
                }
            # 检查3列宽度分配（20% + 60% + 20%）
            sidebar_left_width = driver.execute_script("""
                return getComputedStyle(document.querySelector('.sidebar-left')).width;
            """)
            main_width = driver.execute_script("""
                return getComputedStyle(document.querySelector('.main-content')).width;
            """)
            sidebar_right_width = driver.execute_script("""
                return getComputedStyle(document.querySelector('.sidebar-right')).width;
            """)
            container_width = driver.execute_script("""
                return getComputedStyle(document.querySelector('.container')).width;
            """)
            # 简化校验：主内容区宽度约为容器的60%
            main_ratio = float(main_width.replace('px', '')) / float(container_width.replace('px', ''))
            if not (0.55 <= main_ratio <= 0.65):
                return {
                    'is_passed': False,
                    'msg': 'PC端主内容区宽度应占60%，请调整Flex宽度分配',
                    'error_type': 'PC端布局比例错误',
                    'score': 0
                }

            # 2. 检查平板端2列布局（768-1200px）
            driver.set_window_size(1000, 800)
            sidebar_left_display = driver.execute_script("""
                return getComputedStyle(document.querySelector('.sidebar-left')).display;
            """)
            if sidebar_left_display != 'none':
                return {
                    'is_passed': False,
                    'msg': '平板端（768-1200px）应隐藏左侧边栏.sidebar-left',
                    'error_type': '平板端布局错误',
                    'score': 0
                }
            # 主内容区与右侧边栏比例（70% + 30%）
            main_ratio_tablet = float(driver.execute_script("""
                return getComputedStyle(document.querySelector('.main-content')).width;
            """).replace('px', '')) / float(driver.execute_script("""
                return getComputedStyle(document.querySelector('.container')).width;
            """).replace('px', ''))
            if not (0.65 <= main_ratio_tablet <= 0.75):
                return {
                    'is_passed': False,
                    'msg': '平板端主内容区宽度应占70%，请调整Flex宽度分配',
                    'error_type': '平板端布局比例错误',
                    'score': 0
                }

            # 3. 检查移动端1列布局（<768px）
            driver.set_window_size(700, 800)
            container_flex_direction = driver.execute_script("""
                return getComputedStyle(document.querySelector('.container')).flexDirection;
            """)
            if container_flex_direction != 'column':
                return {
                    'is_passed': False,
                    'msg': '移动端（<768px）应设置flex-direction: column实现堆叠布局',
                    'error_type': '移动端布局错误',
                    'score': 0
                }
            # 主内容区和右侧边栏宽度100%
            main_width_mobile = driver.execute_script("""
                return getComputedStyle(document.querySelector('.main-content')).width;
            """)
            if '100%' not in main_width_mobile:
                return {
                    'is_passed': False,
                    'msg': '移动端主内容区宽度应设为100%',
                    'error_type': '移动端布局宽度错误',
                    'score': 0
                }

            # 4. 检查导航栏移动端适配（隐藏第4、5个链接）
            nav_link_4_display = driver.execute_script("""
                return getComputedStyle(document.querySelector('.nav-links a:nth-child(4)')).display;
            """)
            nav_link_5_display = driver.execute_script("""
                return getComputedStyle(document.querySelector('.nav-links a:nth-child(5)')).display;
            """)
            if nav_link_4_display != 'none' or nav_link_5_display != 'none':
                return {
                    'is_passed': False,
                    'msg': '移动端应隐藏第4、5个导航链接（标签、关于）',
                    'error_type': '导航栏响应式错误',
                    'score': 0
                }

            # 所有校验通过
            return {
                'is_passed': True,
                'msg': '响应式布局进阶完成！PC/平板/移动端适配完美，用户体验优秀～',
                'error_type': None,
                'score': 100
            }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'响应式校验异常：{str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            if driver:
                driver.quit()

    @staticmethod
    def validate_4_2(html_code, css_code):
        """关卡4-2：CSS美化与动画校验"""
        driver = None
        try:
            driver = Stage4Validator._init_selenium()
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{full_html}")

            # 1. 检查卡片渐变背景（从#3498db到#2980b9）
            card_bg = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card')).backgroundImage;
            """)
            if 'linear-gradient' not in card_bg or '3498db' not in card_bg or '2980b9' not in card_bg:
                return {
                    'is_passed': False,
                    'msg': '卡片未设置渐变背景，请添加background: linear-gradient(to right, #3498db, #2980b9)',
                    'error_type': '渐变背景错误',
                    'score': 0
                }

            # 2. 检查卡片圆角（border-radius: 8px）
            card_radius = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card')).borderRadius;
            """)
            if '8px' not in card_radius:
                return {
                    'is_passed': False,
                    'msg': '卡片未设置圆角，请添加border-radius: 8px',
                    'error_type': '圆角设置错误',
                    'score': 0
                }

            # 3. 检查卡片阴影（box-shadow: 0 2px 10px rgba(0,0,0,0.1)）
            card_shadow = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card')).boxShadow;
            """)
            if 'rgba(0, 0, 0, 0.1)' not in card_shadow:
                return {
                    'is_passed': False,
                    'msg': '卡片阴影效果错误，请添加box-shadow: 0 2px 10px rgba(0,0,0,0.1)',
                    'error_type': '阴影设置错误',
                    'score': 0
                }

            # 4. 检查卡片hover上浮效果（transform: translateY(-5px)）
            # 触发hover事件
            driver.execute_script("""
                const card = document.querySelector('.card');
                const event = new MouseEvent('mouseover', { bubbles: true });
                card.dispatchEvent(event);
            """)
            card_transform = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card')).transform;
            """)
            # 检查是否有Y轴平移（matrix中第5个值为Y偏移）
            if 'matrix' in card_transform:
                transform_values = re.findall(r'\((.*?)\)', card_transform)[0].split(', ')
                y_translate = float(transform_values[5])
                if y_translate > -4:  # 上浮至少4px（接近5px）
                    return {
                        'is_passed': False,
                        'msg': '卡片hover未实现上浮5px效果，请添加transform: translateY(-5px)',
                        'error_type': 'hover上浮效果错误',
                        'score': 0
                    }
            else:
                return {
                    'is_passed': False,
                    'msg': '卡片hover未实现上浮5px效果，请添加transform: translateY(-5px)',
                    'error_type': 'hover上浮效果错误',
                    'score': 0
                }

            # 5. 检查按钮hover动画（背景色#f1c40f、缩放1.05）
            driver.execute_script("""
                const btn = document.querySelector('.card-btn');
                const event = new MouseEvent('mouseover', { bubbles: true });
                btn.dispatchEvent(event);
            """)
            btn_bg = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-btn')).backgroundColor;
            """)
            btn_transform = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-btn')).transform;
            """)
            # 检查背景色（#f1c40f对应rgb(241, 196, 15)）
            if btn_bg != 'rgb(241, 196, 15)':
                return {
                    'is_passed': False,
                    'msg': '按钮hover背景色错误，应设置为#f1c40f',
                    'error_type': '按钮hover背景色错误',
                    'score': 0
                }
            # 检查缩放（matrix中第0个值为缩放比例）
            if 'matrix' in btn_transform:
                scale = float(re.findall(r'\((.*?)\)', btn_transform)[0].split(', ')[0])
                if scale < 1.04:  # 缩放至少1.04（接近1.05）
                    return {
                        'is_passed': False,
                        'msg': '按钮hover未实现缩放1.05效果，请添加transform: scale(1.05)',
                        'error_type': '按钮hover缩放效果错误',
                        'score': 0
                    }
            else:
                return {
                    'is_passed': False,
                    'msg': '按钮hover未实现缩放1.05效果，请添加transform: scale(1.05)',
                    'error_type': '按钮hover缩放效果错误',
                    'score': 0
                }

            # 6. 检查过渡动画（transition: all 0.3s ease）
            card_transition = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card')).transition;
            """)
            btn_transition = driver.execute_script("""
                return getComputedStyle(document.querySelector('.card-btn')).transition;
            """)
            if '0.3s' not in card_transition or '0.3s' not in btn_transition:
                return {
                    'is_passed': False,
                    'msg': '卡片和按钮未设置过渡动画，请添加transition: all 0.3s ease',
                    'error_type': '过渡动画错误',
                    'score': 0
                }

            # 所有校验通过
            return {
                'is_passed': True,
                'msg': 'CSS美化与动画效果完美！渐变、阴影、hover动画都符合要求，视觉体验优秀～',
                'error_type': None,
                'score': 100
            }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'美化与动画校验异常：{str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            if driver:
                driver.quit()

    @staticmethod
    def validate_4_3(html_code, css_code):
        """关卡4-3：综合项目（个人博客首页）校验"""
        driver = None
        try:
            driver = Stage4Validator._init_selenium()
            full_html = f"<html><head><style>{css_code}</style></head><body>{html_code}</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{full_html}")

            # 综合项目采用评分制（0-100分），分5个维度
            score = 0
            feedback = []

            # 1. 语义化HTML结构（20分）
            semantic_tags = ['header', 'nav', 'main', 'aside', 'footer', 'article']
            missing_semantic = []
            for tag in semantic_tags:
                if not driver.execute_script(f"""
                    return document.querySelector('{tag}') !== null;
                """):
                    missing_semantic.append(tag)
            if not missing_semantic:
                score += 20
                feedback.append('语义化结构完整（20分）')
            else:
                score += max(0, 20 - len(missing_semantic) * 4)
                feedback.append(f'语义化结构缺失{", ".join(missing_semantic)}（{max(0, 20 - len(missing_semantic) * 4)}分）')

            # 2. Flex+Grid混合布局（25分）
            # 检查是否同时使用Flex和Grid
            has_flex = False
            has_grid = False
            all_elements = driver.execute_script("""
                return Array.from(document.getElementsByTagName('*')).map(el => getComputedStyle(el).display);
            """)
            if 'flex' in all_elements:
                has_flex = True
            if 'grid' in all_elements:
                has_grid = True
            if has_flex and has_grid:
                score += 15
                feedback.append('Flex+Grid混合布局使用正确（15分）')
            else:
                score += (10 if has_flex or has_grid else 0)
                feedback.append(f'{"仅使用Flex" if has_flex else "仅使用Grid" if has_grid else "未使用Flex/Grid"}（{10 if has_flex or has_grid else 0}分）')
            # 检查布局合理性（主内容区居中）
            main_center = driver.execute_script("""
                const main = document.querySelector('main');
                if (!main) return false;
                const marginLeft = parseInt(getComputedStyle(main).marginLeft);
                const marginRight = parseInt(getComputedStyle(main).marginRight);
                return marginLeft === marginRight && marginLeft > 0;
            """)
            if main_center:
                score += 10
                feedback.append('主内容区水平居中（10分）')
            else:
                feedback.append('主内容区未水平居中（0分）')

            # 3. 响应式适配（25分）
            # PC端（>1200px）布局
            driver.set_window_size(1400, 800)
            pc_layout_valid = driver.execute_script("""
                const container = document.querySelector('.container') || document.body;
                return getComputedStyle(container).display !== 'block' || container.offsetWidth > 1200;
            """)
            # 移动端（<768px）布局
            driver.set_window_size(700, 800)
            mobile_layout_valid = driver.execute_script("""
                const container = document.querySelector('.container') || document.body;
                return getComputedStyle(container).flexDirection === 'column' || container.offsetWidth === 700;
            """)
            if pc_layout_valid and mobile_layout_valid:
                score += 25
                feedback.append('PC/移动端响应式适配完美（25分）')
            elif pc_layout_valid or mobile_layout_valid:
                score += 15
                feedback.append(f'{"仅PC端" if pc_layout_valid else "仅移动端"}适配正确（15分）')
            else:
                feedback.append('未实现响应式适配（0分）')

            # 4. CSS美化与动画（20分）
            # 检查背景/阴影/圆角
            has_beautiful_style = driver.execute_script("""
                const body = document.body;
                const has_bg = getComputedStyle(body).backgroundImage !== 'none';
                const has_shadow = Array.from(document.getElementsByTagName('*')).some(el => 
                    getComputedStyle(el).boxShadow !== 'none'
                );
                const has_radius = Array.from(document.getElementsByTagName('*')).some(el => 
                    getComputedStyle(el).borderRadius !== '0px'
                );
                return has_bg || has_shadow || has_radius;
            """)
            # 检查动画效果
            has_animation = driver.execute_script("""
                return Array.from(document.getElementsByTagName('*')).some(el => 
                    getComputedStyle(el).transition !== 'none' || getComputedStyle(el).animation !== 'none'
                );
            """)
            if has_beautiful_style and has_animation:
                score += 20
                feedback.append('CSS美化与动画效果优秀（20分）')
            elif has_beautiful_style or has_animation:
                score += 10
                feedback.append(f'{"仅美化" if has_beautiful_style else "仅动画"}效果达标（10分）')
            else:
                feedback.append('未添加CSS美化与动画（0分）')

            # 5. 文本样式可读性（10分）
            text_style_valid = driver.execute_script("""
                const p = document.querySelector('p');
                if (!p) return false;
                const fontSize = parseInt(getComputedStyle(p).fontSize);
                const lineHeight = parseFloat(getComputedStyle(p).lineHeight);
                const color = getComputedStyle(p).color;
                // 字体14-18px，行高1.5-1.8，颜色非纯白/纯黑
                return fontSize >=14 && fontSize <=18 && lineHeight >=1.5 && lineHeight <=1.8 && color !== 'rgb(255, 255, 255)' && color !== 'rgb(0, 0, 0)';
            """)
            if text_style_valid:
                score += 10
                feedback.append('文本样式可读性优秀（10分）')
            else:
                feedback.append('文本样式可读性不佳（0分）')

            # 判定是否通关（60分及以上）
            is_passed = score >= 60
            final_msg = f'综合项目得分：{score}分！{"恭喜通关所有关卡！" if is_passed else "未达标，请继续优化～"}'
            final_msg += '\n评分详情：' + ' | '.join(feedback)

            return {
                'is_passed': is_passed,
                'msg': final_msg,
                'error_type': None if is_passed else '综合项目未达标',
                'score': score
            }
        except Exception as e:
            return {
                'is_passed': False,
                'msg': f'综合项目校验异常：{str(e)[:50]}',
                'error_type': '校验异常',
                'score': 0
            }
        finally:
            if driver:
                driver.quit()