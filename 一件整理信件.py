import os
import shutil
import re
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROLLS_DIR = os.path.join(BASE_DIR, "rolls")
LETTERS_DIR = os.path.join(BASE_DIR, "letters")

def compress_image(src_path, dst_path, max_width=2048, quality=80):
    """将图片调整最大宽度并保存为轻量级 WebP 格式"""
    try:
        with Image.open(src_path) as img:
            img = ImageOps.exif_transpose(img) if hasattr(Image, 'exif_transpose') else img
            w, h = img.size
            if w > max_width:
                h = int(h * (max_width / w))
                img = img.resize((max_width, h), Image.Resampling.LANCZOS)
            
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(dst_path, "WEBP", quality=quality, optimize=True)
    except Exception as e:
        print(f"  └─ 压缩失败 {os.path.basename(src_path)}: {e}")
        shutil.copy2(src_path, dst_path)

def build_subfolder_index(folder_path, folder_name):
    sub_index_path = os.path.join(folder_path, "index.html")
    raw_dir = os.path.join(folder_path, "raw")
    web_dir = os.path.join(folder_path, "images")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(web_dir, exist_ok=True)
    
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            shutil.move(os.path.join(folder_path, f), os.path.join(raw_dir, f))

    raw_images = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    raw_images.sort()
    
    web_images = []
    for img_name in raw_images:
        src_raw = os.path.join(raw_dir, img_name)
        base_name = os.path.splitext(img_name)[0]
        webp_name = f"{base_name}.webp"
        dst_web = os.path.join(web_dir, webp_name)
        
        if not os.path.exists(dst_web):
            compress_image(src_raw, dst_web)
            
        web_images.append(f"images/{webp_name}")

    js_image_list = ",\n".join([f'  "{img}"' for img in web_images])

    sub_html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{folder_name}</title>
<style>
body {{ margin: 0; background: #111; color: #ddd; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
h1 {{ text-align: center; font-size: 18px; margin: 14px 0 4px; font-weight: 500; }}
.intro {{ text-align: center; font-size: 11px; color: #777; margin-bottom: 4px; }}
.meta {{ text-align: center; font-size: 12px; color: #666; margin-bottom: 12px; }}
.gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 6px; padding: 6px; }}
.gallery img {{ width: 100%; display: block; cursor: pointer; background: #1a1a1a; transition: transform 0.15s ease, opacity 0.15s ease; box-shadow: 0 1px 4px rgba(0,0,0,0.4); user-select: none; -webkit-touch-callout: none; }}
.gallery img:hover {{ transform: scale(1.02); opacity: 0.9; }}
.viewer {{ position: fixed; inset: 0; background: #0b0b0b; display: none; align-items: center; justify-content: center; z-index: 999; }}
.viewer.active {{ display: flex; cursor: none; }}
.viewer img {{ max-width: 95%; max-height: 95%; box-shadow: 0 0 30px rgba(0,0,0,0.6); }}
.frame {{ position: absolute; top: 12px; right: 12px; font-size: 12px; color: #aaa; }}
.back-link {{ position: absolute; top: 12px; left: 12px; font-size: 12px; color: #777; text-decoration: none; }}
.back-link:hover {{ color: #ccc; }}
</style>
</head>
<body>
<a class="back-link" href="../">← Index</a>
<h1>{folder_name}</h1>
<p class="intro">Tap to view · Swipe / Click to browse</p>
<p class="meta">Roll Archive</p>
<div class="gallery" id="gallery"></div>
<div class="viewer" id="viewer">
  <div class="frame" id="frame"></div>
  <img id="viewerImg" decoding="async">
</div>
<script>
const images = [
{js_image_list}
];
const gallery = document.getElementById("gallery");
const viewer = document.getElementById("viewer");
const viewerImg = document.getElementById("viewerImg");
const frame = document.getElementById("frame");
let current = 0;
images.forEach((src, i) => {{
  const img = document.createElement("img");
  img.src = src;
  img.loading = "lazy";
  img.decoding = "async";
  img.onerror = () => img.style.opacity = 0.3;
  img.onclick = () => showImage(i);
  gallery.appendChild(img);
}});
function showImage(i) {{
  current = i;
  viewerImg.src = images[i];
  frame.textContent = String(i + 1).padStart(3, "0");
  viewer.classList.add("active");
}}
viewer.onclick = () => viewer.classList.remove("active");
document.addEventListener("keydown", e => {{
  if (!viewer.classList.contains("active")) return;
  if (e.key === "ArrowRight") showImage((current + 1) % images.length);
  if (e.key === "ArrowLeft") showImage((current - 1 + images.length) % images.length);
  if (e.key === "Escape") viewer.classList.remove("active");
}});
</script>
</body>
</html>'''

    with open(sub_index_path, "w", encoding="utf-8") as f:
        f.write(sub_html_content)

def process_letters():
    """自动创建 letters 目录，并把里面的 .txt 变成极简风网页"""
    os.makedirs(LETTERS_DIR, exist_ok=True)
    txt_files = [f for f in os.listdir(LETTERS_DIR) if f.endswith(".txt")]
    txt_files.sort(reverse=True)

    items_html = ""
    for txt in txt_files:
        txt_path = os.path.join(LETTERS_DIR, txt)
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        title = lines[0] if lines else "Untitled"
        content_lines = lines[1:] if len(lines) > 1 else []
        content_html = "\n".join([f"    <p>{p}</p>" for p in content_lines])
        
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", txt)
        date_str = date_match.group(0) if date_match else "Archive"
        html_name = os.path.splitext(txt)[0] + ".html"
        
        # 生成单封信页面
        letter_page_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title}</title>
<style>
body {{ margin: 0; background: #111; color: #ccc; font-family: -apple-system, BlinkMacSystemFont, "Noto Serif SC", serif; line-height: 1.8; display: flex; justify-content: center; padding: 40px 20px; }}
.container {{ max-width: 600px; width: 100%; }}
.back {{ display: inline-block; color: #555; text-decoration: none; font-size: 13px; margin-bottom: 30px; }}
.back:hover {{ color: #aaa; }}
h1 {{ font-size: 22px; font-weight: 400; color: #eee; margin-bottom: 8px; }}
.date {{ font-size: 12px; color: #555; margin-bottom: 40px; font-family: -apple-system, sans-serif; }}
.content p {{ margin-bottom: 24px; font-size: 15px; color: #bbb; word-break: break-word; }}
</style>
</head>
<body>
<div class="container">
  <a class="back" href="./index.html">← Letters Index</a>
  <h1>{title}</h1>
  <div class="date">{date_str}</div>
  <div class="content">{content_html}</div>
</div>
</body>
</html>'''
        with open(os.path.join(LETTERS_DIR, html_name), "w", encoding="utf-8") as f:
            f.write(letter_page_content)
            
        items_html += f'''  <a class="letter-item" href="./{html_name}">
    <span class="title">{title}</span>
    <span class="date">{date_str}</span>
  </a>\n'''

    # 生成信件列表主页
    letters_index_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Letters Archive</title>
<style>
body {{ margin: 0; background: #111; color: #ddd; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 40px 20px; display: flex; justify-content: center; }}
.container {{ max-width: 600px; width: 100%; }}
.back-main {{ display: inline-block; color: #555; text-decoration: none; font-size: 13px; margin-bottom: 20px; }}
.back-main:hover {{ color: #aaa; }}
h1 {{ font-size: 18px; font-weight: 500; margin-bottom: 6px; color: #eee; }}
.subtitle {{ font-size: 12px; color: #555; margin-bottom: 30px; }}
.letter-item {{ display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #1e1e1e; text-decoration: none; color: #ccc; }}
.letter-item:hover {{ opacity: 0.7; }}
.title {{ font-size: 14px; }}
.date {{ font-size: 12px; color: #555; }}
</style>
</head>
<body>
<div class="container">
  <a class="back-main" href="../rolls/index.html">← Film Rolls</a>
  <h1>Letters</h1>
  <div class="subtitle">Written thoughts & notes</div>
  <div class="list">
{items_html}  </div>
</div>
</body>
</html>'''
    with open(os.path.join(LETTERS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(letters_index_content)

def run():
    if not os.path.exists(ROLLS_DIR):
        os.makedirs(ROLLS_DIR)

    # 1. 归档新胶片
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path) and item not in ["rolls", "letters", ".git", ".vscode"]:
            shutil.move(item_path, os.path.join(ROLLS_DIR, item))

    # 2. 整理子胶片
    folders = [f for f in os.listdir(ROLLS_DIR) if os.path.isdir(os.path.join(ROLLS_DIR, f))]
    for folder in folders:
        build_subfolder_index(os.path.join(ROLLS_DIR, folder), folder)

    folders.sort(reverse=True)
    links_html = "".join([f'  <a class="roll" href="./{f}/"><span>{f}</span><small>Roll</small></a>\n' for f in folders])

    # 3. 生成含有顶部“信件跳转链接”的胶片主页
    main_html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Film Rolls Index</title>
<style>
body {{ margin: 0; background: #111; color: #ddd; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
.header {{ display: flex; justify-content: space-between; align-items: center; max-width: 720px; margin: 20px auto 0; padding: 0 16px; }}
.title-group {{ flex-grow: 1; text-align: center; margin-left: 50px; }}
h1 {{ font-size: 18px; margin: 0; font-weight: 500; }}
.note {{ font-size: 11px; color: #666; margin-top: 2px; }}
.letters-btn {{ font-size: 12px; color: #888; text-decoration: none; border: 1px solid #282828; padding: 4px 10px; border-radius: 4px; transition: all 0.2s; }}
.letters-btn:hover {{ color: #eee; border-color: #555; background: #1a1a1a; }}
.list {{ max-width: 720px; margin: 20px auto 0; padding: 0 10px 30px; }}
.roll {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; border-bottom: 1px solid #222; text-decoration: none; color: #ddd; }}
.roll:hover {{ background: #181818; }}
.roll span {{ font-size: 14px; letter-spacing: 0.3px; }}
.roll small {{ font-size: 11px; color: #888; }}
</style>
</head>
<body>

<div class="header">
  <div class="title-group">
    <h1>Film Rolls</h1>
    <div class="note">Noritsu HS1800 · Roll Archive</div>
  </div>
  <a class="letters-btn" href="../letters/index.html">✉ Letters</a>
</div>

<div class="list">
{links_html}</div>

</body>
</html>'''

    with open(os.path.join(ROLLS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(main_html_content)

    # 4. 自动生成信件板块
    process_letters()

    print("\n✅ 胶片主页与信件模块已全部更新完成！")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"运行出错: {e}")
    input("\n按回车键退出...")