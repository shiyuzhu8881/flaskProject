"""进度管理服务：处理用户关卡解锁、进度更新逻辑"""
from app import db
from app.models.user import User
from app.models.level import Level

def update_user_progress(user_id, level_id):
    """
    通关后更新用户进度，解锁下一关卡
    参数：user_id（用户ID）、level_id（已通关关卡ID）
    返回：bool（更新成功与否）
    """
    # 获取用户和所有关卡
    user = User.query.get(user_id)
    if not user:
        return False
    levels = Level.query.order_by(Level.id).all()
    level_ids = [level.id for level in levels]

    # 获取当前进度
    progress = user.get_progress()
    # 标记当前关卡为已通关
    progress[level_id] = 'passed'

    # 找到下一关卡并解锁
    current_idx = level_ids.index(level_id)
    if current_idx < len(level_ids) - 1:
        next_level_id = level_ids[current_idx + 1]
        progress[next_level_id] = 'unlocked'

    # 保存进度
    user.update_progress(progress)
    db.session.commit()
    return True

def get_next_level(level_id):
    """
    获取指定关卡的下一关卡ID
    参数：level_id（当前关卡ID）
    返回：str/None（下一关卡ID或None）
    """
    levels = Level.query.order_by(Level.id).all()
    level_ids = [level.id for level in levels]
    if level_id not in level_ids:
        return None
    current_idx = level_ids.index(level_id)
    if current_idx < len(level_ids) - 1:
        return level_ids[current_idx + 1]
    return None

def get_user_current_level(user_id):
    """
    获取用户当前可玩的关卡ID
    参数：user_id（用户ID）
    返回：str（当前关卡ID）
    """
    user = User.query.get(user_id)
    if not user:
        return '1-1'  # 默认返回第一关
    progress = user.get_progress()
    levels = Level.query.order_by(Level.id).all()
    level_ids = [level.id for level in levels]

    # 优先返回未通关的unlocked关卡
    for level_id in level_ids:
        status = progress.get(level_id, 'locked')
        if status == 'unlocked':
            return level_id

    # 所有关卡已通关，返回最后一关
    return level_ids[-1]