import os
import shutil
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROLLS_DIR = os.path.join(BASE_DIR, "rolls")

def compress_image(src_path, dst_path, max_width=2048, quality=80):
    """将图片调整最大宽度并保存为轻量级 WebP 格式"""
    try:
        with Image.open(src_path) as img:
            # 处理图片旋转方向 (EXIF)
            img = ImageOps.exif_transpose(img) if hasattr(Image, 'exif_transpose') else img
            w, h = img.size
            if w > max_width:
                h = int(h * (max_width / w))
                img = img.resize((max_width, h), Image.Resampling.LANCZOS)
            
            # 转为 RGB 模式保存
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(dst_path, "WEBP", quality=quality, optimize=True)
    except Exception as e:
        print(f"  └─ 压缩失败 {os.path.basename(src_path)}: {e}")
        # 失败则直接复制原图
        shutil.copy2(src_path, dst_path)

def build_subfolder_index(folder_path, folder_name):
    sub_index_path = os.path.join(folder_path, "index.html")
    raw_dir = os.path.join(folder_path, "raw")        # 存放原图
    web_dir = os.path.join(folder_path, "images")     # 存放网页压缩图
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(web_dir, exist_ok=True)
    
    # 1. 移动根目录下的图片到 raw/
    for f in os.listdir(folder_path):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            shutil.move(os.path.join(folder_path, f), os.path.join(raw_dir, f))

    # 2. 检查 raw/ 里的原图，生成压缩图到 images/
    raw_images = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    raw_images.sort()
    
    web_images = []
    for img_name in raw_images:
        src_raw = os.path.join(raw_dir, img_name)
        base_name = os.path.splitext(img_name)[0]
        webp_name = f"{base_name}.webp"
        dst_web = os.path.join(web_dir, webp_name)
        
        # 如果网页图不存在，自动生成压缩版
        if not os.path.exists(dst_web):
            print(f"  └─ 正在为网页压缩图片: {img_name} -> {webp_name}")
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
body {{
  margin: 0;
  background: #111;
  color: #ddd;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

h1 {{ text-align: center; font-size: 18px; margin: 14px 0 4px; font-weight: 500; }}
.intro {{ text-align: center; font-size: 11px; color: #777; margin-bottom: 4px; }}
.meta {{ text-align: center; font-size: 12px; color: #666; margin-bottom: 12px; }}

.gallery {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 6px;
  padding: 6px;
}}

.gallery img {{
  width: 100%;
  display: block;
  cursor: pointer;
  background: #1a1a1a;
  transition: transform 0.15s ease, opacity 0.15s ease;
  box-shadow: 0 1px 4px rgba(0,0,0,0.4);
  user-select: none;
  -webkit-touch-callout: none;
}}

.gallery img:hover {{ transform: scale(1.02); opacity: 0.9; }}

.viewer {{
  position: fixed;
  inset: 0;
  background: #0b0b0b;
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 999;
}}

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

def run():
    if not os.path.exists(ROLLS_DIR):
        os.makedirs(ROLLS_DIR)

    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path) and item not in ["rolls", ".git", ".vscode"]:
            target_path = os.path.join(ROLLS_DIR, item)
            shutil.move(item_path, target_path)
            print(f"📁 归档新胶片: {item}")

    folders = [f for f in os.listdir(ROLLS_DIR) if os.path.isdir(os.path.join(ROLLS_DIR, f))]
    
    for folder in folders:
        print(f"\n🔍 处理胶片卷目录: {folder}")
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

    print("\n✅ 所有图片压缩与 index.html 网页更新完成！")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"运行出错: {e}")
    input("\n按回车键退出...")