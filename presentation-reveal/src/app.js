/* Презентация «Император и старец»: reveal.js + GSAP + three.js.
   reveal.js  — слайды, клавиатура, пульт, свайпы, клавиша F.
   three.js   — объёмное яблоко с освещением.
   GSAP       — падение яблока, камера, вылет текста, листья.
   Manim      — анимированные схемы (заранее отрендерены в WebP). */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('js');

  var slidesEl = document.querySelector('.reveal .slides');
  var sections = Array.prototype.slice.call(slidesEl.children);
  var N = sections.length;
  var tree = document.getElementById('tree');
  var heroImg = document.getElementById('hero');
  var canvas = document.getElementById('apple3d');
  var fx = document.getElementById('fx');
  var bar = document.querySelector('.controls-bar');
  var prevBtn = document.getElementById('prev'), nextBtn = document.getElementById('next');
  var count = document.getElementById('count'), progress = document.getElementById('bar');
  var fsBtn = document.getElementById('fs');
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  /* ================= сцена: фото яблони ================= */
  // разметка в единицах кадра 750×1001 (фото 3840×5127, яблоня в Баркедале, CC0)
  var IMG_W = 750, IMG_H = 1001, PX = 715, P_TOP = 150, P_BOT = 540, P_GROUND = 905;
  var W = 0, H = 0, SH = 0, u2px = 1, offX = 0, XG = 0, R = 24, VS = 1;
  var perch = [], restTilt = [];
  var st = { x: 0, y: 0, tilt: 0, rx: 0, ry: 0, sx: 1, sy: 1, speed: 0 };   // состояние яблока
  var cam = 0, cur = 0, moveTl = null;

  function layoutSlides() {
    W = window.innerWidth; H = window.innerHeight;
    var ch = bar.offsetHeight + 24;
    var w = W > 700 ? W * 0.84 : W - 24;
    VS = Math.min(w / 1280, (H - ch - 20) / 720);
    var left = (W - 1280 * VS) / 2, top = Math.max(8, (H - ch - 720 * VS) / 2);
    slidesEl.style.transform = 'translate(' + left.toFixed(1) + 'px,' + top.toFixed(1) + 'px) scale(' + VS.toFixed(4) + ')';
  }

  function buildScene() {
    u2px = Math.max(W / IMG_W, H * 1.3 / IMG_H);
    SH = Math.round(IMG_H * u2px);
    var vr = slidesEl.getBoundingClientRect(), gut = W - vr.right;
    var gx = gut > 26 ? vr.right + gut / 2 : W - 22;
    offX = clamp(gx - PX * u2px, W - IMG_W * u2px, 0);
    XG = PX * u2px + offX;
    tree.style.width = Math.round(IMG_W * u2px) + 'px';
    tree.style.height = SH + 'px';
    R = clamp(W * 0.036, 42, 78) / 2;
    perch = []; restTilt = [];
    for (var i = 0; i < N - 1; i++) perch.push((P_TOP + (P_BOT - P_TOP) * i / (N - 2)) * u2px);
    perch.push(P_GROUND * u2px);
    var seed = 1864;
    for (i = 0; i < N; i++) { seed = (seed * 9301 + 49297) % 233280; restTilt.push(i ? (seed / 233280 - 0.5) * 0.6 : 0); }
  }
  function target() { return clamp(st.y - H * 0.5, 0, SH - H); }

  /* ================= three.js: объёмное яблоко ================= */
  var THREEok = false, renderer, scene3, camera3, squashG, tiltG, spinG, shadowM, ghosts = [];
  function appleTexture() {          // кожура с настоящего фото яблока (tools/apple_skin.py)
    var t = new THREE.Texture();
    var im = new Image();
    im.onload = function () { t.image = im; t.needsUpdate = true; };
    im.src = 'data:image/webp;base64,' + (window.__APPLE_SKIN || '');
    t.wrapS = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
    return t;
  }
  function appleGeometry() {
    var pts = [];
    for (var i = 0; i <= 64; i++) {
      var t = i / 64 * Math.PI;                              // 0 — низ, PI — верх
      var r = Math.sin(t) * (1 + 0.07 * -Math.cos(t)) * 0.97;   // чуть шире к плечикам
      var y = -Math.cos(t) * 1.0;
      y -= 0.30 * Math.exp(-Math.pow((Math.PI - t) / 0.42, 2));   // впадина у черенка
      y += 0.14 * Math.exp(-Math.pow(t / 0.38, 2));               // впадина снизу
      pts.push(new THREE.Vector2(Math.max(r, 0.0001), y));
    }
    var geo = new THREE.LatheGeometry(pts, 72);
    geo.computeVertexNormals();
    return geo;
  }
  function initThree() {
    if (!window.THREE) return false;
    try {                                  // сначала тихо проверяем, есть ли 3D-графика
      var probe = document.createElement('canvas');
      if (!(probe.getContext('webgl2') || probe.getContext('webgl'))) return false;
    } catch (e) { return false; }
    try {
      renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true, premultipliedAlpha: true });
    } catch (e) { return false; }
    if (!renderer.getContext()) return false;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
    scene3 = new THREE.Scene();
    camera3 = new THREE.OrthographicCamera(0, 1, 0, -1, -2000, 2000);
    scene3.add(new THREE.HemisphereLight(0xdfefff, 0x3c5a2a, 1.1));
    var sun = new THREE.DirectionalLight(0xfff1d6, 2.3); sun.position.set(0.8, 1.1, 1.2); scene3.add(sun);
    var rim = new THREE.DirectionalLight(0xbfe0ff, 0.9); rim.position.set(-1, 0.3, -0.6); scene3.add(rim);
    var fill = new THREE.DirectionalLight(0xffffff, 0.5); fill.position.set(-0.6, -0.4, 1); scene3.add(fill);

    var skin = new THREE.MeshPhysicalMaterial({ map: appleTexture(), roughness: 0.45, clearcoat: 0.55, clearcoatRoughness: 0.28 });
    var body = new THREE.Mesh(appleGeometry(), skin);
    var stemCurve = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0.6, 0), new THREE.Vector3(0.03, 0.9, 0), new THREE.Vector3(0.12, 1.18, 0.02)]);
    var stem = new THREE.Mesh(new THREE.TubeGeometry(stemCurve, 12, 0.045, 8, false), new THREE.MeshStandardMaterial({ color: 0x5a3b22, roughness: 0.9 }));
    var ls = new THREE.Shape();
    ls.moveTo(0, 0); ls.bezierCurveTo(0.18, 0.16, 0.5, 0.2, 0.78, 0); ls.bezierCurveTo(0.5, -0.2, 0.18, -0.16, 0, 0);
    var leafGeo = new THREE.ShapeGeometry(ls, 12);
    var leaf = new THREE.Mesh(leafGeo, new THREE.MeshStandardMaterial({ color: 0x4f9a3a, roughness: 0.6, side: THREE.DoubleSide }));
    leaf.position.set(0.1, 1.0, 0.02); leaf.rotation.set(-0.5, 0.3, 0.45); leaf.scale.setScalar(1.5);
    spinG = new THREE.Group(); spinG.add(body, stem, leaf);
    tiltG = new THREE.Group(); tiltG.add(spinG);
    squashG = new THREE.Group(); squashG.add(tiltG);
    scene3.add(squashG);
    // мягкая тень под яблоком
    var sc = document.createElement('canvas'); sc.width = sc.height = 64;
    var sg = sc.getContext('2d'), rg = sg.createRadialGradient(32, 32, 0, 32, 32, 32);
    rg.addColorStop(0, 'rgba(0,0,0,.5)'); rg.addColorStop(1, 'rgba(0,0,0,0)'); sg.fillStyle = rg; sg.fillRect(0, 0, 64, 64);
    shadowM = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false }));
    shadowM.position.z = -500; scene3.add(shadowM);
    // шлейф за быстро летящим яблоком
    for (var k = 0; k < 3; k++) {
      var gm = new THREE.Mesh(body.geometry, new THREE.MeshBasicMaterial({ color: 0xd23a2a, transparent: true, opacity: 0, depthWrite: false }));
      gm.position.z = -300 - k; scene3.add(gm); ghosts.push(gm);
    }
    canvas.hidden = false; heroImg.hidden = true;
    return true;
  }
  function sizeThree() {
    if (!THREEok) return;
    renderer.setSize(W, H, false);
    camera3.left = 0; camera3.right = W; camera3.top = 0; camera3.bottom = -H; camera3.updateProjectionMatrix();
  }

  /* ================= кадр ================= */
  var hist = [];
  function draw() {
    var ty = -Math.round(cam);
    tree.style.transform = 'translate3d(' + offX.toFixed(1) + 'px,' + ty + 'px,0)';
    var sy = st.y - cam;
    if (THREEok) {
      squashG.position.set(st.x, -sy, 0);
      squashG.scale.set(R * st.sx, R * st.sy, R * st.sx);
      tiltG.rotation.set(st.rx, 0, -st.tilt);
      spinG.rotation.y = st.ry;
      shadowM.position.set(st.x + R * 0.25, -(sy + R * 0.55), -500);
      shadowM.scale.set(R * 2.3, R * 1.0, 1);
      shadowM.material.opacity = st.speed > 0 ? 0.25 : 0.7;
      hist.unshift([st.x, sy]); if (hist.length > 10) hist.pop();
      var trail = Math.min(1, st.speed / (H * 1.2));
      ghosts.forEach(function (g, k) {
        var h = hist[Math.min(hist.length - 1, (k + 1) * 3)];
        g.position.set(h[0], -h[1], g.position.z); g.scale.set(R * st.sx * .96, R * st.sy * 1.04, R);
        g.material.opacity = trail * [0.22, 0.12, 0.06][k];
      });
      renderer.render(scene3, camera3);
    } else {
      var HS = R * 2.06;
      heroImg.style.width = heroImg.style.height = HS + 'px';
      heroImg.style.transform = 'translate3d(' + (st.x - HS / 2).toFixed(1) + 'px,' + (sy - HS / 2).toFixed(1) + 'px,0) scale(' +
        st.sx.toFixed(3) + ',' + st.sy.toFixed(3) + ') rotate(' + (st.tilt + st.rx).toFixed(3) + 'rad)';
    }
    parts.forEach(function (q) {
      q.el.style.opacity = clamp(q.life * 1.6, 0, 1).toFixed(3);
      q.el.style.transform = 'translate3d(' + (q.x - q.w / 2).toFixed(1) + 'px,' + (q.y - cam - q.h / 2).toFixed(1) + 'px,0) rotate(' + q.r.toFixed(3) + 'rad) scale(' + q.s.toFixed(3) + ')';
    });
  }

  // камера догоняет яблоко; лёгкое вращение яблока в покое показывает объём
  // общая скорость анимаций (задаётся в build.py): GSAP, камера и листья ускоряются одинаково
  var SPEED = window.__SPEED || 1;
  gsap.globalTimeline.timeScale(SPEED);
  gsap.ticker.add(function (time, dtMs) {
    var dt = Math.min(0.05, dtMs / 1000);
    stepParts(dt * SPEED);
    cam += (target() - cam) * (1 - Math.exp(-dt * 6.5 * SPEED));
    if (!moveTl && !reduce) st.ry += dt * 0.35;
    draw();
  });

  /* ================= листья и пыль ================= */
  var parts = [];
  var LEAF_COLS = [['#6fbf4a', '#3d7f26'], ['#8ccf55', '#4d8f2c'], ['#5aa83f', '#2f6b20'], ['#a7c94a', '#6b8a22']];
  function spawnLeaf(x, y, kick) {
    var c = LEAF_COLS[(Math.random() * LEAF_COLS.length) | 0], w = R * (1.3 + Math.random() * 0.6), h = w * 0.5;
    var el = document.createElement('div');
    el.innerHTML = '<svg viewBox="-20 -10 40 20" width="' + w.toFixed(0) + '" height="' + h.toFixed(0) + '"><path d="M-19 0 C -9 -11, 9 -10, 19 0 C 9 10, -9 11, -19 0 Z" fill="' + c[0] + '" stroke="' + c[1] + '" stroke-width="1.2"/><path d="M-19 0 L 17 0" stroke="' + c[1] + '" stroke-width="1"/></svg>';
    fx.appendChild(el);
    parts.push({ el: el, kind: 'leaf', x: x, y: y, w: w, h: h, vx: (Math.random() - 0.5) * R * 6 * kick, vy: -R * (1 + Math.random() * 2) * kick,
      r: Math.random() * 6.28, vr: (Math.random() - 0.5) * 6, ph: Math.random() * 6.28, s: 1, life: 2.4 + Math.random() * 0.8 });
  }
  function spawnDust(x, y) {
    for (var k = 0; k < 7; k++) {
      var w = R * (1.4 + Math.random() * 1.4), el = document.createElement('div');
      el.style.width = w + 'px'; el.style.height = (w * 0.55) + 'px'; el.style.borderRadius = '50%';
      el.style.background = 'radial-gradient(closest-side, rgba(214,196,150,.55), rgba(214,196,150,0))';
      fx.appendChild(el);
      parts.push({ el: el, kind: 'dust', x: x, y: y + R * 0.7, w: w, h: w * 0.55, vx: (k / 6 - 0.5) * 2 * R * 5, vy: -R * (0.6 + Math.random()), r: 0, vr: 0, ph: 0, s: 0.4, life: 0.9 + Math.random() * 0.4 });
    }
  }
  function stepParts(dt) {
    for (var k = parts.length - 1; k >= 0; k--) {
      var q = parts[k];
      q.life -= dt;
      if (q.kind === 'leaf') {
        q.ph += dt * 3.2;
        q.vy += (H * 0.09 - q.vy) * Math.min(1, dt * 2.2);
        q.vx *= 1 - Math.min(1, dt * 1.5);
        q.x += (q.vx + Math.sin(q.ph) * R * 3) * dt; q.y += q.vy * dt;
        q.r += (q.vr + Math.cos(q.ph) * 1.5) * dt;
      } else {
        q.x += q.vx * dt; q.y += q.vy * dt; q.vx *= 1 - Math.min(1, dt * 3); q.vy *= 1 - Math.min(1, dt * 3);
        q.s += dt * 1.6;
      }
      if (q.life <= 0) { q.el.parentNode && q.el.parentNode.removeChild(q.el); parts.splice(k, 1); }
    }
  }

  /* ================= движение яблока (GSAP) ================= */
  var TWO_PI = Math.PI * 2;
  function fallTo(b, resting, fromFirst) {
    var y0 = st.y, y1 = perch[b], g = H * 2.6;
    var T = Math.sqrt(2 * Math.max(1, y1 - y0) / g);
    var b1 = R * 1.1, t1 = Math.sqrt(2 * b1 / g), b2 = R * 0.35, t2 = Math.sqrt(2 * b2 / g);
    var drift = R * (Math.random() * 0.8 - 0.4);
    var tl = gsap.timeline();
    if (resting) {                                           // раскачивается всё сильнее и срывается
      var amp = fromFirst ? [0.05, -0.09, 0.13, -0.17, 0.08] : [0.06, -0.1, 0.07];
      var base = st.tilt;
      amp.forEach(function (a) { tl.to(st, { tilt: base + a, duration: 0.1, ease: 'sine.inOut' }); });
      tl.to(st, { y: y0 - R * 0.25, sx: 1.06, sy: 0.94, duration: 0.09, ease: 'power1.out' });
      tl.call(function () { for (var n = 0; n < (fromFirst ? 3 : 2); n++) spawnLeaf(st.x, y0 - R * 0.6, 1); });
      T = Math.sqrt(2 * Math.max(1, y1 - (y0 - R * 0.25)) / g);
    }
    // свободное падение: power2.in — это и есть y = g·t²/2
    tl.add('fall');
    tl.to(st, { y: y1, duration: T, ease: 'power2.in' }, 'fall');
    tl.to(st, { x: XG + drift, duration: T, ease: 'none' }, 'fall');
    tl.to(st, { rx: Math.round(st.rx / TWO_PI) * TWO_PI + TWO_PI, ry: st.ry + Math.PI * 1.5, tilt: restTilt[b], duration: T, ease: 'none' }, 'fall');
    tl.to(st, { sx: 0.91, sy: 1.15, duration: T * 0.7, ease: 'power1.in' }, 'fall');
    tl.to(st, { speed: g * T, duration: T, ease: 'none' }, 'fall');
    // удар: сплющивание, пыль или лист, два отскока
    tl.call(function () { st.speed = 0; if (b === N - 1) spawnDust(st.x, y1); else spawnLeaf(st.x, y1 - R * 0.4, 0.6); });
    tl.to(st, { sx: 1.22, sy: 0.74, duration: 0.06, ease: 'power2.out' });
    tl.to(st, { y: y1 - b1, sx: 0.96, sy: 1.06, duration: t1, ease: 'power2.out' });
    tl.to(st, { y: y1, duration: t1, ease: 'power2.in' });
    tl.to(st, { sx: 1.1, sy: 0.88, duration: 0.05, ease: 'power2.out' });
    tl.to(st, { y: y1 - b2, sx: 1, sy: 1, duration: t2, ease: 'power2.out' });
    tl.to(st, { y: y1, duration: t2, ease: 'power2.in' });
    return tl;
  }
  function riseTo(b) {
    return gsap.timeline().to(st, { y: perch[b], x: XG, rx: Math.round(st.rx / TWO_PI) * TWO_PI, tilt: restTilt[b], sx: 1, sy: 1, speed: 0, duration: 1, ease: 'power2.inOut' });
  }

  /* ================= текст вылетает из яблока ================= */
  var DIAG = window.__DIAGRAMS || {}, blobUrls = {};
  function diagramUrl(n) {           // новый адрес каждый раз — анимация WebP начинается сначала
    if (!DIAG[n]) return null;
    try {
      if (!blobUrls[n]) {
        var bin = atob(DIAG[n]), arr = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
        blobUrls[n] = new Blob([arr], { type: 'image/webp' });
      }
      return URL.createObjectURL(blobUrls[n]);
    } catch (e) { return null; }
  }
  function playDiagram(img) {
    if (reduce || !img) return;
    var u = diagramUrl(img.getAttribute('data-n'));
    if (!u) return;
    var old = img.getAttribute('data-blob');
    img.src = u; img.setAttribute('data-blob', u);
    if (old) setTimeout(function () { URL.revokeObjectURL(old); }, 4000);
  }
  function items(i) { return Array.prototype.slice.call(sections[i].querySelectorAll('.a, .footer')); }
  function hideContent(i) { var l = items(i); gsap.killTweensOf(l); gsap.set(l, { opacity: 0, x: 0, y: 0, scale: 1 }); }
  function showNow(i) { var l = items(i); gsap.killTweensOf(l); gsap.set(l, { opacity: 1, x: 0, y: 0, scale: 1 }); }
  function emerge(i) {
    var list = items(i);
    gsap.killTweensOf(list);
    if (reduce) { showNow(i); return; }
    gsap.set(list, { opacity: 0, x: 0, y: 0, scale: 1 });
    var ax = st.x, ay = st.y - target();
    list.forEach(function (e, k) {
      var r = e.getBoundingClientRect();
      var dx = (ax - (r.left + r.right) / 2) / VS, dy = (ay - (r.top + r.bottom) / 2) / VS;
      var img = e.querySelector('img.diagram');
      gsap.fromTo(e, { x: dx, y: dy, scale: 0.04, opacity: 0 },
        { x: 0, y: 0, scale: 1, opacity: 1, duration: 0.85, delay: k * 0.075, ease: 'power3.out',
          onStart: img ? function () { playDiagram(img); } : null });
    });
  }

  /* ================= смена слайда ================= */
  function go(b) {
    if (b === cur && !moveTl) return;
    var from = cur; cur = b; ui();
    hideContent(b);
    if (moveTl) { moveTl.kill(); moveTl = null; }
    if (reduce) { st.y = perch[b]; st.x = XG; st.tilt = restTilt[b]; cam = target(); showNow(b); return; }
    var resting = Math.abs(st.y - perch[from]) < 1 && st.speed === 0;
    moveTl = perch[b] > st.y + 1 ? fallTo(b, resting, from === 0 && resting) : riseTo(b);
    moveTl.eventCallback('onComplete', function () { moveTl = null; st.speed = 0; if (cur === b) emerge(b); });
  }
  function ui() {
    prevBtn.disabled = cur === 0;
    nextBtn.disabled = cur === N - 1;
    count.textContent = (cur + 1) + ' / ' + N;
    progress.style.width = ((cur + 1) / N * 100) + '%';
  }

  /* ================= полноэкранный режим ================= */
  var canFs = !!(root.requestFullscreen || root.webkitRequestFullscreen);
  function isFs() { return !!(document.fullscreenElement || document.webkitFullscreenElement); }
  function toggleFs() {
    try {
      if (isFs()) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      else { var p = (root.requestFullscreen || root.webkitRequestFullscreen).call(root); if (p && p.catch) p.catch(function () {}); }
    } catch (e) {}
  }
  if (!canFs) fsBtn.hidden = true;
  fsBtn.addEventListener('click', toggleFs);
  function fsLabel() { fsBtn.textContent = isFs() ? 'Обычный режим' : 'Во весь экран'; }
  document.addEventListener('fullscreenchange', fsLabel);
  document.addEventListener('webkitfullscreenchange', fsLabel);

  /* ================= запуск ================= */
  function relayout() {
    layoutSlides(); buildScene(); sizeThree();
    if (moveTl) { moveTl.kill(); moveTl = null; showNow(cur); }
    st.x = XG; st.y = perch[cur]; st.tilt = restTilt[cur]; st.sx = st.sy = 1; st.speed = 0; cam = target();
    draw();
  }
  var rt = null, lastW = 0, lastH = 0;
  window.addEventListener('resize', function () {
    clearTimeout(rt);
    rt = setTimeout(function () {
      if (window.innerWidth === lastW && window.innerHeight === lastH) return;
      lastW = window.innerWidth; lastH = window.innerHeight; relayout();
    }, 250);
  });

  THREEok = initThree();
  sections.forEach(function (s, i) { hideContent(i); });

  Reveal.initialize({
    width: 1280, height: 720, disableLayout: true,
    hash: false, history: false, respondToHashChanges: false, fragmentInURL: false,
    controls: false, progress: false, slideNumber: false, overview: false, help: false,
    center: false, transition: 'fade', transitionSpeed: 'fast', backgroundTransition: 'none',
    touch: true, loop: false, keyboard: { 13: 'next' }, postMessage: false, postMessageEvents: false,
    previewLinks: false, autoPlayMedia: false, preloadIframes: false, pdfMaxPagesPerSlide: 1
  }).then(function () {
    lastW = window.innerWidth; lastH = window.innerHeight;
    relayout(); ui();
    setTimeout(function () { emerge(0); }, 400);
  });
  Reveal.on('slidechanged', function (e) { go(e.indexh); });
  prevBtn.addEventListener('click', function () { Reveal.prev(); });
  nextBtn.addEventListener('click', function () { Reveal.next(); });

  window.__deck = {
    get cur() { return cur; }, get busy() { return !!moveTl; }, get webgl() { return THREEok; },
    get apple() { return { x: st.x, y: st.y - cam, cam: cam, perch: perch, R: R }; }
  };
})();
