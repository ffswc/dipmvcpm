import os
import shutil
import re
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROLLS_DIR = os.path.join(BASE_DIR, "rolls")
LETTERS_DIR = os.path.join(BASE_DIR, "letters")

def compress_image(src_path, dst_path, max_width=2048, quality=80):
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
        shutil.copy2(src_path, dst_path)

def process_rolls():
    os.makedirs(ROLLS_DIR, exist_ok=True)
    ignore_dirs = ["rolls", "letters", ".git", ".vscode", "__pycache__"]
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path) and item not in ignore_dirs:
            shutil.move(item_path, os.path.join(ROLLS_DIR, item))

    folders = [f for f in os.listdir(ROLLS_DIR) if os.path.isdir(os.path.join(ROLLS_DIR, f))]
    
    for folder in folders:
        folder_path = os.path.join(ROLLS_DIR, folder)
        raw_dir = os.path.join(folder_path, "raw")
        web_dir = os.path.join(folder_path, "images")
        
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(web_dir, exist_ok=True)
        
        for source in [folder_path, web_dir]:
            for f in os.listdir(source):
                src_file = os.path.join(source, f)
                if os.path.isfile(src_file) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    dst_raw = os.path.join(raw_dir, f)
                    if not os.path.exists(dst_raw):
                        shutil.move(src_file, dst_raw)

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

        # 子页面（胶片画廊）响应式 CSS 适配
        sub_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>{folder}</title>
<style>
* {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
body {{ margin: 0; background: #0c0c0c; color: #a0a0a0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; min-height: 100vh; }}
.nav {{ padding: 20px; display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: 0 auto; }}
.back-link {{ font-size: 13px; color: #666; text-decoration: none; letter-spacing: 1px; }}
header {{ text-align: center; margin: 10px 0 30px; padding: 0 20px; }}
h1 {{ font-size: 20px; font-weight: 400; color: #eee; margin: 0 0 6px; word-break: break-all; }}
.meta {{ font-size: 11px; color: #444; font-family: monospace; letter-spacing: 1px; }}

/* 响应式网格：手机默认 2 列大图，屏幕变宽后自动增加列数 */
.gallery {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; padding: 0 12px 60px; max-width: 1000px; margin: 0 auto; }}
@media (min-width: 600px) {{
  .gallery {{ grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 0 20px 60px; }}
}}
@media (min-width: 900px) {{
  .gallery {{ grid-template-columns: repeat(4, 1fr); gap: 16px; }}
}}

.gallery img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; cursor: pointer; background: #161616; border-radius: 3px; opacity: 0.95; }}

.viewer {{ position: fixed; inset: 0; background: rgba(0,0,0,0.96); display: none; align-items: center; justify-content: center; z-index: 999; touch-action: manipulation; }}
.viewer.active {{ display: flex; }}
.viewer img {{ max-width: 95vw; max-height: 85vh; border-radius: 2px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); object-fit: contain; }}
.frame {{ position: absolute; bottom: 20px; font-size: 12px; color: #666; font-family: monospace; }}
</style>
</head>
<body>
<div class="nav"><a class="back-link" href="../">← INDEX</a></div>
<header>
  <h1>{folder}</h1>
  <div class="meta">{len(web_images)} FRAMES · NORITSU HS1800</div>
</header>
<div class="gallery" id="gallery"></div>
<div class="viewer" id="viewer">
  <img id="viewerImg">
  <div class="frame" id="frame"></div>
</div>
<script>
const images = [{js_image_list}];
const gallery = document.getElementById("gallery");
const viewer = document.getElementById("viewer");
const viewerImg = document.getElementById("viewerImg");
const frame = document.getElementById("frame");
let current = 0;
images.forEach((src, i) => {{
  const img = document.createElement("img");
  img.src = src; img.loading = "lazy";
  img.onclick = () => showImage(i);
  gallery.appendChild(img);
}});
function showImage(i) {{
  current = i; viewerImg.src = images[i];
  frame.textContent = `${{String(i + 1).padStart(2, '0')}} / ${{String(images.length).padStart(2, '0')}}`;
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
        with open(os.path.join(folder_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(sub_html)

    # 胶片主页 Responsive CSS
    folders.sort(reverse=True)
    links_html = "".join([f'  <a class="roll-card" href="./{f}/"><span class="title">{f}</span><span class="tag">ROLL</span></a>\n' for f in folders])
    
    rolls_index = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>Film Archives</title>
<style>
* {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
body {{ margin: 0; background: #0c0c0c; color: #a0a0a0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 0 16px 60px; min-height: 100vh; }}
.container {{ max-width: 680px; margin: 0 auto; }}
header {{ padding: 40px 0 24px; display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid #1a1a1a; }}
h1 {{ font-size: 20px; font-weight: 500; color: #eee; margin: 0; letter-spacing: 0.5px; }}
.subtitle {{ font-size: 11px; color: #444; margin-top: 4px; font-family: monospace; }}
.letters-btn {{ font-size: 12px; color: #888; text-decoration: none; padding: 5px 12px; border: 1px solid #222; border-radius: 16px; white-space: nowrap; }}
.list {{ margin-top: 8px; }}
.roll-card {{ display: flex; justify-content: space-between; align-items: center; padding: 18px 8px; border-bottom: 1px solid #141414; text-decoration: none; }}
.roll-card:active {{ background: #141414; }}
.title {{ font-size: 14px; color: #bbb; font-weight: 400; word-break: break-all; padding-right: 12px; }}
.tag {{ font-size: 10px; color: #333; font-family: monospace; letter-spacing: 1px; flex-shrink: 0; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>Film Archives</h1>
      <div class="subtitle">Noritsu HS1800 · Roll Gallery</div>
    </div>
    <a class="letters-btn" href="../letters/index.html">✉ Letters</a>
  </header>
  <div class="list">
{links_html}  </div>
</div>
</body>
</html>'''
    with open(os.path.join(ROLLS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(rolls_index)

def process_letters():
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
        
        letter_page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>{title}</title>
<style>
* {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
body {{ margin: 0; background: #0c0c0c; color: #b5b5b5; font-family: "Noto Serif SC", "Georgia", serif; line-height: 1.8; display: flex; justify-content: center; padding: 30px 18px 60px; min-height: 100vh; }}
.container {{ max-width: 560px; width: 100%; }}
.back {{ display: inline-block; color: #555; text-decoration: none; font-size: 12px; margin-bottom: 30px; font-family: -apple-system, sans-serif; }}
h1 {{ font-size: 20px; font-weight: 400; color: #ededed; margin-bottom: 6px; line-height: 1.3; }}
.date {{ font-size: 11px; color: #444; margin-bottom: 36px; font-family: monospace; }}
.content p {{ margin-bottom: 22px; font-size: 15px; color: #b5b5b5; text-align: justify; word-break: break-word; }}
</style>
</head>
<body>
<div class="container">
  <a class="back" href="./index.html">← BACK TO LETTERS</a>
  <h1>{title}</h1>
  <div class="date">{date_str}</div>
  <div class="content">
{content_html}
  </div>
</div>
</body>
</html>'''
        with open(os.path.join(LETTERS_DIR, html_name), "w", encoding="utf-8") as f:
            f.write(letter_page)
            
        items_html += f'''  <a class="letter-item" href="./{html_name}">
    <span class="title">{title}</span>
    <span class="date">{date_str}</span>
  </a>\n'''

    letters_index = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>Letters</title>
<style>
* {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
body {{ margin: 0; background: #0c0c0c; color: #a0a0a0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 0 16px 60px; }}
.container {{ max-width: 680px; margin: 0 auto; }}
header {{ padding: 40px 0 24px; display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid #1a1a1a; }}
h1 {{ font-size: 20px; font-weight: 500; color: #eee; margin: 0; }}
.subtitle {{ font-size: 11px; color: #444; margin-top: 4px; font-family: monospace; }}
.back-btn {{ font-size: 12px; color: #888; text-decoration: none; padding: 5px 12px; border: 1px solid #222; border-radius: 16px; white-space: nowrap; }}
.list {{ margin-top: 8px; }}
.letter-item {{ display: flex; justify-content: space-between; align-items: center; padding: 18px 8px; border-bottom: 1px solid #141414; text-decoration: none; }}
.letter-item:active {{ background: #141414; }}
.title {{ font-size: 14px; color: #bbb; word-break: break-all; padding-right: 12px; }}
.date {{ font-size: 11px; color: #444; font-family: monospace; flex-shrink: 0; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>Letters</h1>
      <div class="subtitle">Written Thoughts & Notes</div>
    </div>
    <a class="back-btn" href="../rolls/index.html">← Film Gallery</a>
  </header>
  <div class="list">
{items_html}  </div>
</div>
</body>
</html>'''
    with open(os.path.join(LETTERS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(letters_index)

if __name__ == "__main__":
    try:
        process_rolls()
        process_letters()
        print("📱 移动端与 PC 端全自适应响应式 UI 已完美更新！")
    except Exception as e:
        print(f"运行失败: {e}")