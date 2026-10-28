"""Sinh thân trang Chính sách quyền riêng tư và Tham quan 360° từ _src/extra.json
(dữ liệu lấy từ bản clone bằng: node _src/extract_ts.mjs). Chạy trước build.py."""
import json, html

D = json.load(open('_src/extra.json', encoding='utf-8'))
e = html.escape

# ===== Chính sách quyền riêng tư =====
toc, secs = [], []
for n, it in enumerate(D['privacy'], 1):
    sid = f'muc-{n}'
    toc.append(f'<a href="#{sid}">{e(it["title"])}</a>')
    out = []
    for b in it['blocks']:
        if b['type'] == 'p':
            lead = f'<b class="lead-no">{e(b["lead"])}</b> ' if b.get('lead') else ''
            cls = ' class="note"' if b.get('emphasis') else ''
            out.append(f'<p{cls}>{lead}{e(b["text"])}</p>')
        elif b['type'] == 'list':
            out.append('<ul>' + ''.join(f'<li>{e(x)}</li>' for x in b['items']) + '</ul>')
        elif b['type'] == 'contact':
            rows = []
            for r in b['rows']:
                v = e(r['value'])
                if r.get('href'):
                    v = f'<a href="{"lien-he.html#gui-yeu-cau" if r["href"] == "/lien-he" else r["href"]}">{v}</a>'
                rows.append(f'<div><dt>{e(r["label"])}</dt><dd>{v}</dd></div>')
            out.append('<dl class="contact">' + ''.join(rows) + '</dl>')
    secs.append(f'<section id="{sid}"><h2>{e(it["title"])}</h2>\n      ' + '\n      '.join(out) + '\n    </section>')

open('_src/chinh-sach-quyen-rieng-tu.body.html', 'w', encoding='utf-8').write(f'''<section class="phero">
  <img src="assets/img/thien-phuoc.jpg" alt="Chùa Thiên Phước trong khuôn viên Hoa Viên Bình Dương">
  <div class="wrap">
    <nav class="crumb" aria-label="Đường dẫn"><a href="trang-chu.html">Trang chủ</a><span>/</span>Chính sách quyền riêng tư</nav>
    <h1>Chính sách quyền riêng tư</h1>
    <p>Cách chúng tôi thu thập, sử dụng và bảo vệ dữ liệu cá nhân của quý khách</p>
  </div>
</section>

<section class="sec"><div class="wrap policy">
  <aside class="ptoc">
    <nav aria-label="Mục lục chính sách"><b>Nội dung</b>{"".join(toc)}</nav>
    <div class="fcall"><span>Thắc mắc về dữ liệu cá nhân</span><a href="tel:0818555444">0818 555 444</a></div>
  </aside>
  <article class="ptext">
    {chr(10).join("    " + s if i else s for i, s in enumerate(secs))}
  </article>
</div></section>
''')

# ===== Tham quan 360° =====
S = D['scenes']
GROUP = {'cong-trinh': 'Công trình', 'khu-mo': 'Khu mộ'}
def card(i, s):
    return (f'<button type="button" data-scene="{s["id"]}"><img src="assets/img/360/{s["thumbnail"].split("/")[-1]}" alt="" loading="lazy" decoding="async">'
            f'<span><small>Điểm {i + 1:02d}</small><b>{e(s["title"])}</b></span></button>')
lists = ''
for g, label in GROUP.items():
    items = [card(i, s) for i, s in enumerate(S) if s['group'] == g]
    lists += f'\n  <h3 class="tgroup">{label} <span>{len(items)} điểm</span></h3>\n  <div class="tlist">\n    ' + '\n    '.join(items) + '\n  </div>'
first = S[0]
open('_src/tham-quan-360.body.html', 'w', encoding='utf-8').write(f'''<link rel="stylesheet" href="assets/vendor/pannellum.css">
<section class="tour" aria-label="Ảnh toàn cảnh 360°">
  <div class="pano" id="pano" tabindex="0" aria-label="Ảnh 360°. Kéo chuột, vuốt hoặc dùng phím mũi tên để nhìn quanh."></div>
  <div class="tour-top">
    <nav class="crumb" aria-label="Đường dẫn"><a href="trang-chu.html">Trang chủ</a><span>/</span>Tham quan 360°</nav>
    <h1>Tham quan Hoa Viên 360°</h1>
    <p>Kéo để nhìn quanh. Bấm mũi tên trong ảnh để sang điểm kế bên.</p>
  </div>
  <div class="tour-cap">
    <div aria-live="polite"><small>Điểm <b id="t-no">01</b> / {len(S):02d} · <span id="t-grp">{GROUP[first["group"]]}</span></small>
    <h2 id="t-title">{e(first["title"])}</h2><p id="t-desc">{e(first["description"])}</p></div>
    <div class="tour-btns"><button type="button" id="t-prev" aria-label="Điểm tham quan trước"><svg width="18" height="18" style="transform:rotate(180deg)"><use href="#i-arrow"/></svg></button><button type="button" id="t-next">Tiếp: <span id="t-next-name"></span> <svg width="18" height="18"><use href="#i-arrow"/></svg></button></div>
  </div>
  <noscript><p class="tour-nojs">Cần bật JavaScript để xem ảnh 360°.</p></noscript>
</section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><h2 class="title">{len(S)} điểm tham quan</h2><p class="lead">Ảnh toàn cảnh chụp bằng flycam tại Hoa Viên Bình Dương. Chọn một điểm để mở.</p></div></div>{lists}
</div></section>
''')

json.dump([{k: s[k] for k in ('id', 'title', 'description', 'pitch', 'yaw', 'group', 'camera', 'links')} | {'blurredYaws': s.get('blurredYaws', []), 'pano': 'assets/img/360/' + s['panorama'].split('/')[-1]} for s in S],
          open('_src/tour.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok', len(D['privacy']), len(S))
