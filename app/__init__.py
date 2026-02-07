from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config

# 初始化第三方扩展
db = SQLAlchemy()  # 数据库ORM
login_manager = LoginManager()  # 用户认证
login_manager.login_view = 'main.login'  # 未登录时跳转的登录页
login_manager.login_message = '请先登录后访问'  # 登录提示信息
migrate = Migrate()  # 数据库迁移
cors = CORS()  # 跨域支持（前端独立部署时用）

def create_app(config_name):
    """Flask工厂函数：创建并配置应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # 加载配置

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})  # API跨域允许

    # 注册蓝图（路由分离）
    from app.routes.main import main as main_bp
    from app.routes.api import api as api_bp
    from app.routes.teacher import teacher as teacher_bp
    app.register_blueprint(main_bp)  # 前端页面（登录、游戏）
    app.register_blueprint(api_bp, url_prefix='/api')  # 后端API
    app.register_blueprint(teacher_bp, url_prefix='/teacher')  # 教师后台

    # 注册错误处理函数
    @app.errorhandler(404)
    def page_not_found(e):
        """404页面处理"""
        return {"status": "error", "msg": "页面不存在"}, 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """500服务器错误处理"""
        return {"status": "error", "msg": "服务器内部错误"}, 500

    return app