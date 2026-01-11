import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 获取DeepSeek API密钥
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    print("警告: DEEPSEEK_API_KEY 环境变量未设置!")

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "AI Agent API",
        "endpoints": ["/chat (POST)", "/health (GET)"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "缺少message参数"}), 400
        
        # 调用DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": data['message']}
            ]
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "response": result['choices'][0]['message']['content']
            })
        else:
            return jsonify({
                "error": f"API调用失败: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
