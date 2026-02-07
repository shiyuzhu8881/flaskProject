from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.level import Level

# 创建蓝图
main = Blueprint('main', __name__)

# 登录页
@main.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录路由"""
    # 已登录用户直接跳转到游戏页面
    if current_user.is_authenticated:
        return redirect(url_for('main.game'))

    # 处理POST登录请求
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'  # 记住登录

        # 验证用户
        user = User.query.get(user_id)
        if user and user.check_password(password):
            # 登录用户
            login_user(user, remember=remember)
            # 跳转至之前访问的页面（如直接访问游戏页会跳登录，登录后返回游戏页）
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.game'))
        else:
            flash('用户名或密码错误，请重试', 'danger')

    # GET请求返回登录页面
    return render_template('auth/login.html')

# 注册页（仅教师可创建学生账号，简化版）
@main.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """学生注册路由（需教师登录后访问）"""
    # 非教师角色禁止访问
    if current_user.role != 'teacher':
        flash('仅教师可创建学生账号', 'warning')
        return redirect(url_for('main.login'))

    # 处理POST注册请求
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 表单验证
        if not (user_id and email and password and confirm_password):
            flash('所有字段均为必填', 'danger')
            return redirect(url_for('main.register'))
        if password != confirm_password:
            flash('两次密码输入不一致', 'danger')
            return redirect(url_for('main.register'))
        if User.query.get(user_id):
            flash('该用户名已存在', 'danger')
            return redirect(url_for('main.register'))

        # 创建学生用户
        student = User(
            id=user_id,
            email=email,
            role='student'
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash(f'学生账号{user_id}创建成功', 'success')
        return redirect(url_for('teacher.student_list'))

    # GET请求返回注册页面
    return render_template('auth/register.html')

# 游戏主界面（登录后访问）
@main.route('/game')
@login_required
def game():
    """游戏主界面路由：动态加载当前可玩关卡"""
    # 获取用户进度
    progress = current_user.get_progress()
    # 获取所有关卡（按ID排序）
    levels = Level.query.order_by(Level.id).all()
    level_ids = [level.id for level in levels]

    # 初始化进度：未解锁任何关卡时，解锁1-1
    if not progress or all(status == 'locked' for status in progress.values()):
        progress = {level.id: 'locked' for level in levels}
        progress['1-1'] = 'unlocked'
        current_user.update_progress(progress)
        db.session.commit()

    # 找到当前可玩的第一个关卡（优先未通关的unlocked关卡）
    current_level_id = None
    for level_id in level_ids:
        status = progress.get(level_id, 'locked')
        if status == 'unlocked':
            current_level_id = level_id
            break
    # 所有关卡已解锁但未通关时，取第一个未通关的
    if not current_level_id:
        for level_id in level_ids:
            if progress.get(level_id) == 'passed':
                continue
            current_level_id = level_id
            break
    # 所有关卡已通关，默认显示最后一关
    if not current_level_id:
        current_level_id = level_ids[-1]

    # 获取当前关卡数据
    current_level = Level.query.get(current_level_id)

    # 渲染游戏页面
    return render_template(
        'game/game.html',
        current_user=current_user,
        current_level=current_level,
        progress=progress,
        all_levels=levels
    )


@main.route('/student/stats')
@login_required
def student_stats():
    """学生进度可视化页面"""
    # 仅学生可访问
    if current_user.role != 'student':
        flash('仅学生可访问该页面', 'warning')
        return redirect(url_for('main.game'))

    # 获取学生统计数据（直接调用服务函数，避免二次请求）
    from app.services.analytics_service import get_user_submission_stats
    stats = get_user_submission_stats(current_user.id)

    # 获取所有关卡（用于展示关卡列表）
    levels = Level.query.order_by(Level.id).all()

    return render_template(
        'student/stats.html',
        current_user=current_user,
        stats=stats,
        all_levels=levels
    )

# 退出登录
@main.route('/logout')
@login_required
def logout():
    """退出登录路由"""
    logout_user()
    flash('已成功退出登录', 'info')
    return redirect(url_for('main.login'))

# 首页（跳转到登录页）
@main.route('/')
def index():
    """首页路由：默认跳转到登录页"""
    return redirect(url_for('main.login'))