"""
Canadian Medical Product Short Name Generator - Flask API
RESTful API 版本
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from pathlib import Path
from processor import CorrectedShortNameProcessor

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局处理器实例
processor = None

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>医疗产品短名称生成器 API</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .input-group {
            margin: 20px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            display: none;
        }
        .success {
            color: #28a745;
        }
        .error {
            color: #dc3545;
        }
        .api-docs {
            margin-top: 40px;
            padding: 20px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 医疗产品短名称生成器 API</h1>
        
        <div class="input-group">
            <label for="description">产品完整描述：</label>
            <textarea id="description" rows="3" placeholder="例如：Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex"></textarea>
        </div>
        
        <div class="input-group">
            <label for="dictionary">词典路径（可选）：</label>
            <input type="text" id="dictionary" placeholder="/path/to/dictionary.xlsx">
        </div>
        
        <button onclick="generateShortName()">生成短名称</button>
        
        <div id="result" class="result"></div>
        
        <div class="api-docs">
            <h2>API 文档</h2>
            
            <h3>1. 生成短名称</h3>
            <pre>
POST /api/generate
Content-Type: application/json

{
    "description": "Solution Dextrose 5% 500 milliliters Bottle Viaflex Non-Latex",
    "dictionary_path": "/path/to/dictionary.xlsx"  // 可选
}
            </pre>
            
            <h3>2. 加载词典</h3>
            <pre>
POST /api/load_dictionary
Content-Type: application/json

{
    "path": "/path/to/dictionary.xlsx"
}
            </pre>
            
            <h3>3. 获取状态</h3>
            <pre>
GET /api/status
            </pre>
        </div>
    </div>
    
    <script>
        async function generateShortName() {
            const description = document.getElementById('description').value;
            const dictionary = document.getElementById('dictionary').value;
            const resultDiv = document.getElementById('result');
            
            if (!description) {
                alert('请输入产品描述');
                return;
            }
            
            resultDiv.style.display = 'none';
            resultDiv.innerHTML = '处理中...';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        description: description,
                        dictionary_path: dictionary || null
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <h3 class="success">✅ 生成成功</h3>
                        <p><strong>短名称：</strong> ${data.short_name}</p>
                        <p><strong>字符数：</strong> ${data.character_count}/35</p>
                        <h4>组件分解：</h4>
                        <ul>
                            ${data.components.map(c => `
                                <li>位置 ${c.position_number} (${c.position}): 
                                    <strong>${c.value}</strong> ← ${c.original}
                                    ${c.mandatory ? ' (必填)' : ''}
                                </li>
                            `).join('')}
                        </ul>
                        ${data.messages.length > 0 ? `
                            <h4>消息：</h4>
                            <ul>
                                ${data.messages.map(m => `<li>${m}</li>`).join('')}
                            </ul>
                        ` : ''}
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <h3 class="error">❌ 生成失败</h3>
                        <p>${data.error || '未知错误'}</p>
                    `;
                }
                
                resultDiv.style.display = 'block';
                
            } catch (error) {
                resultDiv.innerHTML = `
                    <h3 class="error">❌ 请求失败</h3>
                    <p>${error.message}</p>
                `;
                resultDiv.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """显示简单的Web界面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取API状态"""
    global processor
    
    return jsonify({
        'status': 'running',
        'dictionary_loaded': processor is not None,
        'dictionary_path': processor.dictionary.loaded_from if processor else None,
        'abbreviation_count': len(processor.dictionary.abbreviations) if processor else 0
    })

@app.route('/api/load_dictionary', methods=['POST'])
def load_dictionary():
    """加载词典文件"""
    global processor
    
    data = request.get_json()
    dictionary_path = data.get('path')
    
    if not dictionary_path:
        return jsonify({
            'success': False,
            'error': '请提供词典文件路径'
        }), 400
    
    if not Path(dictionary_path).exists():
        return jsonify({
            'success': False,
            'error': f'文件不存在: {dictionary_path}'
        }), 404
    
    try:
        processor = CorrectedShortNameProcessor(dictionary_path)
        return jsonify({
            'success': True,
            'message': f'词典加载成功，共 {len(processor.dictionary.abbreviations)} 个缩写',
            'abbreviation_count': len(processor.dictionary.abbreviations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_short_name():
    """生成短名称"""
    global processor
    
    data = request.get_json()
    description = data.get('description', '').strip()
    dictionary_path = data.get('dictionary_path')
    
    if not description:
        return jsonify({
            'success': False,
            'error': '请提供产品描述'
        }), 400
    
    # 如果提供了新的词典路径，加载它
    if dictionary_path and Path(dictionary_path).exists():
        processor = CorrectedShortNameProcessor(dictionary_path)
    
    # 如果还没有处理器，创建一个不使用词典的处理器
    if processor is None:
        processor = CorrectedShortNameProcessor()  # 不使用词典
    
    try:
        # 处理描述
        result = processor.process_full_description(description)
        
        return jsonify({
            'success': result['success'],
            'original': result['original'],
            'short_name': result['short_name'],
            'character_count': result['character_count'],
            'components': result['components'],
            'messages': result['messages']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch', methods=['POST'])
def batch_generate():
    """批量生成短名称"""
    global processor
    
    data = request.get_json()
    descriptions = data.get('descriptions', [])
    dictionary_path = data.get('dictionary_path')
    
    if not descriptions:
        return jsonify({
            'success': False,
            'error': '请提供产品描述列表'
        }), 400
    
    # 加载词典
    if dictionary_path and Path(dictionary_path).exists():
        processor = CorrectedShortNameProcessor(dictionary_path)
    elif processor is None:
        processor = CorrectedShortNameProcessor()
    
    results = []
    for desc in descriptions:
        try:
            result = processor.process_full_description(desc)
            results.append({
                'original': desc,
                'short_name': result['short_name'],
                'success': result['success'],
                'character_count': result['character_count']
            })
        except Exception as e:
            results.append({
                'original': desc,
                'short_name': '',
                'success': False,
                'error': str(e)
            })
    
    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    })

if __name__ == '__main__':
    # 开发模式运行
    app.run(debug=True, host='0.0.0.0', port=5000)
