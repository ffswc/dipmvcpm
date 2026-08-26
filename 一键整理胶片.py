import os
import shutil

# 获取根目录与 rolls 目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROLLS_DIR = os.path.join(BASE_DIR, "rolls")

def run():
    if not os.path.exists(ROLLS_DIR):
        os.makedirs(ROLLS_DIR)

    # 1. 自动将根目录下错放的胶片文件夹移动到 rolls 文件夹内
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path) and item not in ["rolls", ".git", ".vscode"]:
            target_path = os.path.join(ROLLS_DIR, item)
            shutil.move(item_path, target_path)
            print(f"📁 已将文件夹 [{item}] 归档至 rolls/")

    # 2. 扫描 rolls 目录下的所有胶片文件夹并排序
    folders = [f for f in os.listdir(ROLLS_DIR) if os.path.isdir(os.path.join(ROLLS_DIR, f))]
    folders.sort(reverse=True)

    # 3. 生成 index.html 网页内容
    links_html = ""
    for folder in folders:
        links_html += f'''  <a class="roll" href="./{folder}/">
    <span>{folder}</span>
    <small>Roll</small>
  </a>\n'''

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Film Rolls Index</title>
<style>
body {{ margin: 0; background: #111; color: #ddd; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
h1 {{ text-align: center; font-size: 18px; margin: 16px 0 6px; font-weight: 500; }}
.note {{ text-align: center; font-size: 12px; color: #777; margin-bottom: 14px; }}
.list {{ max-width: 720px; margin: 0 auto; padding: 0 10px 30px; }}
.roll {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; border-bottom: 1px solid #222; text-decoration: none; color: #ddd; }}
.roll:hover {{ background: #181818; }}
.roll span {{ font-size: 14px; letter-spacing: 0.3px; }}
.roll small {{ font-size: 11px; color: #888; }}
</style>
</head>
<body>

<h1>Film Rolls</h1>
<div class="note">Noritsu HS1800 · Roll Archive</div>

<div class="list">
{links_html}</div>

</body>
</html>'''

    # 4. 写入到 rolls/index.html
    target_index = os.path.join(ROLLS_DIR, "index.html")
    with open(target_index, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("\n🎉 成功！`rolls/index.html` 网页已更新！")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"运行出错: {e}")
    input("\n按回车键退出...")