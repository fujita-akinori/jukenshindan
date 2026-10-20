/* ===========================================================
   ホームのヒーロー背景：ポンポン現れて消えていく四角形と、近くの四角形どうしを結ぶ線
   - 四角形は一定間隔で新しく現れ、ゆっくり回転・漂流しながら寿命が来ると消える
   - 近い四角形どうしは細い線で結ばれ、離れるほど線が薄くなる
   - マウス（タッチ）を近づけると四角形が少しよける
   - 「視差効果を減らす」設定の端末では、動かない静止画として描く
   =========================================================== */
(function(){
  var canvas = document.getElementById('bg-shapes');
  if(!canvas) return;
  var ctx = canvas.getContext('2d');
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var W = 0, H = 0, DPR = 1;
  var shapes = [];
  var lastSpawn = 0;

  // 見た目の調整値
  var LIFE = 11000;          // 1つの四角形が表示されている時間（ミリ秒）
  var POP_IN = 450;          // 現れるときのポンッという拡大にかける時間
  var FADE_OUT = 2600;       // 消えるときのフェードにかける時間
  var LINK_DIST = 190;       // この距離より近い四角形どうしを線で結ぶ
  var REPEL_DIST = 140;      // マウスがこの距離に入るとよける
  var SQUARE_ALPHA = 0.13;   // 四角形の最大の濃さ
  var LINE_ALPHA = 0.30;     // 線の最大の濃さ

  function resize(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = Math.round(W * DPR); canvas.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }

  // 画面の広さに応じて、同時に出ている数と大きさを決める
  function targetCount(){ return Math.max(10, Math.min(22, Math.round(W * H / 30000))); }
  function sizeRange(){ var s = Math.min(W, 900) / 900; return [24 + 20 * s, 60 + 50 * s]; }

  function spawn(now, age){
    var r = sizeRange();
    shapes.push({
      x: Math.random() * W,
      y: Math.random() * H,
      size: r[0] + Math.random() * (r[1] - r[0]),
      rot: Math.random() * Math.PI,
      vr: (Math.random() - 0.5) * 0.00035,      // 1ミリ秒あたりの回転
      vx: (Math.random() - 0.5) * 0.012,        // 1ミリ秒あたりの移動
      vy: (Math.random() - 0.5) * 0.012,
      tone: 185 + Math.floor(Math.random() * 40),
      born: now - (age || 0)
    });
  }

  // 現れる→保つ→消える の濃さ（0〜1）
  function lifeAlpha(s, now){
    var t = now - s.born;
    if(t < 0) return 0;
    if(t < POP_IN) return t / POP_IN;
    var left = LIFE - t;
    if(left < FADE_OUT) return Math.max(0, left / FADE_OUT);
    return 1;
  }
  // 現れるときだけ少し大きく弾む
  function popScale(s, now){
    var t = (now - s.born) / POP_IN;
    if(t >= 1) return 1;
    var e = 1 - Math.pow(1 - t, 3);
    return 0.4 + 0.75 * e - 0.15 * Math.sin(Math.PI * t);
  }

  var pointer = { x: -9999, y: -9999 };
  function setPointer(cx, cy){
    var rect = canvas.getBoundingClientRect();
    pointer.x = cx - rect.left; pointer.y = cy - rect.top;
  }
  var host = canvas.parentElement;
  host.addEventListener('mousemove', function(e){ setPointer(e.clientX, e.clientY); });
  host.addEventListener('mouseleave', function(){ pointer.x = pointer.y = -9999; });
  host.addEventListener('touchmove', function(e){ if(e.touches[0]) setPointer(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
  host.addEventListener('touchend', function(){ pointer.x = pointer.y = -9999; });

  function draw(now, dt){
    ctx.clearRect(0, 0, W, H);

    // 位置の更新
    for(var i = 0; i < shapes.length; i++){
      var s = shapes[i];
      s.x += s.vx * dt; s.y += s.vy * dt; s.rot += s.vr * dt;
      var dx = s.x - pointer.x, dy = s.y - pointer.y, d2 = dx * dx + dy * dy;
      if(d2 < REPEL_DIST * REPEL_DIST && d2 > 1){
        var d = Math.sqrt(d2), k = (1 - d / REPEL_DIST);
        s.x += dx / d * k * k * 2.2; s.y += dy / d * k * k * 2.2;
      }
    }

    // 線（四角形の下に描く）
    ctx.lineWidth = 1;
    for(var a = 0; a < shapes.length; a++){
      var A = shapes[a], la = lifeAlpha(A, now);
      if(la <= 0) continue;
      for(var b = a + 1; b < shapes.length; b++){
        var B = shapes[b], lb = lifeAlpha(B, now);
        if(lb <= 0) continue;
        var ex = A.x - B.x, ey = A.y - B.y, e2 = ex * ex + ey * ey;
        if(e2 > LINK_DIST * LINK_DIST) continue;
        var closeness = 1 - Math.sqrt(e2) / LINK_DIST;
        var alpha = LINE_ALPHA * closeness * Math.min(la, lb);
        ctx.strokeStyle = 'rgba(205,205,212,' + alpha.toFixed(3) + ')';
        ctx.beginPath(); ctx.moveTo(A.x, A.y); ctx.lineTo(B.x, B.y); ctx.stroke();
      }
    }

    // 四角形
    for(var j = 0; j < shapes.length; j++){
      var q = shapes[j], al = lifeAlpha(q, now);
      if(al <= 0) continue;
      var sz = q.size * popScale(q, now);
      ctx.save();
      ctx.translate(q.x, q.y); ctx.rotate(q.rot);
      ctx.fillStyle = 'rgba(' + q.tone + ',' + q.tone + ',' + (q.tone + 6) + ',' + (SQUARE_ALPHA * al).toFixed(3) + ')';
      ctx.fillRect(-sz / 2, -sz / 2, sz, sz);
      ctx.restore();
    }
  }

  function init(){
    resize();
    shapes = [];
    var now = performance.now(), n = targetCount();
    // 最初から画面がにぎやかになるよう、年齢をばらして並べておく
    for(var i = 0; i < n; i++) spawn(now, POP_IN + Math.random() * (LIFE - FADE_OUT - POP_IN));
    lastSpawn = now;
  }

  var prev = 0;
  function loop(now){
    var dt = prev ? Math.min(now - prev, 50) : 16; prev = now;
    // 寿命が尽きたものを消し、間隔をあけて新しいものを出す
    shapes = shapes.filter(function(s){ return now - s.born < LIFE; });
    var interval = LIFE / targetCount();
    if(now - lastSpawn > interval && shapes.length < targetCount() + 4){ spawn(now, 0); lastSpawn = now; }
    draw(now, dt);
    requestAnimationFrame(loop);
  }

  var resizeTimer = null;
  window.addEventListener('resize', function(){
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function(){ var oldW = W; resize(); if(Math.abs(W - oldW) > 80) init(); }, 150);
  });

  init();
  if(reduceMotion){ draw(performance.now(), 0); }
  else { requestAnimationFrame(loop); }
})();
