from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.submission import Submission
from app.models.level import Level
from app.services.analytics_service import get_user_submission_stats
from app.services.analytics_service import (
    get_class_analytics,
    get_student_detail_stats,
    generate_comparison_chart
)

# 创建教师后台蓝图
teacher = Blueprint('teacher', __name__)

# 教师后台首页（数据看板）
@teacher.route('/dashboard')
@login_required
def dashboard():
    """教师数据看板：班级整体进度、薄弱知识点、成绩分布"""
    # 验证教师角色
    if current_user.role != 'teacher':
        return jsonify({'status': 'error', 'msg': '无访问权限'}), 403

    # 获取班级整体分析数据
    class_analytics = get_class_analytics()

    # 渲染数据看板页面
    return render_template(
        'teacher/dashboard.html',
        current_user=current_user,
        analytics=class_analytics
    )

# 学生列表页
@teacher.route('/students')
@login_required
def student_list():
    """学生列表：查看所有学生账号"""
    if current_user.role != 'teacher':
        return jsonify({'status': 'error', 'msg': '无访问权限'}), 403

    # 获取所有学生（按ID排序）
    students = User.query.filter_by(role='student').order_by(User.id).all()

    return render_template(
        'teacher/student_list.html',
        current_user=current_user,
        students=students,
        get_user_submission_stats=get_user_submission_stats
    )

# 学生详情页
@teacher.route('/student/<user_id>')
@login_required
def student_detail(user_id):
    """学生详情：查看单个学生的提交记录、错误分布、进度"""
    if current_user.role != 'teacher':
        return jsonify({'status': 'error', 'msg': '无访问权限'}), 403

    # 获取学生数据
    student = User.query.get(user_id)
    if not student or student.role != 'student':
        return jsonify({'status': 'error', 'msg': '学生不存在'}), 404

    # 获取学生详细统计数据
    student_stats = get_student_detail_stats(user_id)

    # 获取学生所有提交记录（按时间倒序）
    submissions = Submission.query.filter_by(user_id=user_id).order_by(Submission.submit_time.desc()).limit(20).all()

    # 获取所有关卡
    levels = Level.query.order_by(Level.id).all()

    return render_template(
        'teacher/student_detail.html',
        current_user=current_user,
        student=student,
        student_stats=student_stats,
        submissions=submissions,
        levels=levels
    )

# 数据分析API：生成对比图表（游戏组vs传统组）
@teacher.route('/analytics/comparison-chart')
@login_required
def comparison_chart():
    """生成游戏组与传统组的对比图表（支撑论文验证）"""
    if current_user.role != 'teacher':
        return jsonify({'status': 'error', 'msg': '无访问权限'}), 403

    # 生成对比图表（返回图片Base64编码，可直接在前端显示）
    chart_base64 = generate_comparison_chart()

    return jsonify({
        'status': 'success',
        'chart_base64': chart_base64
    })