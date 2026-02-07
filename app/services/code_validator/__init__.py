"""代码校验服务：统一入口，路由到对应阶段的校验逻辑"""
from app.services.code_validator.stage1 import Stage1Validator
from app.services.code_validator.stage2 import Stage2Validator
from app.services.code_validator.stage3 import Stage3Validator
from app.services.code_validator.stage4 import Stage4Validator

def validate_code(level_id, html_code, css_code):
    """
    代码校验统一入口
    参数：level_id（关卡ID）、html_code（HTML代码）、css_code（CSS代码）
    返回：{is_passed: bool, msg: str, error_type: str, score: int}
    """
    # 根据关卡ID判断阶段
    if level_id.startswith('1-'):
        return Stage1Validator.validate(level_id, html_code, css_code)
    elif level_id.startswith('2-'):
        return Stage2Validator.validate(level_id, html_code, css_code)
    elif level_id.startswith('3-'):
        return Stage3Validator.validate(level_id, html_code, css_code)
    elif level_id.startswith('4-'):
        return Stage4Validator.validate(level_id, html_code, css_code)
    else:
        return {
            'is_passed': False,
            'msg': '无效的关卡ID',
            'error_type': '系统错误',
            'score': 0
        }