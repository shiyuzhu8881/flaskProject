import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'web-architect-2024-sec-key'  # 会话加密密钥
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用SQLAlchemy修改跟踪警告
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'web_architect.db')  # SQLite数据库路径
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')  # 日志输出配置

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True  # 开启调试模式
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    # 生产环境可替换为PostgreSQL（需手动安装依赖）
    # SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/web_architect'

# 配置映射，支持环境切换
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}