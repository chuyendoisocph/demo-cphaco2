/* trang Tham quan 360°: Pannellum + mũi tên nối các điểm theo vị trí GPS lúc chụp (dữ liệu TOUR từ bản clone) */
(function(){
  if(!window.pannellum||!window.TOUR)return;
  var DEG=Math.PI/180,R=6371000,HFOV=100,MARGIN=6;
  // tự xoay chậm từ trái sang phải khi người xem không thao tác (trừ ảnh ngoài cổng, và khi máy bật giảm chuyển động)
  var ROT=matchMedia('(prefers-reduced-motion: reduce)').matches?false:-3,NO_ROT={'cong-1':1};
  var byId={};TOUR.forEach(function(s,i){s.no=i;byId[s.id]=s});
  function norm(d){return((d+180)%360+360)%360-180}
  function bearing(a,b){var dl=(b.lon-a.lon)*DEG,y=Math.sin(dl)*Math.cos(b.lat*DEG),x=Math.cos(a.lat*DEG)*Math.sin(b.lat*DEG)-Math.sin(a.lat*DEG)*Math.cos(b.lat*DEG)*Math.cos(dl);return Math.atan2(y,x)/DEG}
  function dist(a,b){var dy=(b.lat-a.lat)*DEG*R,dx=(b.lon-a.lon)*DEG*R*Math.cos(a.lat*DEG);return Math.hypot(dx,dy)}
  function gap(a,b){return Math.abs(norm(a-b))}
  // hướng nhìn gần nhất không chạm vùng ảnh bị làm mờ (công trình ngoài hoa viên)
  function clearYaw(s,yaw){
    var half=HFOV/2+MARGIN,rs=s.blurredYaws;
    function hit(c){return rs.some(function(r){return gap(c,(r[0]+r[1])/2)<half+(r[1]-r[0])/2})}
    if(!hit(yaw))return yaw;
    var c=[];rs.forEach(function(r){c.push(norm(r[0]-half-1),norm(r[1]+half+1))});
    c=c.filter(function(x){return !hit(x)});
    return c.length?c.reduce(function(b,x){return gap(x,yaw)<gap(b,yaw)?x:b}):yaw;
  }
  function label(div,t){div.setAttribute('title','Đi tới '+t);var s=document.createElement('span');s.textContent=t;div.appendChild(s)}

  var scenes={};
  TOUR.forEach(function(s){
    scenes[s.id]={title:s.title,panorama:s.pano,pitch:s.pitch,yaw:clearYaw(s,s.yaw),hfov:HFOV,
      hotSpots:s.links.filter(function(id){return byId[id]}).map(function(id){
        var t=byId[id],dir=bearing(s.camera,t.camera);
        return{type:'scene',sceneId:id,yaw:norm(dir-s.camera.heading),
          pitch:Math.min(-4,Math.max(-45,-Math.atan2(s.camera.altitude,dist(s.camera,t.camera))/DEG)),
          targetYaw:clearYaw(t,norm(dir-t.camera.heading)),targetPitch:t.pitch,
          cssClass:'hs-go',createTooltipFunc:label,createTooltipArgs:t.title};
      })};
  });

  var start=byId[location.hash.slice(1)]?location.hash.slice(1):TOUR[0].id;
  var viewer=pannellum.viewer('pano',{default:{firstScene:start,sceneFadeDuration:800,autoLoad:true,compass:false,
    mouseZoom:'fullscreenonly',minHfov:50,maxHfov:120,strings:{loadingLabel:'Đang tải ảnh…',loadButtonLabel:'Bấm để tải ảnh 360°'}},scenes:scenes});

  var $=function(id){return document.getElementById(id)},GRP={'cong-trinh':'Công trình','khu-mo':'Khu mộ'};
  var btns=[].slice.call(document.querySelectorAll('.tlist button'));
  function show(id){
    var s=byId[id],nx=TOUR[(s.no+1)%TOUR.length];
    $('t-no').textContent=(s.no<9?'0':'')+(s.no+1);$('t-grp').textContent=GRP[s.group];
    $('t-title').textContent=s.title;$('t-desc').textContent=s.description;$('t-next-name').textContent=nx.title;
    btns.forEach(function(b){if(b.dataset.scene===id)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current')});
    history.replaceState(null,'','#'+id);
  }
  function go(id){if(id!==viewer.getScene())viewer.loadScene(id)}
  viewer.on('scenechange',show);show(start);
  // chỉ bắt đầu xoay sau IDLE ms không thao tác (kể cả ngay sau khi mở ảnh); mọi lần chạm, kéo, cuộn, gõ phím đều đếm lại
  var IDLE=4000,idle;
  function wait(){
    clearTimeout(idle);viewer.stopAutoRotate();
    if(ROT&&!NO_ROT[viewer.getScene()])idle=setTimeout(function(){viewer.startAutoRotate(ROT,viewer.getPitch())},IDLE);
  }
  ['pointerdown','pointerup','wheel','keydown','touchstart','touchend'].forEach(function(e){$('pano').addEventListener(e,wait,{passive:true})});
  viewer.on('load',wait);
  $('t-next').onclick=function(){go(TOUR[(byId[viewer.getScene()].no+1)%TOUR.length].id)};
  $('t-prev').onclick=function(){go(TOUR[(byId[viewer.getScene()].no+TOUR.length-1)%TOUR.length].id)};
  // chọn điểm trong danh sách: cuộn lên khung ảnh rồi mở
  btns.forEach(function(b){b.onclick=function(){go(b.dataset.scene);document.querySelector('.tour').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});$('pano').focus({preventScroll:true})}});
})();
