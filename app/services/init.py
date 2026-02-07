# 导出核心服务，简化导入
from app.services.code_validator import validate_code
from app.services.progress_service import update_user_progress, get_next_level
from app.services.analytics_service import (
    get_user_submission_stats,
    get_class_analytics,
    get_student_detail_stats,
    generate_comparison_chart
)