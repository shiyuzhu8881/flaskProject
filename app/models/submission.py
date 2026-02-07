from app import db
from datetime import datetime

class Submission(db.Model):
    """学生代码提交记录模型（支撑论文数据分析）"""
    __tablename__ = 'submissions'

    # 字段定义
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增ID
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)  # 关联用户
    level_id = db.Column(db.String(10), db.ForeignKey('levels.id'), nullable=False)  # 关联关卡
    html_code = db.Column(db.Text, nullable=False)  # 提交的HTML代码
    css_code = db.Column(db.Text, default='')  # 提交的CSS代码
    is_passed = db.Column(db.Boolean, default=False)  # 是否通关
    error_type = db.Column(db.String(50))  # 错误类型（如"标签未闭合"）
    score = db.Column(db.Integer, default=0)  # 得分（综合关卡1-100分）
    submit_time = db.Column(db.DateTime, default=datetime.utcnow)  # 提交时间
    used_hint_count = db.Column(db.Integer, default=0)  # 使用提示次数（用于分析学习行为）

    # 关联关系（用于查询）
    user = db.relationship('User', backref=db.backref('submissions', lazy='dynamic'))
    level = db.relationship('Level', backref=db.backref('submissions', lazy='dynamic'))

    def __repr__(self):
        return f'<Submission {self.id}: User {self.user_id} - Level {self.level_id}>'