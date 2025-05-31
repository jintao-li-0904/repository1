#!/usr/bin/env python3
"""
医疗产品短名称生成器 - 启动脚本
选择运行不同版本的应用
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import pandas
        import openpyxl
        return True
    except ImportError:
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("依赖安装完成！\n")

def main():
    print("="*60)
    print("🏥 医疗产品短名称生成器")
    print("="*60)
    
    # 检查依赖
    if not check_dependencies():
        print("⚠️  检测到缺少依赖包")
        response = input("是否自动安装依赖？(y/n): ")
        if response.lower() == 'y':
            install_dependencies()
        else:
            print("请手动运行: pip install -r requirements.txt")
            sys.exit(1)
    
    print("\n请选择运行模式：")
    print("1. Streamlit 应用 (推荐 - 功能最完整)")
    print("2. Gradio 应用 (简洁 - 支持公共分享)")
    print("3. Flask API (开发者 - RESTful API)")
    print("4. 命令行模式 (快速测试)")
    print("0. 退出")
    
    choice = input("\n请输入选择 (0-4): ").strip()
    
    if choice == '1':
        print("\n启动 Streamlit 应用...")
        print("提示：应用将在浏览器中自动打开")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_streamlit.py"])
        
    elif choice == '2':
        print("\n启动 Gradio 应用...")
        print("提示：将生成一个可分享的公共链接")
        subprocess.run([sys.executable, "app_gradio.py"])
        
    elif choice == '3':
        print("\n启动 Flask API...")
        print("提示：API 将运行在 http://localhost:5000")
        subprocess.run([sys.executable, "app_flask.py"])
        
    elif choice == '4':
        print("\n进入命令行模式...")
        from processor import CorrectedShortNameProcessor, print_result
        
        # 询问词典路径
        dict_path = input("请输入词典文件路径 (直接回车使用默认): ").strip()
        if not dict_path:
            dict_path = "/Users/lijintao/Desktop/merged_dictionary.xlsx"
        
        if Path(dict_path).exists():
            processor = CorrectedShortNameProcessor(dict_path)
            print(f"✅ 词典加载成功！")
        else:
            processor = CorrectedShortNameProcessor()
            print("⚠️  未找到词典文件，继续运行但不使用缩写")
        
        print("\n输入 'quit' 退出")
        print("-"*60)
        
        while True:
            description = input("\n输入产品描述: ").strip()
            if description.lower() in ['quit', 'exit', 'q']:
                break
            
            if description:
                result = processor.process_full_description(description)
                print_result(result)
    
    elif choice == '0':
        print("\n再见！")
        sys.exit(0)
    
    else:
        print("\n无效选择，请重试")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已终止")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
