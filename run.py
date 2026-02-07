import os
import json  # 提前导入json，避免重复导入
from app import create_app, db
from app.models.user import User
from app.models.level import Level
from app.models.submission import Submission

# 创建Flask应用实例（默认开发环境）
app = create_app(os.getenv('FLASK_ENV') or 'default')


# 注册命令行指令：初始化数据库并添加默认数据
@app.cli.command("init-db")
def init_db():
    """初始化数据库，创建表结构并添加12关卡+默认账号"""
    # 先删除旧表（确保模型修改生效，开发环境放心用）
    db.drop_all()
    # 创建新表
    db.create_all()
    print("数据库表结构创建完成")

    # 1. 添加12关卡完整数据（从JSON文件读取）
    with open('app/data/default_levels.json', 'r', encoding='utf-8') as f:
        levels_data = json.load(f)
        for level in levels_data:
            level_type = level.get('type', 'code').strip()
            if not level_type:
                level_type = 'code'

            extra_config = level.get('extra_config', {})
            if isinstance(extra_config, dict):
                extra_config = json.dumps(extra_config, ensure_ascii=False)
            elif not isinstance(extra_config, str):
                extra_config = '{}'

            new_level = Level(
                id=level['id'],
                stage=level['stage'],
                topic=level['topic'],
                task=level['task'],
                difficulty=level['difficulty'],
                hints=json.dumps(level['hints'], ensure_ascii=False),
                initial_html=level['initial_html'],
                initial_css=level['initial_css'],
                required_knowledge=json.dumps(level['required_knowledge'], ensure_ascii=False),
                type=level_type,  # ✅ 补全type字段
                extra_config=extra_config  # ✅ 补全extra_config字段
            )
            db.session.add(new_level)
    print(f"{len(levels_data)}关卡数据添加完成")  # 修正：不是固定12个，按实际读取数显示

    # 2. 添加默认账号
    # 教师账号：user_id=teacher1，password=123456
    teacher = User(
        id='teacher1',
        email='teacher1@uws.ac.uk',
        role='teacher'
    )
    teacher.set_password('123456')
    db.session.add(teacher)

    # 学生测试账号：user_id=student001，password=123456
    student = User(
        id='student001',
        email='student001@uws.ac.uk',
        role='student'
    )
    student.set_password('123456')
    db.session.add(student)

    # 提交事务
    db.session.commit()
    print("默认账号添加完成：")
    print("- 教师：ID=teacher1，密码=123456")
    print("- 学生：ID=student001，密码=123456")


# 注册命令行指令：生成测试数据（用于论文数据分析）
@app.cli.command("generate-test-data")
def generate_test_data():
    """生成10条学生提交测试数据（用于论文预测试）"""
    import random
    from datetime import datetime, timedelta

    # 模拟student001的10次提交（覆盖前3关卡）
    levels = ['1-1', '1-2', '1-3', '2-1']
    error_types = ['标签未闭合', 'Flex布局未启用', 'CSS选择器错误', 'Grid列数错误', None]
    for i in range(10):
        submission = Submission(
            user_id='student001',
            level_id=random.choice(levels),
            html_code=f'<html><body><div>测试提交{i}</div></body></html>',
            css_code=f'.test {{ color: red; }}',
            is_passed=random.choice([True, False]),
            error_type=random.choice(error_types),
            score=random.randint(60, 100) if random.choice([True, False]) else random.randint(30, 59),
            submit_time=datetime.now() - timedelta(days=random.randint(1, 7))
        )
        db.session.add(submission)
    db.session.commit()
    print("测试数据生成完成（10条提交记录）")


if __name__ == '__main__':
    # 启动应用（支持局域网访问）
    app.run(host='0.0.0.0', port=5000, debug=True)