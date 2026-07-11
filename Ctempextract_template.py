import json
import re

# ファイルを読み込み
with open(r"C:\work\schedule-app\POC\teamschedulePOC.html", "r", encoding="utf-8") as f:
    content = f.read()

# テンプレートスクリプトタグを検索
template_match = re.search(r'<script type="__bundler/template">(.+?)</script>', content, re.DOTALL)
if template_match:
    template_json_str = template_match.group(1).strip()
    
    # JSON文字列をパース
    try:
        template_html = json.loads(template_json_str)
        
        # HTML構造を簡略化して表示
        html_lines = template_html.split('\n')
        
        # 主要な要素を抽出
        print("=== 主要なHTML要素 ===")
        for line in html_lines[:300]:
            if '<' in line and '>' in line:
                # タグのみを抽出
                tags = re.findall(r'<[^>]+>', line)
                for tag in tags:
                    if not any(c in tag for c in ['font-face', 'unicode-range']):
                        print(tag[:120])
                        
    except json.JSONDecodeError as e:
        print(f"JSON解析エラー: {e}")
        print(f"最初の500文字: {template_json_str[:500]}")
else:
    print("テンプレートスクリプトが見つかりません")
