"""Sinh _src/hoi-dap.body.html từ faq-content.ts của bản clone (chỉ đọc file clone)."""
import re

SRC = 'C:/Users/PC/Desktop/clone-nirvana/src/lib/faq-content.ts'
src = open(SRC, encoding='utf-8').read()
body = src[src.index('export const FAQ_GROUPS'):]

groups = []
for gm in re.finditer(r'category:\s*"([^"]+)",\s*items:\s*\[(.*?)\n    \],', body, re.S):
    items = []
    for im in re.finditer(r'q:\s*"([^"]+)",\s*a:\s*\[(.*?)\],', gm.group(2), re.S):
        items.append((im.group(1), re.findall(r'"([^"]*)"', im.group(2))))
    groups.append((gm.group(1), items))
print([len(i) for g, i in groups])

ids = ['thong-tin', 'khu-mo', 'ho-so', 'quyen-an-tang', 'thanh-toan']
tel = lambda t: t.replace('0818 555 444', '<a href="tel:0818555444">0818 555 444</a>')
nav = '\n'.join(f'      <a href="#{ids[k]}">{g}<span>{len(it)}</span></a>' for k, (g, it) in enumerate(groups))
secs = ''
for k, (g, it) in enumerate(groups):
    secs += f'\n    <section class="fgroup" id="{ids[k]}">\n      <h2>{g}</h2>\n'
    for q, a in it:
        ps = ''.join(f'<p>{tel(x)}</p>' for x in a)
        secs += f'      <details><summary>{q}</summary><div class="ans">{ps}</div></details>\n'
    secs += '    </section>'
total = sum(len(i) for _, i in groups)

out = f'''<section class="phero">
  <img src="assets/img/vinh-hang-dai-2.jpg" alt="Vĩnh Hằng Đài giữa vòng xoay cây xanh">
  <div class="wrap">
    <nav class="crumb" aria-label="Đường dẫn"><a href="trang-chu.html">Trang chủ</a><span>/</span>Hỏi & đáp</nav>
    <h1>Hỏi & đáp</h1>
    <p>Giải đáp những thắc mắc thường gặp tại Hoa Viên Bình Dương</p>
  </div>
</section>

<section class="sec"><div class="wrap faq">
  <aside class="fnav">
    <label class="fsearch"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input type="search" id="faq-q" placeholder="Tìm câu hỏi, ví dụ: thanh toán" aria-label="Tìm trong {total} câu hỏi"></label>
    <nav aria-label="Nhóm câu hỏi">
{nav}
    </nav>
    <div class="fcall"><small>Cần hỏi trực tiếp?</small><a href="tel:0818555444">0818 555 444</a><span>Tổng đài 24/7</span></div>
  </aside>
  <div class="flist">
    <p class="sr" id="faq-n" role="status"></p>
    <p class="fempty" id="faq-empty" hidden>Không tìm thấy câu hỏi phù hợp. Quý khách có thể gọi tổng đài <a href="tel:0818555444">0818 555 444</a> hoặc <a href="lien-he.html#gui-yeu-cau">gửi yêu cầu</a>.</p>{secs}
  </div>
</div></section>

<section class="ask-band"><div class="wrap">
  <div><h2>Chưa thấy câu trả lời quý khách cần?</h2><p>Gửi câu hỏi cho chúng tôi, nhân viên tư vấn sẽ liên hệ lại.</p></div>
  <div class="acts"><a class="btn btn-trang" href="lien-he.html#gui-yeu-cau">Gửi câu hỏi <svg width="18" height="18"><use href="#i-arrow"/></svg></a><a class="tel" href="tel:0818555444"><svg width="20" height="20"><use href="#i-phone"/></svg>0818 555 444</a></div>
</div></section>
'''
open('_src/hoi-dap.body.html', 'w', encoding='utf-8').write(out)
