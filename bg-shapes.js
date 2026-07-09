(function(){
  const canvas = document.getElementById('bg-shapes');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let W, H, DPR;
  function resize(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  window.addEventListener('resize', resize);

  const COLORS = ['rgba(160,160,168,0.16)', 'rgba(160,160,168,0.10)', 'rgba(200,200,206,0.07)', 'rgba(200,200,206,0.045)'];
  const COUNT = 16;
  let shapes = [];

  function makeShape(){
    const w = 16 + Math.random() * 26;
    const h = w; // 正方形
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      w: w,
      h: h,
      rot: Math.random() * Math.PI,
      vx: (Math.random() - 0.5) * 0.12,
      vy: (Math.random() - 0.5) * 0.12,
      vr: (Math.random() - 0.5) * 0.0025,
      color: COLORS[Math.floor(Math.random() * COLORS.length)]
    };
  }

  function init(){
    resize();
    shapes = [];
    for(let i = 0; i < COUNT; i++) shapes.push(makeShape());
  }

  const mouse = { x: -9999, y: -9999, active: false };
  canvas.parentElement.addEventListener('mousemove', (e)=>{
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
    mouse.active = true;
  });
  canvas.parentElement.addEventListener('mouseleave', ()=>{ mouse.active = false; });

  const AVOID_RADIUS = 130;
  const AVOID_FORCE = 0.9;

  function step(){
    ctx.clearRect(0, 0, W, H);

    shapes.forEach(s => {
      if(mouse.active){
        const dx = s.x - mouse.x;
        const dy = s.y - mouse.y;
        const dist = Math.sqrt(dx*dx + dy*dy) || 1;
        if(dist < AVOID_RADIUS){
          const force = (1 - dist / AVOID_RADIUS) * AVOID_FORCE;
          s.vx += (dx / dist) * force * 0.6;
          s.vy += (dy / dist) * force * 0.6;
        }
      }

      s.vx *= 0.96;
      s.vy *= 0.96;
      s.vx = Math.max(-2.2, Math.min(2.2, s.vx));
      s.vy = Math.max(-2.2, Math.min(2.2, s.vy));

      s.x += s.vx;
      s.y += s.vy;
      s.rot += s.vr;

      const pad = s.h;
      if(s.x < -pad) s.x = W + pad;
      if(s.x > W + pad) s.x = -pad;
      if(s.y < -pad) s.y = H + pad;
      if(s.y > H + pad) s.y = -pad;

      ctx.save();
      ctx.translate(s.x, s.y);
      ctx.rotate(s.rot);
      ctx.fillStyle = s.color;
      ctx.fillRect(-s.w/2, -s.h/2, s.w, s.h);
      ctx.restore();
    });

    if(!prefersReducedMotion) requestAnimationFrame(step);
  }

  init();
  if(prefersReducedMotion){
    step();
  } else {
    step();
  }
})();
