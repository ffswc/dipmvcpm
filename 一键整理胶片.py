import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROLLS_DIR = os.path.join(BASE_DIR, "rolls")

def build_subfolder_index(folder_path, folder_name):
    """如果子胶片文件夹内没有 index.html，自动生成一个展示 images 目录下所有图片的 index.html"""
    sub_index_path = os.path.join(folder_path, "index.html")
    img_dir = os.path.join(folder_path, "images")
    
    # 兼容处理：如果没有 images 文件夹，但当前目录下有图片，自动创建 images 文件夹并把图片移进去
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        for f in os.listdir(folder_path):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                shutil.move(os.path.join(folder_path, f), os.path.join(img_dir, f))
    
    # 获取 images 目录下的所有图片文件名
    images = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    images.sort()
    
    # 动态生成图片标签
    img_tags = "\n".join([f'    <img src="./images/{img}" loading="lazy">' for img in images])
    
    sub_html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{folder_name}</title>
<style>
body {{ margin: 0; background: #111; color: #ddd; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; text-align: center; }}
h1 {{ font-size: 18px; margin: 20px 0; font-weight: 500; color: #eee; }}
.gallery {{ display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 0 10px 40px; }}
.gallery img {{ max-width: 100%; width: auto; max-height: 90vh; border-radius: 2px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
a.back {{ display: inline-block; margin: 15px 0; color: #888; text-decoration: none; font-size: 13px; }}
a.back:hover {{ color: #fff; }}
</style>
</head>
<body>
<a class="back" href="../">← Back to Rolls Index</a>
<h1>{folder_name}</h1>
<div class="gallery">
{img_tags}
</div>
</body>
</html>'''

    # 如果原文件夹没有 index.html，就写入新生成的
    if not os.path.exists(sub_index_path):
        with open(sub_index_path, "w", encoding="utf-8") as f:
            f.write(sub_html_content)
        print(f"✨ 已为 [{folder_name}] 自动生成子网页 index.html")

def run():
    if not os.path.exists(ROLLS_DIR):
        os.makedirs(ROLLS_DIR)

    # 1. 自动归档根目录下的胶片文件夹
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path) and item not in ["rolls", ".git", ".vscode"]:
            target_path = os.path.join(ROLLS_DIR, item)
            shutil.move(item_path, target_path)
            print(f"📁 已归档胶片: {item}")

    # 2. 遍历 rolls 文件夹，补齐各卷的 index.html，并更新主 index.html
    folders = [f for f in os.listdir(ROLLS_DIR) if os.path.isdir(os.path.join(ROLLS_DIR, f))]
    
    for folder in folders:
        folder_path = os.path.join(ROLLS_DIR, folder)
        build_subfolder_index(folder_path, folder)

    folders.sort(reverse=True)

    links_html = ""
    for folder in folders:
        links_html += f'''  <a class="roll" href="./{folder}/">
    <span>{folder}</span>
    <small>Roll</small>
  </a>\n'''

    main_html_content = f'''<!DOCTYPE html>
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

    target_index = os.path.join(ROLLS_DIR, "index.html")
    with open(target_index, "w", encoding="utf-8") as f:
        f.write(main_html_content)

    print("\n🎉 处理完毕！`rolls/index.html` 及各子页面均已就绪！")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"运行出错: {e}")
    input("\n按回车键退出...")