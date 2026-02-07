from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.level import Level
from app.models.submission import Submission
from app.services.code_validator import validate_code
from app.services.progress_service import update_user_progress, get_next_level
from app.services.analytics_service import get_user_submission_stats

# 创建API蓝图
api = Blueprint('api', __name__)

# 1. 代码提交与校验API
@api.route('/submit-code', methods=['POST'])
@login_required
def submit_code():
    """
    学生代码提交与校验API
    请求体：{level_id: str, html_code: str, css_code: str, used_hint_count: int}
    响应：{status: str, msg: str, is_passed: bool, next_level: str/None, score: int}
    """
    # 获取请求数据
    data = request.json
    level_id = data.get('level_id')
    html_code = data.get('html_code', '').strip()
    css_code = data.get('css_code', '').strip()
    used_hint_count = data.get('used_hint_count', 0)

    # 验证参数
    if not level_id:
        return jsonify({
            'status': 'error',
            'msg': '缺少关卡ID',
            'is_passed': False
        }), 400

    # 获取关卡数据
    level = Level.query.get(level_id)
    if not level:
        return jsonify({
            'status': 'error',
            'msg': '关卡不存在',
            'is_passed': False
        }), 404

    # 调用校验服务（核心逻辑）
    validate_result = validate_code(level_id, html_code, css_code)
    is_passed = validate_result['is_passed']
    error_type = validate_result['error_type']
    msg = validate_result['msg']

    # 计算得分（综合关卡1-100分，其他关卡通关得100分）
    score = validate_result.get('score', 100) if is_passed else 0
    if level_id == '4-3':  # 综合项目单独计分
        score = validate_result.get('score', 0)

    # 记录提交记录
    submission = Submission(
        user_id=current_user.id,
        level_id=level_id,
        html_code=html_code,
        css_code=css_code,
        is_passed=is_passed,
        error_type=error_type,
        score=score,
        used_hint_count=used_hint_count
    )
    db.session.add(submission)
    db.session.commit()

    # 通关后更新进度，获取下一关卡
    next_level = None
    if is_passed:
        # 更新用户进度
        update_user_progress(current_user.id, level_id)
        # 获取下一关卡ID
        next_level = get_next_level(level_id)
        msg = f'恭喜通关！{msg} 即将解锁关卡{next_level}' if next_level else f'恭喜通关所有关卡！{msg}'

    # 返回响应
    return jsonify({
        'status': 'success' if is_passed else 'fail',
        'msg': msg,
        'is_passed': is_passed,
        'next_level': next_level,
        'score': score,
        'error_type': error_type
    })

# 2. 获取关卡提示API
@api.route('/get-hint/<level_id>')
@login_required
def get_hint(level_id):
    """
    获取关卡提示API
    路径参数：level_id（关卡ID）
    响应：{status: str, hint: str}
    """
    # 获取关卡数据
    level = Level.query.get(level_id)
    if not level:
        return jsonify({
            'status': 'error',
            'hint': '关卡不存在'
        }), 404

    # 获取提示列表
    hints = level.get_hints()
    # 统计用户已使用的提示次数（简化版：返回第一个未使用的提示）
    submission_count = Submission.query.filter_by(
        user_id=current_user.id,
        level_id=level_id
    ).count()
    # 根据提交次数返回不同提示（提交次数越多，提示越详细）
    hint_index = min(submission_count, len(hints)-1)
    current_hint = hints[hint_index]

    return jsonify({
        'status': 'success',
        'hint': current_hint
    })

# 3. 获取用户进度API
@api.route('/user-progress')
@login_required
def user_progress():
    """
    获取用户当前进度API
    响应：{status: str, progress: dict, current_level: str}
    """
    progress = current_user.get_progress()
    levels = Level.query.order_by(Level.id).all()
    level_ids = [level.id for level in levels]

    # 确定当前关卡
    current_level_id = None
    for level_id in level_ids:
        status = progress.get(level_id, 'locked')
        if status == 'unlocked':
            current_level_id = level_id
            break
    if not current_level_id:
        current_level_id = level_ids[0]

    return jsonify({
        'status': 'success',
        'progress': progress,
        'current_level': current_level_id
    })

# 4. 获取用户学习统计API（用于学生自我评估）
@api.route('/user-stats')
@login_required
def user_stats():
    """
    获取用户学习统计API
    响应：{status: str, stats: dict}
    """
    stats = get_user_submission_stats(current_user.id)
    return jsonify({
        'status': 'success',
        'stats': stats
    })


# 加分接口
@api.route('/add-score', methods=['POST'])
@login_required
def add_score():
    """给当前用户添加积分（新增接口）"""
    try:
        data = request.get_json()
        add_score = int(data.get('score', 0))

        if add_score <= 0:
            return jsonify({
                'success': False,
                'msg': '积分必须为正数'
            }), 400

        # 更新用户积分（复用原有User模型）
        current_user.score += add_score
        db.session.commit()

        return jsonify({
            'success': True,
            'new_score': current_user.score,
            'msg': f'成功添加{add_score}积分'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'msg': f'错误：{str(e)}'
        }), 500


# 更新进度接口
@api.route('/update-progress', methods=['POST'])
@login_required
def update_progress():
    """更新用户关卡进度（新增接口）"""
    try:
        data = request.get_json()
        progress_dict = data.get('progress', {})

        # 验证进度格式
        if not isinstance(progress_dict, dict):
            return jsonify({
                'success': False,
                'msg': '进度必须为字典格式'
            }), 400

        # 复用User模型原有方法更新进度
        current_user.update_progress(progress_dict)
        db.session.commit()

        return jsonify({
            'success': True,
            'msg': '进度更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'msg': f'错误：{str(e)}'
        }), 500