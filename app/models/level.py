from app import db
import json


class Level(db.Model):
    """关卡模型"""
    __tablename__ = 'levels'  # 表名（可选，默认小写类名）

    # 核心字段：全部强制非空，消除默认值干扰
    id = db.Column(db.String(10), primary_key=True)  # 关卡ID：1-1, 1-2...
    stage = db.Column(db.Integer, nullable=False)  # 阶段：1,2,3...
    topic = db.Column(db.String(100), nullable=False)  # 关卡主题
    task = db.Column(db.Text, nullable=False)  # 关卡任务描述
    difficulty = db.Column(db.Integer, nullable=False)  # 难度：1-5
    hints = db.Column(db.Text, nullable=False)  # 提示（JSON字符串）
    initial_html = db.Column(db.Text, nullable=False)  # 初始HTML代码
    initial_css = db.Column(db.Text, nullable=False)  # 初始CSS代码
    required_knowledge = db.Column(db.Text, nullable=False)  # 所需知识点（JSON字符串）

    type = db.Column(db.String(10), nullable=False)  # 关卡类型：code/choice/drag
    extra_config = db.Column(db.Text, nullable=False, default='{}')  # 额外配置（JSON字符串）

    def get_hints(self):
        """解析hints字段（JSON字符串）为列表"""
        try:
            return json.loads(self.hints)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_required_knowledge(self):
        """解析required_knowledge字段为列表"""
        try:
            return json.loads(self.required_knowledge)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_extra_config(self):
        """解析extra_config字段（JSON字符串）为字典"""
        try:
            # 额外防护：如果是空字符串，返回空字典
            if not self.extra_config or self.extra_config.strip() == '':
                return {}
            return json.loads(self.extra_config)
        except (json.JSONDecodeError, TypeError):
            return {}  # 解析失败返回空字典，避免模板报错

    def __repr__(self):
        return f'<Level {self.id}: {self.topic}>'