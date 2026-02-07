from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime

class User(UserMixin, db.Model):
    """用户模型（学生/教师）"""
    __tablename__ = 'users'

    # 字段定义
    id = db.Column(db.String(50), primary_key=True)  # 用户ID（学号/工号）
    email = db.Column(db.String(120), unique=True, nullable=False)  # 邮箱（唯一）
    password_hash = db.Column(db.String(128), nullable=False)  # 加密密码
    role = db.Column(db.String(20), nullable=False)  # 角色：student/teacher
    progress = db.Column(db.Text, default='{}')  # 学习进度（JSON字符串）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 密码相关方法
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    # 进度相关方法
    def get_progress(self):
        """获取进度（JSON字符串转字典）"""
        return json.loads(self.progress)

    def update_progress(self, progress_dict):
        """更新进度（字典转JSON字符串）"""
        self.progress = json.dumps(progress_dict, ensure_ascii=False)

    def __repr__(self):
        return f'<User {self.id} ({self.role})>'

# Flask-Login回调函数：通过用户ID加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)