{% extends "base.html" %}

{% block title %}Web Architect - {{ current_level.id }} {{ current_level.topic }}{% endblock %}

{% block extra_css %}
<!-- CodeMirror Styles -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/monokai.min.css">
<!-- Game-Specific CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/game.css') }}">
<!-- 新增：拖拽功能样式 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.css">
<!-- 新增：Font Awesome 6 图标（增强视觉） -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  /* 基础游戏化样式增强 */
  :root {
    --success-color: #198754;
    --danger-color: #dc3545;
    --primary-color: #0d6efd;
    --warning-color: #ffc107;
    --game-shadow: 0 4px 12px rgba(0,0,0,0.1);
    --game-shadow-hover: 0 6px 18px rgba(0,0,0,0.15);
    --transition-base: all 0.3s ease;
  }

  .game-container {
    padding: 20px 0;
  }

  .card {
    border: none;
    border-radius: 12px;
    box-shadow: var(--game-shadow);
    transition: var(--transition-base);
  }

  .card:hover {
    box-shadow: var(--game-shadow-hover);
  }

  .card-header {
    border-radius: 12px 12px 0 0 !important;
    padding: 15px 20px;
  }

  .card-footer {
    border-radius: 0 0 12px 12px !important;
    border-top: 1px solid #eee;
  }

  /* 选择题样式增强 */
  .choice-option {
    margin-bottom: 15px;
    padding: 15px;
    border: 2px solid #eee;
    border-radius: 10px;
    cursor: pointer;
    transition: var(--transition-base);
    position: relative;
    overflow: hidden;
  }

  .choice-option:hover {
    background-color: #f8f9fa;
    border-color: var(--primary-color);
    transform: translateY(-2px);
  }

  .choice-option.selected {
    background-color: rgba(13, 110, 253, 0.1);
    border-color: var(--primary-color);
  }

  .choice-option.correct {
    background-color: rgba(25, 135, 84, 0.1);
    border-color: var(--success-color);
  }

  .choice-option.incorrect {
    background-color: rgba(220, 53, 69, 0.1);
    border-color: var(--danger-color);
  }

  /* 拖拽样式增强 */
  .drag-target {
    margin-bottom: 20px;
    padding: 20px;
    border: 2px solid #ddd;
    border-radius: 10px;
    transition: var(--transition-base);
  }

  .drag-target:hover {
    border-color: var(--primary-color);
  }

  .draggable-item {
    margin-bottom: 10px;
    padding: 12px;
    background-color: #e9ecef;
    border-radius: 8px;
    text-align: center;
    cursor: grab;
    transition: var(--transition-base);
    border: 2px solid transparent;
  }

  .draggable-item:hover {
    background-color: #dee2e6;
    transform: scale(1.02);
    border-color: var(--primary-color);
  }

  .draggable-item:active {
    cursor: grabbing;
    transform: scale(0.98);
  }

  .drop-area {
    min-height: 50px;
    margin-top: 10px;
    border: 2px dashed #adb5bd;
    border-radius: 8px;
    padding: 15px;
    transition: var(--transition-base);
  }

  .drop-area.filled {
    border-color: var(--success-color);
    background-color: #f0fdf4;
  }

  .drop-area.hovering {
    border-color: var(--primary-color);
    background-color: rgba(13, 110, 253, 0.05);
  }

  .drop-area.error {
    border-color: var(--danger-color);
    animation: shake 0.5s ease;
  }

  /* 积分展示样式增强 */
  .score-card {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border: 1px solid #ffc107;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
  }

  .score-card h5 {
    color: #856404;
    margin-bottom: 10px;
    font-weight: 600;
  }

  .score-card .score-value {
    font-size: 28px;
    font-weight: bold;
    color: #dc3545;
    position: relative;
    display: inline-block;
  }

  .score-value.animate {
    animation: pulse 0.5s ease;
  }

  /* 生命值样式 */
  .health-bar {
    display: flex;
    gap: 8px;
    margin: 15px 0;
  }

  .health-heart {
    font-size: 24px;
    color: var(--danger-color);
    transition: var(--transition-base);
  }

  .health-heart.empty {
    color: #ddd;
    transform: scale(0.8);
  }

  /* 成就提示样式 */
  .achievement-toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: white;
    border-radius: 10px;
    padding: 15px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    display: flex;
    align-items: center;
    gap: 10px;
    z-index: 9999;
    transform: translateX(120%);
    transition: transform 0.5s ease;
  }

  .achievement-toast.show {
    transform: translateX(0);
  }

  .achievement-icon {
    font-size: 24px;
    color: var(--warning-color);
  }

  /* 计时奖励样式 */
  .timer-bar {
    height: 8px;
    background-color: #eee;
    border-radius: 4px;
    margin: 10px 0;
    overflow: hidden;
  }

  .timer-progress {
    height: 100%;
    background: linear-gradient(90deg, #0d6efd 0%, #6610f2 100%);
    width: 100%;
    transition: width linear;
  }

  .time-bonus {
    font-size: 14px;
    color: var(--primary-color);
    font-weight: 600;
    margin-top: 5px;
  }

  /* 按钮样式增强 */
  .btn {
    border-radius: 8px;
    transition: var(--transition-base);
    border: none;
    font-weight: 500;
  }

  .btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }

  .btn:active {
    transform: translateY(0);
  }

  /* 动画定义 */
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .fade-in-up {
    animation: fadeInUp 0.5s ease forwards;
  }

  /* 关卡加载动画 */
  .level-loader {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.8);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    color: white;
  }

  .level-loader h2 {
    font-size: 32px;
    margin-bottom: 20px;
  }

  .loader-spinner {
    width: 50px;
    height: 50px;
    border: 5px solid rgba(255,255,255,0.2);
    border-top: 5px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>
{% endblock %}

{% block content %}
<!-- 新增：关卡加载动画 -->
<div class="level-loader" id="level-loader">
  <h2>Loading Level {{ current_level.id }}...</h2>
  <div class="loader-spinner"></div>
  <p>Preparing your challenge...</p>
</div>

<div class="game-container row g-4">
    <!-- Left Side: Task & Story Area (2 Columns) -->
    <div class="col-lg-3 col-md-12">
        <div class="card h-100 fade-in-up" style="animation-delay: 0.1s">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="fa fa-gamepad"></i> Challenge {{ current_level.id }}: {{ current_level.topic }}
                </h5>
            </div>
            <div class="card-body">
                <div class="scene mb-4">
                    <img src="{{ url_for('static', filename='assets/images/stage' + current_level.stage|string + '.png') }}"
                         alt="Stage Scene" class="img-fluid rounded" style="border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                </div>
                <div class="task-description">
                    <h6 class="fw-bold">Mission:</h6>
                    <p class="text-muted">{{ current_level.task }}</p>

                    <!-- 新增：计时奖励条 -->
                    <div class="mt-3">
                        <h6 class="fw-bold">Time Bonus:</h6>
                        <div class="timer-bar">
                            <div class="timer-progress" id="timer-progress"></div>
                        </div>
                        <div class="time-bonus" id="time-bonus">+10 Points (Fast Answer!)</div>
                    </div>

                    <!-- 新增：生命值显示 -->
                    <div class="mt-3">
                        <h6 class="fw-bold">Lives:</h6>
                        <div class="health-bar" id="health-bar">
                            <i class="fa-solid fa-heart health-heart"></i>
                            <i class="fa-solid fa-heart health-heart"></i>
                            <i class="fa-solid fa-heart health-heart"></i>
                        </div>
                    </div>

                    <div class="mt-3">
                        <h6 class="fw-bold">Required Skills:</h6>
                        <ul class="list-unstyled">
                            {% for knowledge in current_level.get_required_knowledge() %}
                                <li><i class="fa fa-star text-warning"></i> {{ knowledge }}</li>
                            {% endfor %}
                        </ul>
                    </div>

                    <!-- 积分展示样式 -->
                    <div class="mt-4 score-card">
                        <h5>Challenge Reward</h5>
                        <div class="score-value" id="level-score">
                            {% if current_level.type == 'code' %}
                                20 Points
                            {% else %}
                                {{ current_level.get_extra_config().score | default(0) }} Points
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <button id="hint-btn" class="btn btn-outline-primary w-100" data-cooldown="0">
                    <i class="fa fa-lightbulb-o"></i> Get Hint
                    <span id="hint-cooldown" class="badge bg-danger ms-2 d-none">3s</span>
                </button>
            </div>
        </div>

        <!-- Level Progress Sidebar -->
        <div class="card mt-4 fade-in-up" style="animation-delay: 0.2s">
            <div class="card-header bg-secondary text-white">
                <h5 class="mb-0">
                    <i class="fa fa-trophy"></i> Your Progress
                </h5>
            </div>
            <div class="card-body">
                <div class="progress mb-3" style="height: 10px; border-radius: 5px;">
                    {% set passed_count = progress.values() | select('equalto', 'passed') | list | length %}
                    {% set total_count = all_levels | length %}
                    {% set progress_percent = (passed_count / total_count) * 100 %}
                    <div class="progress-bar bg-success" role="progressbar" style="width: {{ progress_percent }}%; border-radius: 5px;" aria-valuenow="{{ progress_percent }}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <p class="text-sm text-muted">Completed: {{ passed_count }}/{{ total_count }} Challenges</p>

                <!-- 总积分展示 -->
                <div class="mt-3 p-3 bg-primary/10 rounded" style="border-radius: 10px;">
                    <p class="text-sm text-muted mb-1">Total Score</p>
                    <p class="fw-bold text-primary" id="total-score">{{ current_user.score }}</p>
                </div>

                <!-- 新增：成就提示 -->
                <div class="mt-3 p-3 bg-warning/10 rounded" style="border-radius: 10px;">
                    <p class="text-sm text-muted mb-1">Badges Earned</p>
                    <div class="d-flex gap-2">
                        {% if passed_count >= 5 %}
                            <i class="fa-solid fa-medal text-warning" title="5 Challenges Completed"></i>
                        {% endif %}
                        {% if passed_count >= 10 %}
                            <i class="fa-solid fa-crown text-warning" title="10 Challenges Completed"></i>
                        {% endif %}
                        {% if usedHintCount == 0 and progress.get(current_level.id) == 'passed' %}
                            <i class="fa-solid fa-brain text-primary" title="No Hints Used"></i>
                        {% endif %}
                    </div>
                </div>

                <div class="level-list mt-3">
                    {% for level in all_levels %}
                        <div class="d-flex align-items-center mb-2">
                            {% if progress.get(level.id) == 'passed' %}
                                <i class="fa fa-check-circle text-success me-2"></i>
                                <span class="text-success">{{ level.id }} - {{ level.topic }}</span>
                            {% elif progress.get(level.id) == 'unlocked' %}
                                <i class="fa fa-lock-open text-primary me-2"></i>
                                <span class="text-primary">{{ level.id }} - {{ level.topic }}</span>
                            {% else %}
                                <i class="fa fa-lock text-muted me-2"></i>
                                <span class="text-muted">{{ level.id }} - {{ level.topic }}</span>
                            {% endif %}
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- Middle: Interactive Area (4 Columns) -->
    <div class="col-lg-5 col-md-12 fade-in-up" style="animation-delay: 0.3s">
        <div class="card h-100">
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0">
                    <i class="fa fa-code"></i> {% if current_level.type == 'code' %}Code Workshop{% elif current_level.type == 'choice' %}Quiz Challenge{% else %}Drag & Match Puzzle{% endif %}
                </h5>
            </div>
            <div class="card-body p-0">
                <!-- 原有：编程关编辑器 -->
                {% if current_level.type == 'code' %}
                    <!-- HTML Editor -->
                    <div class="editor-container p-3 border-bottom">
                        <h6 class="fw-bold mb-2">HTML Workshop</h6>
                        <textarea id="html-editor" class="editor">{{ current_level.initial_html }}</textarea>
                    </div>
                    <!-- CSS Editor -->
                    <div class="editor-container p-3">
                        <h6 class="fw-bold mb-2">CSS Styling</h6>
                        <textarea id="css-editor" class="editor">{{ current_level.initial_css }}</textarea>
                    </div>
                {% elif current_level.type == 'choice' %}
                    <!-- 优化：选择题区域 -->
                    <div class="p-4">
                        <h6 class="fw-bold mb-4">Question: {{ current_level.task }}</h6>

                        <form id="choice-form">
                            {% set config = current_level.get_extra_config() | default({}, true) %}
                            {% if config.options and config.options is mapping and config.options|length > 0 %}
                                {% for option_key, option_val in config.options.items() %}
                                    <div class="form-check choice-option mb-3" data-option="{{ option_key }}">
                                        <input class="form-check-input"
                                               type="{{ 'radio' if config.question_type == 'single' else 'checkbox' }}"
                                               name="answer"
                                               id="option-{{ option_key }}"
                                               value="{{ option_key }}">
                                        <label class="form-check-label" for="option-{{ option_key }}">
                                            {{ option_key }}. {{ option_val }}
                                        </label>
                                    </div>
                                {% endfor %}
                            {% else %}
                                <div class="alert alert-warning text-center py-3">
                                    <i class="fa fa-exclamation-triangle"></i> No options configured for this question!
                                </div>
                            {% endif %}
                        </form>
                    </div>
                {% elif current_level.type == 'drag' %}
                    <!-- 新增：拖拽区域 -->
                    <div class="p-4">
                        {% set config = current_level.get_extra_config() | default({}, true) %}
                        <div class="row g-4">
                            <!-- 左侧目标区 -->
                            <div class="col-6">
                                <h6 class="fw-bold mb-3">Target Elements</h6>
                                {% if config.targets and config.targets|length > 0 %}
                                    {% for target in config.targets %}
                                        <div class="drag-target">
                                            <h7>{{ target.name }}</h7>
                                            <div class="drop-area" data-target="{{ target.id }}"></div>
                                        </div>
                                    {% endfor %}
                                {% else %}
                                    <div class="alert alert-warning text-center py-3">
                                        <i class="fa fa-exclamation-triangle"></i> No target elements configured!
                                    </div>
                                {% endif %}
                            </div>
                            <!-- 右侧拖拽项 -->
                            <div class="col-6">
                                <h6 class="fw-bold mb-3">Draggable Selectors</h6>
                                <div id="draggable-list">
                                    {% if config.draggables and config.draggables|length > 0 %}
                                        {% for draggable in config.draggables %}
                                            <div class="draggable-item" data-id="{{ draggable.id }}" data-correct="{{ draggable.correct_target }}">
                                                {{ draggable.content }}
                                            </div>
                                        {% endfor %}
                                    {% else %}
                                        <div class="alert alert-warning text-center py-3">
                                            <i class="fa fa-exclamation-triangle"></i> No draggable items configured!
                                        </div>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </div>
                {% endif %}
            </div>
            <div class="card-footer">
                <!-- 提交按钮（根据关卡类型切换） -->
                {% if current_level.type == 'code' %}
                    <button id="submit-btn" class="btn btn-success w-100 py-2">
                        <i class="fa fa-rocket"></i> Launch Code (Test Your Work)
                    </button>
                {% elif current_level.type == 'choice' %}
                    <button id="submit-choice" class="btn btn-success w-100 py-2">
                        <i class="fa fa-check"></i> Submit Answer
                    </button>
                {% elif current_level.type == 'drag' %}
                    <button id="submit-drag" class="btn btn-success w-100 py-2">
                        <i class="fa fa-check"></i> Check Matching
                    </button>
                {% endif %}
                <!-- Submission Feedback Area -->
                <div id="feedback" class="mt-3 alert d-none" role="alert"></div>

                <!-- 新增：成就提示容器 -->
                <div class="achievement-toast" id="achievement-toast">
                    <i class="fa-solid fa-award achievement-icon"></i>
                    <div>
                        <h6 class="mb-0">New Achievement!</h6>
                        <p class="mb-0 small" id="achievement-message">You earned a badge!</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Right Side: Live Preview Area (5 Columns) -->
    <div class="col-lg-4 col-md-12 fade-in-up" style="animation-delay: 0.4s">
        <div class="card h-100">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0 d-flex justify-content-between align-items-center">
                    <span><i class="fa fa-desktop"></i> {% if current_level.type == 'code' %}Live Preview{% else %}Result Zone{% endif %}</span>
                    {% if current_level.type == 'code' %}
                        <div class="device-buttons">
                            <button class="btn btn-sm btn-light device-btn active" data-device="pc">PC</button>
                            <button class="btn btn-sm btn-light device-btn" data-device="pad">Tablet</button>
                            <button class="btn btn-sm btn-light device-btn" data-device="phone">Phone</button>
                        </div>
                    {% endif %}
                </h5>
            </div>
            <div class="card-body p-0">
                {% if current_level.type == 'code' %}
                    <div class="preview-container">
                        <iframe id="preview-iframe" class="w-100"></iframe>
                    </div>
                {% else %}
                    <!-- 选择题/拖拽题结果展示区 -->
                    <div class="p-4 text-center" style="min-height: 300px; display: flex; align-items: center; justify-content: center;">
                        <div id="result-area">
                            <i class="fa fa-gamepad fa-3x text-muted mb-3"></i>
                            <p class="text-muted">Complete the challenge to see your result!</p>
                        </div>
                    </div>
                {% endif %}
            </div>
            <div class="card-footer text-center text-muted">
                {% if current_level.type == 'code' %}
                    <p class="mb-0">💡 Tip: Preview updates in real-time! Test on different devices to win bonus points.</p>
                {% elif current_level.type == 'choice' %}
                    <p class="mb-0">💡 Tip: Answer fast for time bonus! No hints = extra badge.</p>
                {% else %}
                    <p class="mb-0">💡 Tip: Drag carefully! Each wrong attempt costs a life.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- 新增：音效资源（隐藏的音频标签） -->
<audio id="sound-correct" src="{{ url_for('static', filename='sounds/correct.mp3') }}" preload="auto"></audio>
<audio id="sound-incorrect" src="{{ url_for('static', filename='sounds/incorrect.mp3') }}" preload="auto"></audio>
<audio id="sound-hint" src="{{ url_for('static', filename='sounds/hint.mp3') }}" preload="auto"></audio>
<audio id="sound-levelup" src="{{ url_for('static', filename='sounds/levelup.mp3') }}" preload="auto"></audio>
<audio id="sound-click" src="{{ url_for('static', filename='sounds/click.mp3') }}" preload="auto"></audio>
{% endblock %}

{% block extra_scripts %}
<!-- CodeMirror Core Libraries -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/htmlmixed/htmlmixed.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/css/css.min.js"></script>
<!-- 新增：拖拽库 -->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
<!-- Game Core Interaction JS -->
<script src="{{ url_for('static', filename='js/game.js') }}"></script>
<script>
    // Global Configuration
    const GAME_CONFIG = {
        currentLevel: '{{ current_level.id }}',
        userId: '{{ current_user.id }}',
        levelType: '{{ current_level.type }}',
        extraConfig: {{ current_level.get_extra_config()|tojson | default('{}') }},
        maxAttempts: 3, // 最大尝试次数（生命值）
        timeBonusDuration: 30, // 计时奖励时长（秒）
        timeBonusPoints: 10 // 计时奖励分数
    };

    // 游戏状态管理
    const gameState = {
        attemptsLeft: GAME_CONFIG.maxAttempts,
        startTime: Date.now(),
        timeBonusAvailable: true,
        hasEarnedNoHintBadge: false,
        hasCompletedLevel: false
    };

    // 音效播放函数
    function playSound(soundId) {
        const sound = document.getElementById(soundId);
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.log('Sound playback blocked:', e));
        }
    }

    // 初始化提示功能（保留原有逻辑）
    document.getElementById('hint-btn').addEventListener('click', function() {
        playSound('sound-click');
        const hints = {{ current_level.get_hints()|tojson | default('[]') }};
        const usedHintCount = parseInt(localStorage.getItem(`hint_${GAME_CONFIG.currentLevel}`) || '0');

        // 提示冷却逻辑
        const cooldownEl = document.getElementById('hint-cooldown');
        if (this.dataset.cooldown > 0) {
            showFeedback('Hint is on cooldown! Wait a few seconds.', 'warning');
            return;
        }

        if (usedHintCount < hints.length) {
            playSound('sound-hint');
            showFeedback(`💡 Hint: ${hints[usedHintCount]}`, 'info');
            localStorage.setItem(`hint_${GAME_CONFIG.currentLevel}`, usedHintCount + 1);

            // 提示冷却（5秒）
            this.dataset.cooldown = 5;
            cooldownEl.classList.remove('d-none');
            const cooldownInterval = setInterval(() => {
                this.dataset.cooldown = parseInt(this.dataset.cooldown) - 1;
                cooldownEl.textContent = `${this.dataset.cooldown}s`;
                if (this.dataset.cooldown <= 0) {
                    clearInterval(cooldownInterval);
                    cooldownEl.classList.add('d-none');
                }
            }, 1000);
        } else {
            showFeedback('❌ No more hints available!', 'warning');
        }
    });

    // 反馈提示函数（增强版）
    function showFeedback(message, type) {
        const feedbackEl = document.getElementById('feedback');
        feedbackEl.innerHTML = message;
        feedbackEl.className = `mt-3 alert alert-${type} fade-in-up`;
        feedbackEl.classList.remove('d-none');

        setTimeout(() => {
            feedbackEl.classList.add('d-none');
        }, 5000);
    }

    // 显示成就提示
    function showAchievement(message) {
        const toastEl = document.getElementById('achievement-toast');
        const msgEl = document.getElementById('achievement-message');
        msgEl.textContent = message;
        toastEl.classList.add('show');

        setTimeout(() => {
            toastEl.classList.remove('show');
        }, 5000);
    }

    // 加分API调用函数（增强版，带动画）
    async function addScore(score) {
        try {
            const response = await fetch('{{ url_for('api.add_score') }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({score: score})
            });
            const data = await response.json();
            if (data.success) {
                // 更新页面积分显示并添加动画
                const scoreEl = document.getElementById('total-score');
                scoreEl.textContent = data.new_score;
                scoreEl.classList.add('animate');
                setTimeout(() => scoreEl.classList.remove('animate'), 500);

                // 显示加分提示
                showFeedback(`+${score} Points Earned! 🎉`, 'success');
                return true;
            } else {
                showFeedback(`❌ ${data.msg}`, 'danger');
                return false;
            }
        } catch (error) {
            showFeedback('❌ Failed to update score', 'danger');
            return false;
        }
    }

    // 更新生命值显示
    function updateHealthBar() {
        const healthHearts = document.querySelectorAll('.health-heart');
        healthHearts.forEach((heart, index) => {
            if (index >= gameState.attemptsLeft) {
                heart.classList.add('empty');
            } else {
                heart.classList.remove('empty');
            }
        });

        // 生命值为0时的提示
        if (gameState.attemptsLeft <= 0) {
            showFeedback('❌ Out of lives! Please try again later or use a hint.', 'danger');
            // 禁用提交按钮
            if (GAME_CONFIG.levelType === 'choice') {
                document.getElementById('submit-choice').disabled = true;
            } else if (GAME_CONFIG.levelType === 'drag') {
                document.getElementById('submit-drag').disabled = true;
            } else if (GAME_CONFIG.levelType === 'code') {
                document.getElementById('submit-btn').disabled = true;
            }
        }
    }

    // 初始化计时奖励条
    function initTimerBar() {
        const timerProgress = document.getElementById('timer-progress');
        const timeBonusEl = document.getElementById('time-bonus');

        if (!timerProgress) return;

        // 设置计时条动画时长
        timerProgress.style.transition = `width ${GAME_CONFIG.timeBonusDuration}s linear`;

        // 开始倒计时
        setTimeout(() => {
            timerProgress.style.width = '0%';
            gameState.timeBonusAvailable = false;
            timeBonusEl.textContent = 'Time Bonus Expired! ⏰';
            timeBonusEl.style.color = 'var(--danger-color)';
        }, 100);
    }

    // 跳转到下一关（增强版）
    function goToNextLevel() {
        playSound('sound-levelup');
        showFeedback('🎉 Level Complete! Moving to next challenge...', 'success');

        const allLevels = {{ all_levels|map(attribute='id')|list|tojson | default('[]') }};
        const currentIndex = allLevels.indexOf(GAME_CONFIG.currentLevel);
        if (currentIndex < allLevels.length - 1) {
            setTimeout(() => {
                window.location.href = `{{ url_for('main.game') }}?level_id=${allLevels[currentIndex + 1]}`;
            }, 2000);
        } else {
            setTimeout(() => {
                window.location.href = '{{ url_for('main.student_stats') }}';
            }, 2000);
        }
    }

    // 页面加载完成后初始化
    document.addEventListener('DOMContentLoaded', () => {
        // 隐藏加载动画
        setTimeout(() => {
            const loader = document.getElementById('level-loader');
            loader.style.opacity = 0;
            setTimeout(() => loader.remove(), 500);
        }, 1000);

        // 初始化生命值
        updateHealthBar();

        // 初始化计时奖励
        initTimerBar();

        // 原有：编程关初始化
        if (GAME_CONFIG.levelType === 'code') {
            initGame();

            // 为提交按钮添加音效
            document.getElementById('submit-btn').addEventListener('click', () => {
                playSound('sound-click');
            });
        }
        // 优化：选择题初始化
        else if (GAME_CONFIG.levelType === 'choice') {
            // 选项点击交互
            document.querySelectorAll('.choice-option').forEach(option => {
                option.addEventListener('click', function() {
                    playSound('sound-click');
                    // 单选逻辑
                    if (GAME_CONFIG.extraConfig.question_type === 'single') {
                        document.querySelectorAll('.choice-option').forEach(opt => {
                            opt.classList.remove('selected');
                        });
                    }
                    this.classList.add('selected');
                });
            });

            document.getElementById('submit-choice').addEventListener('click', async () => {
                playSound('sound-click');

                // 容错检查
                if (!GAME_CONFIG.extraConfig || !GAME_CONFIG.extraConfig.correct_answer) {
                    showFeedback('❌ Question configuration error! Please contact the administrator.', 'danger');
                    return;
                }
                if (!GAME_CONFIG.extraConfig.options || Object.keys(GAME_CONFIG.extraConfig.options).length === 0) {
                    showFeedback('⚠️ No options available for this question!', 'warning');
                    return;
                }

                // 生命值检查
                if (gameState.attemptsLeft <= 0) {
                    showFeedback('❌ No lives left!', 'danger');
                    return;
                }

                const formData = new FormData(document.getElementById('choice-form'));
                const answers = Array.from(formData.getAll('answer')).sort();
                const correctAnswer = GAME_CONFIG.extraConfig.correct_answer
                    .toString().split(',').map(a => a.trim()).sort();

                if (answers.length === 0) {
                    showFeedback('⚠️ Please select an answer!', 'warning');
                    return;
                }

                if (JSON.stringify(answers) === JSON.stringify(correctAnswer)) {
                    // 答案正确
                    playSound('sound-correct');

                    // 计算总分（基础分 + 时间奖励）
                    let totalScore = GAME_CONFIG.extraConfig.score || 0;
                    if (gameState.timeBonusAvailable) {
                        totalScore += GAME_CONFIG.timeBonusPoints;
                        showFeedback(`✅ Correct! +${GAME_CONFIG.extraConfig.score || 0} Points +${GAME_CONFIG.timeBonusPoints} Time Bonus!`, 'success');
                    } else {
                        showFeedback(`✅ Correct! +${totalScore} Points!`, 'success');
                    }

                    // 加分
                    const scoreAdded = await addScore(totalScore);
                    if (scoreAdded) {
                        // 标记关卡完成
                        gameState.hasCompletedLevel = true;

                        // 无提示成就
                        const usedHintCount = parseInt(localStorage.getItem(`hint_${GAME_CONFIG.currentLevel}`) || '0');
                        if (usedHintCount === 0 && !gameState.hasEarnedNoHintBadge) {
                            showAchievement('No Hints Used! 🧠');
                            gameState.hasEarnedNoHintBadge = true;
                        }

                        // 快速答题成就
                        if (gameState.timeBonusAvailable) {
                            showAchievement('Fast Answer! ⚡');
                        }

                        // 更新选项样式
                        document.querySelectorAll('.choice-option').forEach(option => {
                            const optionKey = option.dataset.option;
                            if (correctAnswer.includes(optionKey)) {
                                option.classList.add('correct');
                            }
                        });

                        // 更新进度为通关
                        const progress = {{ current_user.get_progress()|tojson | default('{}') }};
                        progress[GAME_CONFIG.currentLevel] = 'passed';
                        fetch('{{ url_for('api.update_progress') }}', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({progress: progress})
                        });

                        // 跳转到下一关
                        setTimeout(goToNextLevel, 2000);
                    }
                } else {
                    // 答案错误
                    playSound('sound-incorrect');
                    gameState.attemptsLeft--;
                    updateHealthBar();

                    // 更新选项样式
                    document.querySelectorAll('.choice-option').forEach(option => {
                        const optionKey = option.dataset.option;
                        if (answers.includes(optionKey) && !correctAnswer.includes(optionKey)) {
                            option.classList.add('incorrect');
                        }
                    });

                    showFeedback(`❌ Wrong answer! ${gameState.attemptsLeft} lives left.`, 'danger');
                }
            });
        }
        // 优化：拖拽题初始化
        else if (GAME_CONFIG.levelType === 'drag') {
            // 容错检查
            if (!GAME_CONFIG.extraConfig || !GAME_CONFIG.extraConfig.targets || !GAME_CONFIG.extraConfig.draggables) {
                showFeedback('❌ Drag & drop configuration error!', 'danger');
                return;
            }

            // 初始化拖拽列表
            const draggableList = document.getElementById('draggable-list');
            new Sortable(draggableList, {
                group: 'shared',
                animation: 150,
                ghostClass: 'bg-light',
                onStart: () => playSound('sound-click')
            });

            // 初始化目标区域
            document.querySelectorAll('.drop-area').forEach(area => {
                new Sortable(area, {
                    group: 'shared',
                    animation: 150,
                    ghostClass: 'bg-primary/10',
                    onAdd: function() {
                        this.el.classList.add('filled');
                        // 限制每个目标区只能有一个拖拽项
                        if (this.el.children.length > 1) {
                            this.el.removeChild(this.el.firstChild);
                        }
                    },
                    onRemove: function() {
                        if (this.el.children.length === 0) {
                            this.el.classList.remove('filled');
                        }
                    },
                    onOver: function() {
                        this.el.classList.add('hovering');
                    },
                    onOut: function() {
                        this.el.classList.remove('hovering');
                    }
                });
            });

            // 提交验证
            document.getElementById('submit-drag').addEventListener('click', async () => {
                playSound('sound-click');

                // 生命值检查
                if (gameState.attemptsLeft <= 0) {
                    showFeedback('❌ No lives left!', 'danger');
                    return;
                }

                let isAllCorrect = true;
                let emptyTargets = false;

                document.querySelectorAll('.drop-area').forEach(area => {
                    const targetId = area.dataset.target;
                    const draggable = area.querySelector('.draggable-item');

                    if (draggable) {
                        const correctTarget = draggable.dataset.correct;
                        if (correctTarget !== targetId) {
                            isAllCorrect = false;
                            area.classList.add('error');
                            setTimeout(() => area.classList.remove('error'), 1000);
                        }
                    } else if (targetId) {
                        // 目标区未匹配拖拽项
                        isAllCorrect = false;
                        emptyTargets = true;
                        area.classList.add('error');
                        setTimeout(() => area.classList.remove('error'), 1000);
                    }
                });

                if (isAllCorrect) {
                    // 匹配正确
                    playSound('sound-correct');

                    // 计算总分
                    let totalScore = GAME_CONFIG.extraConfig.score || 0;
                    if (gameState.timeBonusAvailable) {
                        totalScore += GAME_CONFIG.timeBonusPoints;
                    }

                    // 加分
                    const scoreAdded = await addScore(totalScore);
                    if (scoreAdded) {
                        gameState.hasCompletedLevel = true;

                        // 成就提示
                        const usedHintCount = parseInt(localStorage.getItem(`hint_${GAME_CONFIG.currentLevel}`) || '0');
                        if (usedHintCount === 0 && !gameState.hasEarnedNoHintBadge) {
                            showAchievement('Perfect Match! 🏆');
                            gameState.hasEarnedNoHintBadge = true;
                        }

                        showFeedback(`✅ All matches correct! +${totalScore} Points!`, 'success');

                        // 更新进度为通关
                        const progress = {{ current_user.get_progress()|tojson | default('{}') }};
                        progress[GAME_CONFIG.currentLevel] = 'passed';
                        fetch('{{ url_for('api.update_progress') }}', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({progress: progress})
                        });

                        // 跳转到下一关
                        setTimeout(goToNextLevel, 2000);
                    }
                } else {
                    // 匹配错误
                    playSound('sound-incorrect');
                    gameState.attemptsLeft--;
                    updateHealthBar();

                    if (emptyTargets) {
                        showFeedback(`❌ Some targets are empty! ${gameState.attemptsLeft} lives left.`, 'danger');
                    } else {
                        showFeedback(`❌ Wrong matches! ${gameState.attemptsLeft} lives left.`, 'danger');
                    }
                }
            });
        }

        // 为所有按钮添加点击音效
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!btn.disabled) {
                    playSound('sound-click');
                }
            });
        });
    });
</script>
{% endblock %}
