import os
import re
from pathlib import Path
import chardet

# 配置项
TARGET_HREF = "/TingleGamePage/"
BASE_TAG_TEMPLATE = f'<base href="{TARGET_HREF}">'

def detect_encoding(file_path):
    """
    读取文件的前一部分字节来检测编码
    """
    with open(file_path, 'rb') as f:
        # 读取前 10000 个字节通常足够判断编码
        rawdata = f.read(10000)
        result = chardet.detect(rawdata)
        encoding = result['encoding']
        confidence = result['confidence']
        
        # 如果检测置信度太低，默认回退到 utf-8
        if not encoding or confidence < 0.7:
            return 'utf-8'
        return encoding

def process_html_file(file_path):
    """
    读取 HTML 文件，检查并插入 base 标签，保持原编码
    """
    # 1. 检测文件编码
    file_encoding = detect_encoding(file_path)
    
    try:
        # 2. 使用检测到的编码读取文件
        with open(file_path, 'r', encoding=file_encoding) as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取失败 ({file_encoding}): {file_path} - {e}")
        return

    # 3. 检查是否已经存在 <base ...> 标签
    if re.search(r'<base\s', content, re.IGNORECASE):
        print(f"⏭️ 已存在 base 标签，跳过: {file_path}")
        return

    # 4. 查找 <head> 标签
    head_match = re.search(r'<head[^>]*>', content, re.IGNORECASE)
    
    if head_match:
        insert_index = head_match.end()
        insertion = f"\n{BASE_TAG_TEMPLATE}"
        
        new_content = content[:insert_index] + insertion + content[insert_index:]
        
        # 5. 使用【相同的编码】写回文件
        try:
            with open(file_path, 'w', encoding=file_encoding) as f:
                f.write(new_content)
            print(f"✅ 已处理: {file_path} (编码: {file_encoding})")
        except Exception as e:
            print(f"❌ 写入失败: {file_path} - {e}")
    else:
        print(f"⚠️ 未找到 <head> 标签，跳过: {file_path}")

def main():
    script_dir = Path(__file__).parent.resolve()
    print(f"🔍 正在扫描路径: {script_dir}")
    
    count = 0
    for html_file in script_dir.rglob("*.html"):
        if html_file.name == __file__:
            continue
        process_html_file(html_file)
        count += 1
    
    print("-" * 30)
    print(f"🏁 扫描完成，共检查 {count} 个 HTML 文件。")

if __name__ == "__main__":
    main()