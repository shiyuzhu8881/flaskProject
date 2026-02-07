// 全局工具函数
window.utils = {
    // 显示消息提示
    showToast: function(message, type = 'success') {
        const toastContainer = document.createElement('div');
        toastContainer.className = `toast position-fixed top-20 end-3 z-50 bg-${type} text-white`;
        toastContainer.setAttribute('role', 'alert');
        toastContainer.setAttribute('aria-live', 'assertive');
        toastContainer.setAttribute('aria-atomic', 'true');
        toastContainer.innerHTML = `
            <div class="toast-body">
                ${message}
            </div>
        `;
        document.body.appendChild(toastContainer);

        const toast = new bootstrap.Toast(toastContainer);
        toast.show();

        // 3秒后自动移除
        setTimeout(() => {
            toast.hide();
            setTimeout(() => {
                document.body.removeChild(toastContainer);
            }, 500);
        }, 3000);
    }
};

// 全局错误处理
window.addEventListener('unhandledrejection', function(event) {
    console.error('未捕获的Promise错误:', event.reason);
    utils.showToast('系统出错，请刷新页面重试', 'danger');
});