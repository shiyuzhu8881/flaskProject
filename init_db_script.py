# init_db_script.py（项目根目录下）
import os
import sys

# 将项目根目录加入Python路径（确保能导入app）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入run.py中的app和init_db函数
from run import app, init_db

# 关键：激活Flask应用上下文（否则DB操作会报错）
with app.app_context():
    init_db()  # 执行初始化逻辑