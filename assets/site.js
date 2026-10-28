/* dùng chung: menu, thanh nav khi cuộn, form demo */
var nav=document.getElementById('nav');
addEventListener('scroll',function(){nav.classList.toggle('scrolled',scrollY>150)},{passive:true});
/* menu điện thoại: Esc hoặc chọn một mục thì đóng, trả con trỏ về nút */
var menuBtn=document.querySelector('.menu-btn');
function setMenu(o){nav.classList.toggle('open',o);menuBtn.setAttribute('aria-expanded',o)}
menuBtn.addEventListener('click',function(){setMenu(!nav.classList.contains('open'))});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){setMenu(false);menuBtn.focus()}});
nav.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false)});

/* form demo: kiểm tra từng ô, báo lỗi ngay dưới ô, rồi hiện lời cảm ơn */
document.querySelectorAll('form[data-demo]').forEach(function(f){
  f.noValidate=true;
  f.querySelectorAll('[required]').forEach(function(el){el.setAttribute('aria-required','true');var r=document.createElement('span');r.className='req';r.textContent='*';r.setAttribute('aria-hidden','true');el.parentNode.firstChild.after(r)});
  function check(el){
    var v=el.value.trim(),msg='';
    if(el.required&&!v)msg=el.type==='tel'?'Vui lòng nhập số điện thoại.':'Vui lòng nhập '+el.parentNode.firstChild.textContent.trim().toLowerCase()+'.';
    else if(v&&el.type==='tel'&&!/^(\+?84|0)\d{9,10}$/.test(v.replace(/[\s.\-()]/g,'')))msg='Số điện thoại chưa đúng, ví dụ 0818 555 444.';
    else if(v&&el.type==='email'&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v))msg='Email chưa đúng, ví dụ ten@gmail.com.';
    var id=(el.id||(el.id=(f.id||'dl')+'-'+el.name))+'-err',box=document.getElementById(id);
    if(msg){
      if(!box){box=document.createElement('span');box.className='err';box.id=id;el.after(box);el.setAttribute('aria-describedby',id)}
      box.textContent=msg;el.setAttribute('aria-invalid','true');
    }else{if(box)box.remove();el.removeAttribute('aria-invalid');el.removeAttribute('aria-describedby')}
    return !msg;
  }
  f.querySelectorAll('input,textarea').forEach(function(el){
    el.addEventListener('blur',function(){if(el.value.trim()||el.hasAttribute('aria-invalid'))check(el)});
    el.addEventListener('input',function(){if(el.hasAttribute('aria-invalid'))check(el)});
  });
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var bad=[].filter.call(f.querySelectorAll('input,textarea'),function(el){return !check(el)});
    if(bad.length){bad[0].focus();return}
    var b=f.querySelector('button[type=submit]'),label=b.firstChild.textContent;
    function note(msg){
      var n=f.querySelector('.note-send');
      if(!n){n=document.createElement('p');n.className='note-send';n.setAttribute('role','status');n.tabIndex=-1;f.appendChild(n)}
      n.textContent=msg;n.focus();
    }
    // chưa có địa chỉ nhận (data-endpoint) thì nói thật là chưa gửi, không báo thành công giả
    if(!f.dataset.endpoint){note('Biểu mẫu này chưa được kết nối nên thông tin chưa được gửi đi. Để đặt lịch hoặc cần hỗ trợ, vui lòng gọi 0818 555 444.');return}
    b.disabled=true;b.firstChild.textContent='Đang gửi… ';
    fetch(f.dataset.endpoint,{method:'POST',body:new FormData(f)}).then(function(r){
      if(!r.ok)throw r;
      f.innerHTML='<h3>Đã ghi nhận yêu cầu</h3><p class="ok" role="status" tabindex="-1">'+(f.dataset.ok||'Nhân viên sẽ gọi lại trong giờ làm việc để hẹn ngày và giờ xe đón. Cần hỗ trợ ngay, vui lòng gọi 0818 555 444.')+'</p>';
      f.querySelector('.ok').focus();
    }).catch(function(){
      b.disabled=false;b.firstChild.textContent=label;
      note('Chưa gửi được yêu cầu, vui lòng thử lại hoặc gọi 0818 555 444.');
    });
  });
});

/* video và bản đồ tải khi bấm: chuyển con trỏ vào khung vừa mở */
document.querySelectorAll('#player,#mapbox').forEach(function(box){
  new MutationObserver(function(){var i=box.querySelector('iframe');if(i)i.focus()}).observe(box,{childList:true});
});

/* ===== hiệu ứng (GSAP + ScrollTrigger + SplitText) =====
   Nhịp chậm, chạy một lần. Không có GSAP hoặc người dùng giảm chuyển động thì trang hiện bình thường. */
(function(){
  var root=document.documentElement;
  if(!window.gsap||!window.ScrollTrigger){root.classList.remove('ga');return}
  gsap.registerPlugin(ScrollTrigger);
  if(window.SplitText)gsap.registerPlugin(SplitText);
  var mm=gsap.matchMedia();
  mm.add('(prefers-reduced-motion: reduce)',function(){root.classList.remove('ga')});
  mm.add('(prefers-reduced-motion: no-preference)',function(){
    var EASE='expo.out',vh=innerHeight;
    gsap.defaults({ease:EASE});
    function below(el){return el.getBoundingClientRect().top>vh*0.92}
    // chữ trồi lên từng dòng; không có SplitText thì hiện dần cả khối
    function split(el,vars){
      if(!window.SplitText){gsap.from(el,{autoAlpha:0,y:24,duration:1.1,delay:vars.delay||0,scrollTrigger:vars.scrollTrigger});return}
      SplitText.create(el,{type:'lines',mask:'lines',autoSplit:true,onSplit:function(self){
        return gsap.from(self.lines,{yPercent:105,duration:1.15,stagger:.09,delay:vars.delay||0,scrollTrigger:vars.scrollTrigger});
      }});
    }

    /* đầu trang con: ảnh thu về khung, chữ trồi lên, ảnh nền trôi chậm khi cuộn */
    var ph=document.querySelector('.phero');
    if(ph){
      var pimg=ph.querySelector(':scope>img'),h1=ph.querySelector('h1');
      if(pimg){
        gsap.fromTo(pimg,{scale:1.1},{scale:1,duration:2.6});
        gsap.to(pimg,{yPercent:14,ease:'none',scrollTrigger:{trigger:ph,start:'top top',end:'bottom top',scrub:true}});
      }
      gsap.from(ph.querySelectorAll('.crumb'),{autoAlpha:0,y:14,duration:1,delay:.05});
      if(h1)split(h1,{delay:.12});
      gsap.from(ph.querySelectorAll('.wrap>p,.callnow'),{autoAlpha:0,y:18,duration:1.1,stagger:.1,delay:.4});
    }

    /* trang chủ: chữ trên ảnh trình chiếu, 4 lối tắt, ảnh trôi chậm khi cuộn */
    var copy=document.getElementById('slide-copy');
    if(copy){
      gsap.from(copy.children,{autoAlpha:0,y:22,duration:1.2,stagger:.1,delay:.15});
      gsap.from('.card .side',{autoAlpha:0,duration:1.2,delay:.6});
      gsap.from('.quick>a',{autoAlpha:0,y:30,duration:1.1,stagger:.08,delay:.35,clearProps:'transform'});
      gsap.to('#slides',{yPercent:12,ease:'none',scrollTrigger:{trigger:'.hero',start:'top top',end:'bottom top',scrub:true}});
    }
    root.classList.remove('ga');

    /* tiêu đề mục: từng dòng trồi lên khi cuộn tới */
    gsap.utils.toArray('.sec .title,.prose>h2').forEach(function(el){
      if(below(el))split(el,{scrollTrigger:{trigger:el,start:'top 88%',once:true}});
    });

    /* thẻ và khối nội dung: hiện dần, các thẻ cùng hàng hiện lần lượt */
    var GROUPS=['.facts>div','.mosaic figure','.prods>a','.benefits li','.guides a','.voices>*','.ev','.posts .post',
      '.stats>.wrap>div','.values article','.works figure','.zpics img','.specs>div','.steps li','.tl li','.gal figure',
      '.reads a','.paths a','.pair article','.groups article','.guide6 li','.gains li','.brs article','.branch-list article',
      '.ways .way','.consider details','.tiles a','.posts-grid .post-card','.inc li','.ffacts>div','.reasons li','.hl li',
      '.sec .lead','.sec-head .link','.prose>blockquote','.player','.map','.tbl','.cform','.side','.ask','.papers','.park',
      '.feat-box','.ev-row>div','.hall-txt','.build-txt','.org-main','.org-br','.pull','.year','.fbox','.cta form'];
    var seen=new Set(),cards=[];
    GROUPS.forEach(function(sel){gsap.utils.toArray(sel).forEach(function(el){
      if(seen.has(el)||el.closest('.phero,.hero')||!below(el))return;seen.add(el);cards.push(el);
    })});
    gsap.set(cards,{autoAlpha:0,y:34});
    ScrollTrigger.batch(cards,{start:'top 92%',once:true,onEnter:function(batch){
      // xong thì gỡ thuộc tính, để hiệu ứng rê chuột của thẻ hoạt động như cũ
      gsap.to(batch,{autoAlpha:1,y:0,duration:1.1,stagger:.09,overwrite:true,clearProps:'transform,opacity,visibility'});
    }});

    /* ảnh lớn: khung mở dần, ảnh bên trong thu về đúng cỡ */
    var FIGS=['.prose>figure','.ev-row figure','.cintro figure','.niche figure','.temple .tpics','.care-pics','.sp-pics',
      '.supply figure','.loved figure','.trust figure','.diff figure','.prep-side figure','.caring .img','.quote figure'];
    gsap.utils.toArray(FIGS.join(',')).forEach(function(el){
      if(seen.has(el)||!below(el))return;seen.add(el);
      var imgs=el.querySelectorAll('img');
      var tl=gsap.timeline({scrollTrigger:{trigger:el,start:'top 88%',once:true},
        onComplete:function(){gsap.set(el,{clearProps:'clipPath,opacity,visibility'});gsap.set(imgs,{clearProps:'transform'})}});
      tl.fromTo(el,{clipPath:'inset(10% 6% 10% 6%)',autoAlpha:0},{clipPath:'inset(0% 0% 0% 0%)',autoAlpha:1,duration:1.4,ease:'expo.inOut'});
      if(imgs.length)tl.fromTo(imgs,{scale:1.18},{scale:1,duration:1.8},0);
    });

    /* ảnh nền khung đặt lịch trôi chậm */
    gsap.utils.toArray('.cta>img').forEach(function(img){
      gsap.fromTo(img,{yPercent:-8,scale:1.18},{yPercent:8,ease:'none',scrollTrigger:{trigger:img.parentNode,start:'top bottom',end:'bottom top',scrub:true}});
    });

    /* số liệu chạy từ 0: chỉ số nguyên có đơn vị (300 ha), bỏ qua năm và giờ */
    gsap.utils.toArray('.facts b,.stats b').forEach(function(el){
      var m=el.textContent.match(/^(\d+)(\s*ha)$/);if(!m)return;
      var o={v:0};
      gsap.to(o,{v:+m[1],duration:1.8,ease:'power3.out',scrollTrigger:{trigger:el,start:'top 85%',once:true},
        onUpdate:function(){el.textContent=Math.round(o.v)+m[2]}});
    });

    /* thanh tiến độ đọc trên trang bài viết */
    var prose=document.querySelector('.prose');
    if(prose){
      var bar=document.createElement('div');bar.className='readbar';bar.setAttribute('aria-hidden','true');document.body.appendChild(bar);
      gsap.fromTo(bar,{scaleX:0},{scaleX:1,ease:'none',scrollTrigger:{trigger:prose,start:'top 20%',end:'bottom 80%',scrub:.3}});
      return function(){bar.remove()};
    }
  });
  // ảnh tải chậm làm đổi chiều cao trang: tính lại vị trí kích hoạt
  addEventListener('load',function(){ScrollTrigger.refresh()});
})();
