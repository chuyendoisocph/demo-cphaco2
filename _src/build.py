"""Ghép trang con: đầu/chân trang lấy từ trang-chu.html, thân trang lấy từ _src/<ten>.body.html."""
import sys,io
home=open('trang-chu.html',encoding='utf-8').read()
def cut(a,b,s=home): i=s.index(a); return s[i:s.index(b,i)]
header=cut('<body>','<main')
CTA=cut('<section class="cta" id="dat-lich">','</main>')
footer=cut('<footer>','<script>')

import hashlib,os,re,re as _re
# phiên bản theo nội dung file, để trình duyệt tải lại CSS/JS khi có thay đổi
ASSET_V=hashlib.md5(open('assets/site.css','rb').read()+open('assets/site.js','rb').read()).hexdigest()[:8]
def ver(html):
    return _re.sub(r'assets/site\.(css|js)(\?v=\w+)?',lambda m:'assets/site.'+m.group(1)+'?v='+ASSET_V,html)
_h=open('trang-chu.html',encoding='utf-8').read()


def resp(html):
    # ảnh trong nội dung: thêm srcset để điện thoại và thẻ nhỏ tải bản nhẹ (tạo bằng _src/gen_sizes.py)
    def one(m):
        tag=re.sub(r'srcset="assets/img/r/[^"]*" sizes="[^"]*" ','',m.group(0))  # trang chủ: tính lại
        if 'srcset=' in tag or 'fetchpriority' in tag or 'class="on"' in tag: return tag
        src=re.search(r'src="assets/img/([^"]+)\.jpg"',tag)
        if not src or not os.path.exists(f'assets/img/r/{src.group(1)}-640.jpg'): return tag
        r=f'assets/img/r/{src.group(1)}'
        # bề rộng hiển thị theo khung chứa ảnh: ảnh nền cả bề ngang, ảnh trong bài, còn lại nửa khung
        before=tail0[max(0,m.start()-90):m.start()]
        if re.search(r'class="(values|family|feat|mapbox|player)"[^<]*>\s*$',before): w='100vw'
        elif re.search(r'class="img"><$|<div class="img">\s*$',before): w='(max-width:760px) 100vw, 60vw'
        elif re.search(r'<figure>\s*$',before) and 'class="prose' in tail0[:m.start()]: w='(max-width:760px) 100vw, 850px'
        else: w='(max-width:760px) 100vw, 50vw'
        # Chrome tự đo bề rộng thật với ảnh tải chậm (sizes="auto"), trình duyệt khác dùng giá trị sau
        if 'loading="lazy"' in tag: w='auto, '+w
        return tag.replace('<img ',f'<img srcset="{r}-640.jpg 640w, {r}-1080.jpg 1080w, assets/img/{src.group(1)}.jpg 1920w" sizes="{w}" ',1)
    i=html.index('<main'); j=html.index('</section>',i)
    tail0=html[j:]
    tail=re.sub(r'<img [^>]*>',one,tail0)
    # ảnh nền khung đặt lịch phủ cả bề ngang: bỏ srcset
    tail=re.sub(r'(<section class="cta" id="dat-lich">\s*<img |<figure class="art-cover"><img )srcset="[^"]*" sizes="[^"]*" ',r'\1',tail)
    return html[:j]+tail

def svg(html):
    # icon trang trí: ẩn với trình đọc màn hình (chữ bên cạnh đã nói đủ nghĩa)
    return re.sub(r'<svg(?![^>]*(?:aria-hidden|aria-label|role)=)',r'<svg aria-hidden="true"',html)

def hero(html):
    # ảnh đầu trang con tải trước
    return re.sub(r'(<section class="phero[^"]*">\s*<img |<figure class="art-cover"><img )',r'\1fetchpriority="high" ',html,1)

def lazy(html):
    # ảnh nằm sau phần đầu trang chỉ tải khi cuộn tới
    i=html.index('<main'); j=html.index('</section>',i)
    tail=html[j:].replace('<img src=','<img loading="lazy" decoding="async" src=')
    tail=tail.replace('<figure class="art-cover"><img loading="lazy" decoding="async" src=','<figure class="art-cover"><img src=')
    return html[:j]+tail

open('trang-chu.html','w',encoding='utf-8').write(ver(svg(resp(_h))))

def build(name,title,desc,nav_href,select=None,js='',cta=True,css=None):
    body=open(f'_src/{name}.body.html',encoding='utf-8').read()
    css=open(f'_src/{css or name}.css',encoding='utf-8').read()
    h=header.replace('<li class="on"><a href="trang-chu.html" aria-current="page">','<li><a href="trang-chu.html">')
    h=h.replace(f'<li><a href="{nav_href}">',f'<li class="on"><a href="{nav_href}"'+(' aria-current="page"' if nav_href==name+'.html' else '')+'>',1)
    c=CTA if cta else ''
    if not cta: h=h.replace('href="#dat-lich"','href="trang-chu.html#dat-lich"')
    if select: c=c.replace(f'<option>{select}</option>',f'<option selected>{select}</option>')
    out=f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="assets/img/favicon-192.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
<script>document.documentElement.classList.add('ga');setTimeout(function(){{document.documentElement.classList.remove('ga')}},2500)</script>
<style>
{css}</style>
</head>
{h}<main id="noi-dung" tabindex="-1">
{body}
{c}</main>

{footer if cta else footer.replace('href="#dat-lich"','href="trang-chu.html#dat-lich"')}<script src="assets/vendor/gsap.min.js"></script><script src="assets/vendor/ScrollTrigger.min.js"></script><script src="assets/vendor/SplitText.min.js"></script><script src="assets/site.js"></script>{js}
</body>
</html>
'''
    open(f'{name}.html','w',encoding='utf-8').write(ver(svg(resp(hero(lazy(out))))))
    print('built',name)

build('khu-mo','Khu mộ & vị trí an nghỉ – Hoa Viên Bình Dương',
      'Năm khu mộ tại Hoa Viên Bình Dương: Long Phụng Minh Đồ, Đại Lộ Vĩnh Hằng, Linh Hoa Tuệ Đàn, Song Thân và khu gia tộc Trúc Lâm Bích Thủy. Diện tích, vị trí và tư vấn chọn nơi an nghỉ.',
      'khu-mo.html','Tham quan, tìm hiểu khu mộ')

PLAYER='''
<script>
document.querySelector('#player button').addEventListener('click',function(){
  document.getElementById('player').innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/%s?autoplay=1&rel=0" title="%s" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
});
</script>'''
build('tang-le','Dịch vụ tang lễ – Hoa Viên Bình Dương',
      'Dịch vụ tang lễ trọn gói của Hoa Viên Bình Dương: khâm liệm, nhập quan, lễ viếng, di quan. Tổng đài tiếp nhận 24/7: 0818 555 444.',
      'khu-mo.html','Dịch vụ tang lễ',PLAYER%('msZmffahu1g','Video giới thiệu dịch vụ tang lễ'))
build('luu-tro-cot','Dịch vụ lưu tro cốt – Hoa Viên Bình Dương',
      'Lưu giữ tro cốt tại Chùa Thiên Phước trong khuôn viên Hoa Viên Bình Dương: hộc lưu cốt bằng gỗ tự nhiên, vị trí cố định, chăm sóc thường xuyên. Tổng đài 24/7: 0818 555 444.',
      'khu-mo.html','Dịch vụ lưu tro cốt')
build('dich-vu-khac','Dịch vụ khác – Hoa Viên Bình Dương',
      'Chăm sóc khu mộ, tư vấn thiết kế và xây dựng mộ, chuẩn bị sanh phần tại Hoa Viên Bình Dương. Tổng đài 24/7: 0818 555 444.',
      'khu-mo.html','Chăm sóc, xây dựng mộ')
build('khi-co-nguoi-than-qua-doi','Khi có người thân qua đời – Hoa Viên Bình Dương',
      'Những việc gia đình cần ưu tiên khi có người thân qua đời và các thủ tục cần lưu ý. Tổng đài Hoa Viên Bình Dương hỗ trợ 24/7: 0818 555 444.',
      'khi-co-nguoi-than-qua-doi.html',cta=False)
build('chuan-bi-tu-som','Chuẩn bị từ sớm – Hoa Viên Bình Dương',
      'Vì sao nên chủ động chuẩn bị từ sớm, lợi ích cho bản thân và gia đình, cẩm nang 6 bước. Hoa Viên Bình Dương tư vấn miễn phí, tổng đài 0818 555 444.',
      'khi-co-nguoi-than-qua-doi.html')
build('ve-chung-toi','Về chúng tôi – Hoa Viên Bình Dương',
      'Hoa Viên Bình Dương: công viên nghĩa trang 300 ha tại Chánh Phú Hòa, do Công ty CP Đầu tư Xây dựng Chánh Phú Hòa vận hành. Tầm nhìn, sứ mệnh, công trình và chi nhánh.',
      've-chung-toi.html')
MAP='''
<script>
document.querySelector('#mapbox button').addEventListener('click',function(){
  document.getElementById('mapbox').innerHTML='<iframe src="https://www.google.com/maps?q=Hoa+Vi%C3%AAn+Ngh%C4%A9a+Trang+B%C3%ACnh+D%C6%B0%C6%A1ng+Ch%C3%A1nh+Ph%C3%BA+H%C3%B2a&output=embed" title="Bản đồ Hoa Viên Bình Dương" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>';
});
</script>'''
build('lien-he','Liên hệ – Hoa Viên Bình Dương',
      'Liên hệ Hoa Viên Bình Dương: tổng đài 24/7 0818 555 444, văn phòng tại Chánh Phú Hòa, ba chi nhánh tại TP. HCM và biểu mẫu gửi yêu cầu tư vấn.',
      'lien-he.html',js=MAP,cta=False)
FAQ_JS='''
<script>
/* lọc câu hỏi theo từ khóa, bỏ dấu để gõ "thanh toan" vẫn ra */
(function(){
  var q=document.getElementById('faq-q'),empty=document.getElementById('faq-empty'),groups=[].slice.call(document.querySelectorAll('.fgroup'));
  function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/đ/g,'d').replace(/Đ/g,'D').toLowerCase()}
  groups.forEach(function(g){[].forEach.call(g.querySelectorAll('details'),function(d){d.dataset.t=norm(d.textContent)})});
  q.addEventListener('input',function(){
    var v=norm(q.value.trim()),any=false,total=0;
    groups.forEach(function(g){
      var n=0;[].forEach.call(g.querySelectorAll('details'),function(d){var hit=!v||d.dataset.t.indexOf(v)>-1;d.hidden=!hit;if(v)d.open=hit;else d.open=false;if(hit)n++});
      g.hidden=!n;if(n)any=true;total+=n;
    });
    empty.hidden=any;
    document.getElementById('faq-n').textContent=v?(total?'Tìm thấy '+total+' câu hỏi phù hợp.':'Không tìm thấy câu hỏi phù hợp.'):'';
  });
})();
</script>'''
build('hoi-dap','Hỏi & đáp – Hoa Viên Bình Dương',
      'Giải đáp thắc mắc thường gặp tại Hoa Viên Bình Dương: khu mộ và xây dựng, quyền an táng, hồ sơ, thanh toán, bảo mật thông tin. Tổng đài 24/7: 0818 555 444.',
      'hoi-dap.html',js=FAQ_JS,cta=False)
build('chi-nhanh','Hệ thống chi nhánh – Hoa Viên Bình Dương',
      'Địa chỉ Hoa Viên Bình Dương và ba chi nhánh tại TP. Hồ Chí Minh. Xem vị trí trên bản đồ và chọn địa điểm thuận tiện cho quý khách.',
      'chi-nhanh.html')
build('su-kien','Sự kiện – Hoa Viên Bình Dương',
      'Lịch lễ trong năm tại Hoa Viên Bình Dương: Lễ Cầu Siêu – Cầu An Tiết Thanh Minh, Giỗ Tổ Hùng Vương, Đại Lễ Vu Lan, Tảo mộ cuối năm.',
      'su-kien.html')
POSTS_JS='''
<script>
/* lọc bài theo chủ đề; khi lọc, bài đầu trở về thẻ thường */
(function(){
  var btns=[].slice.call(document.querySelectorAll('.cats button')),cards=[].slice.call(document.querySelectorAll('#posts .post-card')),lead=document.querySelector('.lead-post');
  btns.forEach(function(b){b.addEventListener('click',function(){
    var c=b.dataset.c;btns.forEach(function(x){x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b)});
    cards.forEach(function(k){k.hidden=!!c&&k.dataset.c!==c});
    lead.classList.toggle('lead-post',!c);
  })});
})();
</script>'''
build('bai-viet','Bài viết – Hoa Viên Bình Dương',
      'Bài viết từ Hoa Viên Bình Dương: hướng dẫn cho gia đình khi tổ chức tang lễ, chuẩn bị từ sớm, lưu giữ tro cốt, chăm sóc khu mộ và văn hóa tưởng niệm.',
      'bai-viet.html',js=POSTS_JS)

build('chinh-sach-quyen-rieng-tu','Chính sách quyền riêng tư – Hoa Viên Bình Dương',
      'Cách Hoa Viên Bình Dương thu thập, sử dụng, bảo mật và chia sẻ dữ liệu cá nhân của khách hàng, cùng quyền truy cập và chỉnh sửa dữ liệu của quý khách.',
      'chinh-sach-quyen-rieng-tu.html',cta=False)
TOUR_JS='<script src="assets/vendor/pannellum.js"></script><script>var TOUR='+open('_src/tour.json',encoding='utf-8').read()+'</script><script src="assets/tour.js"></script>'
build('tham-quan-360','Tham quan Hoa Viên 360° – Hoa Viên Bình Dương',
      'Khám phá Hoa Viên Bình Dương qua ảnh toàn cảnh 360° chụp bằng flycam: cổng hoa viên, Đại Lộ Vĩnh Hằng, Vĩnh Hằng Đài, Chùa Thiên Phước và các khu mộ.',
      'tham-quan-360.html','Tham quan, tìm hiểu khu mộ',TOUR_JS)

import json
for a in json.load(open('_src/articles.json',encoding='utf-8')):
    build('bai-viet-'+a['slug'],a['title']+' – Hoa Viên Bình Dương',a['excerpt'],'bai-viet.html',css='bai-viet-chi-tiet')
