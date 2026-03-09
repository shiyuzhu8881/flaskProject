// 游戏全局变量
let htmlEditor, cssEditor;
let usedHintCount = 0;

// 初始化游戏
function initGame() {
    // 初始化代码编辑器
    initEditors();
    // 初始化实时预览
    updatePreview();
    // 绑定事件监听
    bindEvents();

    // 游戏化初始化：显示欢迎提示
    showGameNotification(`Welcome to Code Challenge! 🚀`, 'info');
}

// 初始化CodeMirror编辑器
function initEditors() {
    // HTML编辑器
    htmlEditor = CodeMirror.fromTextArea(document.getElementById('html-editor'), {
        mode: 'htmlmixed',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseTags: true,
        matchBrackets: true,
        indentUnit: 4,
        indentWithTabs: false,
        extraKeys: {
            // 新增：快捷键支持（游戏化）
            "Ctrl-S": function() { document.getElementById('submit-btn').click(); },
            "Cmd-S": function() { document.getElementById('submit-btn').click(); }
        }
    });

    // CSS编辑器
    cssEditor = CodeMirror.fromTextArea(document.getElementById('css-editor'), {
        mode: 'css',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        indentWithTabs: false
    });

    // 监听编辑器变化，实时更新预览
    htmlEditor.on('change', updatePreview);
    cssEditor.on('change', updatePreview);

    // 编辑器聚焦动画
    htmlEditor.on('focus', function() {
        this.getWrapperElement().style.boxShadow = '0 0 0 2px #0d6efd';
    });
    htmlEditor.on('blur', function() {
        this.getWrapperElement().style.boxShadow = 'none';
    });
    cssEditor.on('focus', function() {
        this.getWrapperElement().style.boxShadow = '0 0 0 2px #0d6efd';
    });
    cssEditor.on('blur', function() {
        this.getWrapperElement().style.boxShadow = 'none';
    });
}

// 实时更新预览区
function updatePreview() {
    const htmlCode = htmlEditor.getValue();
    const cssCode = cssEditor.getValue();
    const previewIframe = document.getElementById('preview-iframe');
    const previewDoc = previewIframe.contentDocument || previewIframe.contentWindow.document;

    // 拼接完整HTML
    const fullHtml = `
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>${cssCode}</style>
        </head>
        <body>${htmlCode}</body>
        </html>
    `;

    // 更新预览
    previewDoc.open();
    previewDoc.write(fullHtml);
    previewDoc.close();
}

// 绑定事件监听
function bindEvents() {
    // 提交按钮事件
    document.getElementById('submit-btn').addEventListener('click', submitCode);

    // 提示按钮事件
    document.getElementById('hint-btn').addEventListener('click', getHint);

    // 设备切换事件
    document.querySelectorAll('.device-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.device-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const device = this.dataset.device;
            adjustPreviewDevice(device);

            // 设备切换反馈
            showGameNotification(`Preview switched to ${device.toUpperCase()} mode!`, 'info');
        });
    });
}

// 调整预览设备模式
function adjustPreviewDevice(device) {
    const previewIframe = document.getElementById('preview-iframe');
    switch(device) {
        case 'pc':
            previewIframe.style.width = '100%';
            previewIframe.style.height = '100%';
            previewIframe.style.margin = '0';
            break;
        case 'pad':
            previewIframe.style.width = '768px';
            previewIframe.style.height = '1024px';
            previewIframe.style.margin = '0 auto';
            break;
        case 'phone':
            previewIframe.style.width = '375px';
            previewIframe.style.height = '667px';
            previewIframe.style.margin = '0 auto';
            break;
    }
}

// 提交代码到后端校验
async function submitCode() {
    const htmlCode = htmlEditor.getValue().trim();
    const cssCode = cssEditor.getValue().trim();
    const submitBtn = document.getElementById('submit-btn');
    const feedbackEl = document.getElementById('feedback');

    // 禁用按钮，防止重复提交
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Launching Code...';
    feedbackEl.className = 'alert d-none';

    try {
        // 发送请求到后端
        const response = await fetch('/api/submit-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: GAME_CONFIG.userId,
                level_id: GAME_CONFIG.currentLevel,
                html_code: htmlCode,
                css_code: cssCode,
                used_hint_count: usedHintCount
            })
        });

        const result = await response.json();

        // 显示反馈
        feedbackEl.classList.remove('d-none');
        if (result.is_passed) {
            playSound('sound-correct');
            feedbackEl.className = 'alert alert-success fade-in-up';
            feedbackEl.innerHTML = `<i class="fa fa-rocket"></i> ${result.msg}`;

            // 计算奖励
            let totalScore = 20;
            if (gameState && gameState.timeBonusAvailable) {
                totalScore += 10;
                feedbackEl.innerHTML += `<br><small>+10 Time Bonus Points! ⚡</small>`;
            }

            // 加分
            await addScore(totalScore);

            // 成就检查
            if (usedHintCount === 0) {
                showAchievement('Coding Master! No Hints Used 🧑‍💻');
            }

            // 播放通关动画
            playSuccessAnimation();

            // 更新进度
            const progress = JSON.parse(localStorage.getItem('progress') || '{}');
            progress[GAME_CONFIG.currentLevel] = 'passed';
            localStorage.setItem('progress', JSON.stringify(progress));

            // 延迟跳转下一关卡
            if (result.next_level) {
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            }
        } else {
            playSound('sound-incorrect');
            feedbackEl.className = 'alert alert-danger fade-in-up';
            feedbackEl.innerHTML = `<i class="fa fa-exclamation-circle"></i> ${result.msg}`;

            // 减少生命值
            if (gameState) {
                gameState.attemptsLeft--;
                updateHealthBar();

                if (gameState.attemptsLeft <= 0) {
                    feedbackEl.innerHTML += '<br><small>Out of lives! Use a hint or try again.</small>';
                    submitBtn.disabled = true;
                }
            }
        }
    } catch (error) {
        feedbackEl.className = 'alert alert-danger fade-in-up';
        feedbackEl.innerHTML = '<i class="fa fa-exclamation-circle"></i> Launch failed! Please refresh and try again.';
        console.error('提交失败:', error);
    } finally {
        // 恢复按钮状态
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa fa-rocket"></i> Launch Code (Test Your Work)';
    }
}

// 获取关卡提示
async function getHint() {
    const hintBtn = document.getElementById('hint-btn');
    hintBtn.disabled = true;
    hintBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading Hint...';

    try {
        const response = await fetch(`/api/get-hint/${GAME_CONFIG.currentLevel}`);
        const result = await response.json();
        if (result.status === 'success') {
            playSound('sound-hint');
            showFeedback(`💡 Hint: ${result.hint}`, 'info');
            usedHintCount++;
        } else {
            showFeedback(`❌ ${result.hint}`, 'danger');
        }
    } catch (error) {
        showFeedback('❌ Failed to get hint, please try again', 'danger');
        console.error('获取提示失败:', error);
    } finally {
        hintBtn.disabled = false;
        hintBtn.innerHTML = '<i class="fa fa-lightbulb-o"></i> Get Hint';
    }
}

// 播放通关成功动画（增强版）
function playSuccessAnimation() {
    const container = document.querySelector('.game-container');
    const confettiCount = 200; // 增加彩带数量

    // 多种形状的彩带
    const shapes = ['circle', 'square', 'triangle'];

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';

        // 随机样式
        const shape = shapes[Math.floor(Math.random() * shapes.length)];
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
        confetti.style.width = `${Math.random() * 15 + 5}px`;
        confetti.style.height = `${Math.random() * 15 + 5}px`;

        // 形状样式
        if (shape === 'circle') {
            confetti.style.borderRadius = '50%';
        } else if (shape === 'triangle') {
            confetti.style.clipPath = 'polygon(50% 0%, 0% 100%, 100% 100%)';
            confetti.style.width = `${Math.random() * 20 + 10}px`;
            confetti.style.height = `${Math.random() * 20 + 10}px`;
        }

        // 随机动画
        const fallDuration = Math.random() * 5 + 2;
        const delay = Math.random() * 2;
        confetti.style.animation = `fall ${fallDuration}s linear ${delay}s forwards`;
        confetti.style.transform = `rotate(${Math.random() * 360}deg)`;

        container.appendChild(confetti);
    }

    // 添加动画样式
    const style = document.createElement('style');
    style.innerHTML = `
        .confetti {
            position: fixed;
            top: -10px;
            z-index: 1000;
            pointer-events: none;
        }
        @keyframes fall {
            0% {
                transform: translateY(0) rotate(0deg);
                opacity: 1;
            }
            100% {
                transform: translateY(100vh) rotate(1440deg);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // 5秒后移除彩带动画
    setTimeout(() => {
        document.querySelectorAll('.confetti').forEach(el => el.remove());
        style.remove();
    }, 5000);
}

// 游戏通知提示
function showGameNotification(message, type = 'info') {
    const feedbackEl = document.getElementById('feedback');
    if (feedbackEl) {
        feedbackEl.innerHTML = message;
        feedbackEl.className = `mt-3 alert alert-${type} fade-in-up`;
        feedbackEl.classList.remove('d-none');

        setTimeout(() => {
            feedbackEl.classList.add('d-none');
        }, 3000);
    }
}
