"""Sinh _src/bai-viet-<slug>.body.html cho từng bài, nội dung lấy từ bản clone (chỉ đọc).
Chạy trước build.py: python _src/gen_articles.py"""
import re, json

CLONE = 'C:/Users/PC/Desktop/clone-nirvana/src/lib/'
meta_src = open(CLONE + 'articles-content.ts', encoding='utf-8').read()
body_src = open(CLONE + 'articles-body.ts', encoding='utf-8').read()

FIELDS = ('title', 'date', 'category', 'excerpt', 'slug')
articles = []
for block in re.findall(r'\{\s*title:.*?image:[^\n]*\n\s*\}', meta_src[meta_src.index('ARTICLE_INPUTS'):], re.S):
    a = {f: re.search(f + r':\s*\n?\s*"([^"]*)"', block).group(1) for f in FIELDS}
    articles.append(a)

bodies = dict(re.findall(r'"([a-z0-9-]+)":\s*`(.*?)`', body_src, re.S))

# Ảnh đầu bài: cùng ảnh với trang danh sách (ảnh chụp thật trong Hoa Viên)
IMG = {
    'doi-phuong-hoang-chuyen-ve-mot-nguoi-biet-lo-truoc': ('assets/img/doi-phuong-hoang.jpg', 'Ảnh minh họa bài Đồi Phượng Hoàng'),
    'can-lam-gi-khi-co-nguoi-than-qua-doi': ('assets/img/care-team.jpg', 'Đội ngũ Hoa Viên tại khu mộ'),
    'an-tang-hay-hoa-tang': ('assets/img/lotus.jpg', 'Vĩnh Hằng Đài tại Hoa Viên Bình Dương'),
    'luu-giu-tro-cot-trang-nghiem': ('assets/img/columbarium-symmetric.jpg', 'Gian thờ và hộc lưu cốt tại Chùa Thiên Phước'),
    'chuan-bi-hau-su-tu-som': ('assets/img/articles/family-plot-aerial-front.jpg', 'Khu mộ gia đình nhìn từ trên cao'),
    'tham-vieng-va-cham-soc-mo-phan': ('assets/img/grave-care-2.jpg', 'Đội chăm sóc vệ sinh quanh các ngôi mộ'),
    'thanh-minh-va-truyen-thong-tuong-nho-to-tien': ('assets/img/dai-le-vu-lan.jpg', 'Các gia đình dự lễ tại Hoa Viên Bình Dương'),
}
# Liên kết theo chủ đề bài: dẫn sang trang dịch vụ liên quan
NEXT = {
    'Chuẩn bị từ sớm': ('chuan-bi-tu-som.html', 'Chuẩn bị từ sớm'),
    'Hướng dẫn dành cho gia đình': ('khi-co-nguoi-than-qua-doi.html', 'Khi có người thân qua đời'),
    'Lưu giữ tro cốt': ('luu-tro-cot.html', 'Dịch vụ lưu tro cốt'),
    'Chăm sóc khu mộ': ('dich-vu-khac.html#cham-soc', 'Chăm sóc khu mộ'),
    'Văn hóa tưởng niệm': ('su-kien.html', 'Sự kiện trong năm'),
}


def clean(html):
    html = html.replace('/images/hvbd/doi-phuong-hoang-chuyen-tro.webp', 'assets/img/articles/doi-phuong-hoang-chuyen-tro.jpg')
    html = html.replace('/images/hvbd/doi-phuong-hoang-ket.webp', 'assets/img/articles/doi-phuong-hoang-ket.jpg')
    lines = [l.strip() for l in html.strip().split('\n')]
    return '\n      '.join(l for l in lines if l)


def related(a):
    others = [o for o in articles if o['slug'] != a['slug']]
    same = [o for o in others if o['category'] == a['category']]
    return (same + [o for o in others if o not in same])[:3]


for a in articles:
    s = a['slug']
    img, alt = IMG[s]
    nh, nt = NEXT[a['category']]
    rel = ''.join(
        f'\n    <a href="bai-viet-{o["slug"]}.html"><div class="ph"><img src="{IMG[o["slug"]][0]}" alt=""></div>'
        f'<b>{o["title"]}</b><span>{o["category"]} · {o["date"]}</span></a>' for o in related(a))
    out = f'''<section class="art-head"><div class="wrap">
  <nav class="crumb" aria-label="Đường dẫn"><a href="trang-chu.html">Trang chủ</a><span>/</span><a href="bai-viet.html">Bài viết</a><span>/</span>{a["category"]}</nav>
  <p class="meta"><b>{a["category"]}</b> · {a["date"]}</p>
  <h1>{a["title"]}</h1>
  <p class="dek">{a["excerpt"]}</p>
</div></section>

<div class="wrap"><figure class="art-cover"><img src="{img}" alt="{alt}"></figure></div>

<section class="art-wrap"><div class="wrap art-grid">
  <article class="prose">
      {clean(bodies[s])}
  </article>
  <aside class="art-side">
    <div class="side-call"><small>Cần tư vấn thêm?</small><a href="tel:0818555444">0818 555 444</a><span>Tổng đài 24/7</span></div>
    <a class="side-next" href="{nh}"><small>Tìm hiểu thêm</small><b>{nt}</b><svg width="18" height="18"><use href="#i-arrow"/></svg></a>
    <a class="link" href="bai-viet.html"><svg width="16" height="16" style="transform:rotate(180deg)"><use href="#i-arrow"/></svg> Tất cả bài viết</a>
  </aside>
</div></section>

<section class="sec alt"><div class="wrap">
  <div class="sec-head"><div><h2 class="title">Bài viết liên quan</h2></div><a class="link" href="bai-viet.html">Tất cả bài viết <svg width="18" height="18"><use href="#i-arrow"/></svg></a></div>
  <div class="reads three">{rel}
  </div>
</div></section>
'''
    open(f'_src/bai-viet-{s}.body.html', 'w', encoding='utf-8').write(out)

json.dump([{k: a[k] for k in ('slug', 'title', 'excerpt')} for a in articles],
          open('_src/articles.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(articles), 'bai;', len(bodies), 'noi dung')
