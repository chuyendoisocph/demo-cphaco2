"""Tạo bản ảnh nhỏ (640w, 1080w) trong assets/img/r/ cho srcset. Chạy lại khi thêm ảnh: python _src/gen_sizes.py"""
import glob, os
from PIL import Image
WIDTHS = (640, 1080)
for p in glob.glob('assets/img/**/*.jpg', recursive=True):
    p = p.replace(os.sep, '/')
    if '/r/' in p: continue
    im = Image.open(p)
    if im.width <= 1180: continue
    rel = p[len('assets/img/'):-4]
    for w in WIDTHS:
        out = f'assets/img/r/{rel}-{w}.jpg'
        if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(p): continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im.convert('RGB').resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(out, quality=80, progressive=True, optimize=True)
print('ok')
