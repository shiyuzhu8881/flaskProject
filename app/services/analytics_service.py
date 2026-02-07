"""数据分析服务：支撑论文有效性验证，提供学生/班级统计、对比图表"""
from app import db
from app.models.user import User
from app.models.submission import Submission
from app.models.level import Level
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO, StringIO
import base64
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # 避免中文乱码（论文建议用英文图表）
plt.rcParams['axes.unicode_minus'] = False

def get_user_submission_stats(user_id):
    """
    获取单个学生的学习统计数据
    参数：user_id（学生ID）
    返回：dict（统计结果）
    """
    # 获取学生所有提交记录
    submissions = Submission.query.filter_by(user_id=user_id).all()
    if not submissions:
        return {
            'total_submissions': 0,
            'passed_levels': 0,
            'avg_score': 0,
            'error_distribution': {},
            'level_progress': {}
        }

    # 转换为DataFrame便于分析
    df = pd.DataFrame([{
        'level_id': s.level_id,
        'is_passed': s.is_passed,
        'score': s.score,
        'error_type': s.error_type,
        'submit_time': s.submit_time
    } for s in submissions])

    # 1. 总提交次数
    total_submissions = len(df)

    # 2. 已通关关卡数（去重）
    passed_levels = int(df[df['is_passed']].groupby('level_id').size().count())
    #passed_levels = df[df['is_passed']].groupby('level_id').size().count()

    # 3. 平均得分
    avg_score = float(df['score'].mean().round(1)) if not df.empty else 0.0
    #avg_score = df['score'].mean().round(1) if not df.empty else 0

    # 4. 错误类型分布（value_counts结果为NumPy int64，转换为Python int）
    error_distribution = {}
    if not df[~df['is_passed']].empty:
        error_series = df[~df['is_passed']]['error_type'].value_counts()
        # 遍历Series，将NumPy int64转为Python int
        for error_type, count in error_series.items():
            error_distribution[error_type] = int(count)

    # 5. 各关卡进度（highest_score转换为Python int）
    level_progress = {}
    levels = Level.query.order_by(Level.id).all()
    for level in levels:
        level_df = df[df['level_id'] == level.id]
        highest_score = level_df['score'].max() if not level_df.empty else 0
        level_progress[level.id] = {
            'submission_count': len(level_df),  # Python原生int
            'is_passed': any(level_df['is_passed']),
            'highest_score': int(highest_score)  # 转换为Python int
        }


    return {
        'total_submissions': total_submissions,
        'passed_levels': passed_levels,
        'avg_score': avg_score,
        'error_distribution': error_distribution,
        'level_progress': level_progress
    }

def get_class_analytics():
    """
    获取班级整体分析数据（教师看板用）
    返回：dict（班级统计结果）
    """
    # 获取所有学生和提交记录
    students = User.query.filter_by(role='student').all()
    submissions = Submission.query.all()
    levels = Level.query.order_by(Level.id).all()
    level_ids = [level.id for level in levels]

    if not students or not submissions:
        return {
            'total_students': 0,
            'avg_passed_levels': 0,
            'avg_avg_score': 0,
            'level_pass_rate': {},
            'common_errors': {},
            'progress_distribution': {}
        }

    # 1. 总学生数
    total_students = len(students)

    # 2. 学生平均通关数、平均得分
    student_stats = []
    for student in students:
        stats = get_user_submission_stats(student.id)
        student_stats.append({
            'passed_levels': stats['passed_levels'],
            'avg_score': stats['avg_score']
        })
    student_df = pd.DataFrame(student_stats)
    avg_passed_levels = student_df['passed_levels'].mean().round(1)
    avg_avg_score = student_df['avg_score'].mean().round(1)

    # 3. 各关卡通过率
    level_pass_rate = {}
    for level_id in level_ids:
        # 参与该关卡的学生数（至少提交1次）
        #participating_students = Submission.query.filter_by(level_id=level_id).groupby('user_id').size().count()
        participating_students = Submission.query.filter_by(level_id=level_id).distinct('user_id').count()
        if participating_students == 0:
            level_pass_rate[level_id] = 0.0
            continue
        # 通关该关卡的学生数
        #passed_students = Submission.query.filter_by(level_id=level_id, is_passed=True).groupby('user_id').size().count()
        passed_students = Submission.query.filter_by(
            level_id=level_id,
            is_passed=True
        ).distinct('user_id').count()
        pass_rate = (passed_students / participating_students) * 100
        level_pass_rate[level_id] = round(pass_rate, 1)

    # 4. 常见错误类型（Top5）
    all_errors = [s.error_type for s in submissions if not s.is_passed and s.error_type]
    if all_errors:
        common_errors = pd.Series(all_errors).value_counts().head(5).to_dict()
    else:
        common_errors = {}

    # 5. 进度分布（各通关数的学生人数）
    progress_distribution = student_df['passed_levels'].value_counts().sort_index().to_dict()

    return {
        'total_students': total_students,
        'avg_passed_levels': avg_passed_levels,
        'avg_avg_score': avg_avg_score,
        'level_pass_rate': level_pass_rate,
        'common_errors': common_errors,
        'progress_distribution': progress_distribution
    }

def get_student_detail_stats(user_id):
    """
    获取单个学生的详细统计（教师端学生详情页用）
    参数：user_id（学生ID）
    返回：dict（详细统计结果）
    """
    base_stats = get_user_submission_stats(user_id)
    submissions = Submission.query.filter_by(user_id=user_id).order_by(Submission.submit_time).all()

    # 1. 通关时间线（各关卡首次通关时间）
    pass_timeline = {}
    for level_id in Level.query.order_by(Level.id).with_entities(Level.id).all():
        level_id = level_id[0]
        first_pass = Submission.query.filter_by(
            user_id=user_id,
            level_id=level_id,
            is_passed=True
        ).order_by(Submission.submit_time).first()
        if first_pass:
            pass_timeline[level_id] = first_pass.submit_time.strftime('%Y-%m-%d %H:%M')
        else:
            pass_timeline[level_id] = '未通关'

    # 2. 各关卡提交次数与得分变化
    level_submission_stats = {}
    for level in Level.query.order_by(Level.id).all():
        level_submissions = Submission.query.filter_by(
            user_id=user_id,
            level_id=level.id
        ).order_by(Submission.submit_time).all()
        if not level_submissions:
            level_submission_stats[level.id] = {
                'submissions': [],
                'score_trend': []
            }
            continue
        submissions_data = [{
            'time': s.submit_time.strftime('%Y-%m-%d %H:%M'),
            'is_passed': s.is_passed,
            'score': s.score,
            'error_type': s.error_type
        } for s in level_submissions]
        score_trend = [s['score'] for s in submissions_data]
        level_submission_stats[level.id] = {
            'submissions': submissions_data,
            'score_trend': score_trend
        }

    # 3. 薄弱知识点（错误次数最多的前3个）
    weak_topics = {}
    error_dist = base_stats['error_distribution']
    if error_dist:
        # 错误类型与知识点映射（简化）
        error_topic_map = {
            '标签未闭合': 'HTML基础结构',
            '语义化标签缺失': 'HTML语义化',
            'Flex布局未启用': 'Flexbox布局',
            'Grid列数错误': 'Grid布局',
            'CSS语法错误': 'CSS基础',
            'padding设置错误': 'CSS盒模型'
        }
        topic_errors = {}
        for error, count in error_dist.items():
            topic = error_topic_map.get(error, '其他')
            topic_errors[topic] = topic_errors.get(topic, 0) + count
        # 排序取前3
        weak_topics = dict(sorted(topic_errors.items(), key=lambda x: x[1], reverse=True)[:3])

    return {
        **base_stats,
        'pass_timeline': pass_timeline,
        'level_submission_stats': level_submission_stats,
        'weak_topics': weak_topics
    }

def generate_comparison_chart():
    """
    生成游戏组vs传统组对比图表（支撑论文验证）
    返回：str（图表Base64编码）
    """
    # 模拟数据（实际论文应替换为真实实验数据）
    groups = ['游戏组（本项目）', '传统教学组']
    metrics = {
        '平均正确率(%)': [89.2, 72.5],
        '平均通关数': [10.5, 7.2],
        '学习兴趣评分(1-5分)': [4.3, 3.1],
        '知识点掌握度(%)': [85.7, 68.3]
    }

    # 创建子图
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    colors = ['#3498db', '#e74c3c']

    # 绘制每个指标的柱状图
    for i, (metric, values) in enumerate(metrics.items()):
        ax = axes[i]
        bars = ax.bar(groups, values, color=colors, alpha=0.8)
        ax.set_title(metric, fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(values) * 1.2)
        # 在柱子上添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{value}', ha='center', va='bottom', fontsize=12)
        ax.grid(axis='y', alpha=0.3)

    # 调整布局
    plt.tight_layout()

    # 保存为BytesIO并转换为Base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return img_base64