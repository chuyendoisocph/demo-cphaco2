/* Công cụ rà soát (chỉ dùng khi phát triển): chạy trong trình duyệt, quét các trang trong iframe.
   window.runAudit(pages, width) → kết quả lưu ở window.__audit */
(function(){
  function lum(c){var m=c.match(/[\d.]+/g);if(!m)return null;var a=m.slice(0,3).map(function(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return{l:.2126*a[0]+.7152*a[1]+.0722*a[2],a:m[3]===undefined?1:+m[3]}}
  function ratio(a,b){var x=Math.max(a,b),y=Math.min(a,b);return(x+.05)/(y+.05)}
  function bgOf(w,el){
    for(var e=el;e&&e.nodeType===1;e=e.parentElement){
      var s=w.getComputedStyle(e);
      if(s.backgroundImage!=='none'&&!/gradient/.test(s.backgroundImage))return 'img';
      var c=lum(s.backgroundColor);if(c&&c.a>.5)return c.l;
      // chữ đè lên ảnh (phần tử anh em là img phủ kín)
      if(e.parentElement&&[].some.call(e.parentElement.children,function(k){return k!==e&&k.tagName==='IMG'&&w.getComputedStyle(k).position==='absolute'}))return 'img';
    }
    return 1;
  }
  function name(el){return(el.getAttribute('aria-label')||el.textContent||el.title||(el.querySelector('img[alt]')||{}).alt||'').trim()}
  function audit(w,d,file,width){
    var r={contrast:[],alt:[],head:[],noname:[],label:[],tap:[],ids:[],links:[]};
    d.querySelectorAll('img').forEach(function(i){if(!i.hasAttribute('alt'))r.alt.push(i.src.split('/').pop())});
    var hs=[].map.call(d.querySelectorAll('h1,h2,h3,h4,h5,h6'),function(h){return +h.tagName[1]});
    if(hs.filter(function(x){return x===1}).length!==1)r.head.push('h1 x'+hs.filter(function(x){return x===1}).length);
    for(var i=1;i<hs.length;i++)if(hs[i]>hs[i-1]+1)r.head.push('h'+hs[i-1]+'→h'+hs[i]+' '+d.querySelectorAll('h1,h2,h3,h4,h5,h6')[i].textContent.trim().slice(0,30));
    d.querySelectorAll('a,button').forEach(function(el){if(el.offsetParent&&!name(el))r.noname.push(el.outerHTML.slice(0,80))});
    d.querySelectorAll('input,select,textarea').forEach(function(el){if(el.type==='hidden')return;var ok=el.labels&&el.labels.length||el.getAttribute('aria-label')||el.getAttribute('aria-labelledby');if(!ok)r.label.push(el.outerHTML.slice(0,80))});
    var seen={};d.querySelectorAll('[id]').forEach(function(e){if(seen[e.id])r.ids.push(e.id);seen[e.id]=1});
    d.querySelectorAll('a[href^="#"]').forEach(function(a){var h=a.getAttribute('href');if(h.length>1&&!d.getElementById(h.slice(1)))r.links.push(h)});
    // tương phản chữ
    var tw=d.createTreeWalker(d.body,NodeFilter.SHOW_TEXT),n,done=new Set();
    while(n=tw.nextNode()){
      var el=n.parentElement;if(!n.textContent.trim()||done.has(el)||!el.offsetParent)continue;done.add(el);
      var s=w.getComputedStyle(el);if(s.visibility==='hidden'||+s.opacity<.5)continue;
      var fg=lum(s.color),bg=bgOf(w,el);if(!fg||bg==='img')continue;
      var cr=ratio(fg.l,bg),fs=parseFloat(s.fontSize),big=fs>=24||(fs>=18.6&&+s.fontWeight>=700);
      if(cr<(big?3:4.5))r.contrast.push(cr.toFixed(2)+' '+fs+'px '+s.color+' '+el.tagName+'.'+el.className+' "'+n.textContent.trim().slice(0,30)+'"');
    }
    // vùng chạm (khổ điện thoại)
    if(width<500)d.querySelectorAll('a,button,summary,input,select').forEach(function(el){
      if(!el.offsetParent)return;var b=el.getBoundingClientRect();if(!b.width)return;
      var inline=w.getComputedStyle(el).display==='inline'&&el.closest('p,li,td')&&!el.closest('nav,footer');
      if(!inline&&(b.height<24||b.width<24))r.tap.push(Math.round(b.width)+'x'+Math.round(b.height)+' '+el.tagName+'.'+el.className+' "'+name(el).slice(0,25)+'"');
    });
    // link tới file trong site
    var hrefs=new Set();d.querySelectorAll('a[href]').forEach(function(a){var h=a.getAttribute('href');if(/^(https?:|tel:|mailto:|#|zalo)/.test(h))return;hrefs.add(h.split('#')[0])});
    r._hrefs=[].slice.call(hrefs);
    r.overflow=d.documentElement.scrollWidth-w.innerWidth;
    return r;
  }
  window.runAudit=async function(pages,width){
    window.__audit={};window.__auditDone=false;
    for(var p of pages){
      var f=document.createElement('iframe');f.style.cssText='position:fixed;left:0;top:0;width:'+width+'px;height:800px;opacity:0;pointer-events:none';document.body.appendChild(f);
      await new Promise(function(res){f.onload=res;f.src=p});
      var w=f.contentWindow,dd=f.contentDocument;dd.documentElement.style.scrollBehavior='auto';
      for(var y=0;y<dd.body.scrollHeight;y+=600){w.scrollTo(0,y);await new Promise(function(res){setTimeout(res,60)})}
      await new Promise(function(res){setTimeout(res,2200)});
      try{window.__audit[p]=audit(w,dd,p,width)}catch(e){window.__audit[p]={err:String(e)}}
      f.remove();
    }
    var all=new Set();Object.values(window.__audit).forEach(function(r){(r._hrefs||[]).forEach(function(h){all.add(h)})});
    var bad=[];for(var h of all){try{var res=await fetch(h,{method:'HEAD'});if(!res.ok)bad.push(h+' '+res.status)}catch(e){bad.push(h+' err')}}
    window.__audit._broken=bad;window.__auditDone=true;
  };
})();
