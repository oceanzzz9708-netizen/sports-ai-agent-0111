from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# 配置 CORS - 更安全的配置
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # 生产环境应该指定具体域名
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 从环境变量获取DeepSeek API密钥
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', "https://api.deepseek.com/v1/chat/completions")

# 验证环境变量
if not DEEPSEEK_API_KEY:
    logger.warning("DEEPSEEK_API_KEY 环境变量未设置！")

@app.before_request
def log_request_info():
    """记录请求信息"""
    logger.info(f"请求: {request.method} {request.path}")

@app.after_request
def add_cors_headers(response):
    """添加CORS头"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/')
def home():
    """首页路由"""
    return jsonify({
        "message": "AI Agent API is running",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat [POST]",
            "health": "/health [GET]",
            "info": "/ [GET]"
        }
    })

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """处理聊天请求"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
            
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        logger.info(f"收到消息: {user_message[:50]}...")
        
        # 检查API密钥
        if not DEEPSEEK_API_KEY:
            return jsonify({
                "error": "API key not configured",
                "response": "抱歉，服务端配置有误，请联系管理员。"
            }), 500
        
        # 调用DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "max_tokens": 2000
        }
        
        logger.info("调用DeepSeek API...")
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
        
        logger.info(f"API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            logger.info(f"AI回复长度: {len(ai_response)}")
            
            return jsonify({
                "response": ai_response,
                "status": "success",
                "usage": result.get('usage', {})
            })
        else:
            error_msg = f"API request failed: {response.status_code}"
            logger.error(f"{error_msg} - {response.text}")
            return jsonify({
                "error": error_msg,
                "details": response.text[:200] if response.text else "No response body",
                "response": "抱歉，AI服务暂时不可用，请稍后重试。"
            }), 500
            
    except requests.exceptions.Timeout:
        logger.error("API请求超时")
        return jsonify({
            "error": "Request timeout",
            "response": "请求超时，请稍后重试。"
        }), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {str(e)}")
        return jsonify({
            "error": f"Network error: {str(e)}",
            "response": "网络连接错误，请检查网络后重试。"
        }), 500
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}")
        return jsonify({
            "error": str(e),
            "response": "服务器内部错误，请稍后重试。"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    health_status = {
        "status": "healthy",
        "timestamp": os.getenv('RAILWAY_SNAPSHOT_ID', 'local'),
        "service": "ai-agent-api"
    }
    
    # 检查关键依赖
    try:
        # 测试API密钥
        if DEEPSEEK_API_KEY:
            health_status["api_key"] = "configured"
        else:
            health_status["api_key"] = "missing"
            health_status["status"] = "degraded"
            
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return jsonify(health_status), 200

@app.route('/info', methods=['GET'])
def info():
    """服务信息"""
    return jsonify({
        "service": "AI Agent API",
        "version": "1.0.0",
        "provider": "DeepSeek",
        "model": "deepseek-chat",
        "max_tokens": 2000,
        "support": "text only"
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"启动服务器: {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
