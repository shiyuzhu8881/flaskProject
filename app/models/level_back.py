from app import db
import json
from datetime import datetime

class Level(db.Model):
    """关卡模型"""
    __tablename__ = 'levels'

    # 字段定义
    id = db.Column(db.String(10), primary_key=True)  # 关卡ID：1-1, 1-2...
    stage = db.Column(db.Integer, nullable=False)  # 阶段：1-4
    topic = db.Column(db.String(50), nullable=False)  # 知识点主题
    task = db.Column(db.Text, nullable=False)  # 任务描述
    difficulty = db.Column(db.Integer, nullable=False)  # 难度：1-5星
    hints = db.Column(db.Text, nullable=False)  # 提示列表（JSON字符串）
    initial_html = db.Column(db.Text, nullable=False)  # 初始HTML代码
    initial_css = db.Column(db.Text, default='')  # 初始CSS代码
    required_knowledge = db.Column(db.Text, nullable=False)  # 必备知识点（JSON字符串）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    # 新增：关卡类型（默认code，可选choice/drag）
    type = db.Column(db.String(20), default='code')
    # 新增：选择题/拖拽题配置（JSON字符串，不影响原有编程关）
    extra_config = db.Column(db.Text, default='{}')

    # 辅助方法：JSON字符串转Python对象
    def get_hints(self):
        """获取提示列表"""
        return json.loads(self.hints)

    def get_required_knowledge(self):
        """获取必备知识点列表"""
        return json.loads(self.required_knowledge)

    def get_extra_config(self):
        """获取额外配置（选择题/拖拽题）"""
        return json.loads(self.extra_config)

    def __repr__(self):
        return f'<Level {self.id}: {self.topic}>'