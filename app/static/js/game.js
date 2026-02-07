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
        indentWithTabs: false
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
    submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> 校验中...';
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
            feedbackEl.className = 'alert alert-success';
            feedbackEl.innerHTML = `<i class="fa fa-check-circle"></i> ${result.msg}`;
            // 播放通关动画（简化版）
            playSuccessAnimation();
            // 延迟跳转下一关卡
            if (result.next_level) {
                setTimeout(() => {
                    window.location.reload(); // 刷新页面加载下一关卡
                }, 2000);
            }
        } else {
            feedbackEl.className = 'alert alert-danger';
            feedbackEl.innerHTML = `<i class="fa fa-exclamation-circle"></i> ${result.msg}`;
        }
    } catch (error) {
        feedbackEl.className = 'alert alert-danger';
        feedbackEl.innerHTML = '<i class="fa fa-exclamation-circle"></i> 提交失败，请刷新页面重试';
        console.error('提交失败:', error);
    } finally {
        // 恢复按钮状态
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa fa-check"></i> 施工检查（提交代码）';
    }
}

// 获取关卡提示
async function getHint() {
    const hintBtn = document.getElementById('hint-btn');
    hintBtn.disabled = true;
    hintBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> 加载中...';

    try {
        const response = await fetch(`/api/get-hint/${GAME_CONFIG.currentLevel}`);
        const result = await response.json();
        if (result.status === 'success') {
            utils.showToast(result.hint, 'info');
            usedHintCount++;
        } else {
            utils.showToast(result.hint, 'danger');
        }
    } catch (error) {
        utils.showToast('获取提示失败，请重试', 'danger');
        console.error('获取提示失败:', error);
    } finally {
        hintBtn.disabled = false;
        hintBtn.innerHTML = '<i class="fa fa-lightbulb-o"></i> 获取提示';
    }
}

// 播放通关成功动画（简化版）
function playSuccessAnimation() {
    const container = document.querySelector('.game-container');
    const confettiCount = 100;
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
        confetti.style.width = `${Math.random() * 10 + 5}px`;
        confetti.style.height = `${Math.random() * 10 + 5}px`;
        confetti.style.animation = `fall ${Math.random() * 3 + 2}s linear forwards`;
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
            border-radius: 50%;
        }
        @keyframes fall {
            to {
                transform: translateY(100vh) rotate(720deg);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // 3秒后移除彩带动画
    setTimeout(() => {
        document.querySelectorAll('.confetti').forEach(el => el.remove());
        style.remove();
    }, 3000);
}