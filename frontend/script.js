// 配置后端API地址（部署后替换为Railway的URL）
const API_URL = 'https://your-backend-url.railway.app'; // 替换为你的Railway URL

let isConnected = false;

// 检查API连接状态
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            setConnected(true);
            return true;
        }
    } catch (error) {
        console.error('API连接失败:', error);
        setConnected(false);
        return false;
    }
}

function setConnected(status) {
    isConnected = status;
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const apiStatus = document.getElementById('apiStatus');
    
    if (status) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = '已连接';
        apiStatus.textContent = '正常';
        apiStatus.style.color = '#28a745';
    } else {
        statusDot.className = 'status-dot';
        statusText.textContent = '未连接';
        apiStatus.textContent = '离线';
        apiStatus.style.color = '#dc3545';
    }
}

// 发送消息
async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    const sendButton = document.getElementById('sendButton');
    
    if (!message) return;
    
    if (!isConnected) {
        alert('请先连接API服务器！');
        return;
    }
    
    // 禁用发送按钮
    sendButton.disabled = true;
    sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';
    
    // 添加用户消息
    addMessage(message, 'user');
    
    // 清空输入框
    input.value = '';
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessage(data.response, 'ai');
        } else {
            throw new Error(data.error || '请求失败');
        }
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessage(`抱歉，出错了：${error.message}`, 'ai');
    } finally {
        // 恢复发送按钮
        sendButton.disabled = false;
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> 发送';
    }
}

// 添加消息到聊天界面
function addMessage(content, type) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'content';
    
    if (type === 'user') {
        avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
        contentDiv.textContent = content;
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(avatarDiv);
    } else {
        avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
        contentDiv.innerHTML = formatMessage(content);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 格式化消息（简单的Markdown支持）
function formatMessage(text) {
    // 处理换行
    let formatted = text.replace(/\n/g, '<br>');
    
    // 简单的粗体
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 简单的斜体
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // 代码块
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    return formatted;
}

// 清空对话
function clearChat() {
    if (confirm('确定要清空对话吗？')) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="message ai-message">
                <div class="avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="content">
                    你好！我是AI助手，有什么可以帮你的吗？
                </div>
            </div>
        `;
    }
}

// 设置提示问题
function setHint(text) {
    document.getElementById('userInput').value = text;
    document.getElementById('userInput').focus();
}

// 回车发送消息
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 页面加载时检查状态
document.addEventListener('DOMContentLoaded', async () => {
    await checkApiStatus();
    
    // 每30秒检查一次连接状态
    setInterval(checkApiStatus, 30000);
});
