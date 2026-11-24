(function () {
  var root = document.getElementById("rg");
  if (!root) return;

  var $ = function (s) { return root.querySelector(s); };
  var steps = root.querySelectorAll("[data-step]");
  var dots = root.querySelectorAll(".rg-steps li");
  var state = { user: null, back: null, sig: null };

  function show(n) {
    steps.forEach(function (s) { s.hidden = s.dataset.step !== String(n); });
    dots.forEach(function (d, i) {
      d.classList.toggle("on", i + 1 === n);
      d.classList.toggle("done", i + 1 < n);
    });
    root.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function msg(el, text, bad) {
    el.textContent = text || "";
    el.classList.toggle("on", !!text);
    el.classList.toggle("bad", !!bad);
  }
  function loadImg(src) {
    return new Promise(function (ok, fail) {
      var i = new Image();
      i.onload = function () { ok(i); };
      i.onerror = function () { fail(new Error("img " + src)); };
      i.src = src;
    });
  }
  var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };

  /* ---------- 1. buscar nick ---------- */
  var formNick = $("#rg-nick-form"), nickMsg = $("#rg-nick-msg");
  formNick.addEventListener("submit", function (e) {
    e.preventDefault();
    var nick = $("#rg-nick").value.trim().replace(/^@/, "");
    if (!/^[A-Za-z0-9_]{3,20}$/.test(nick)) {
      return msg(nickMsg, "O nick do Roblox tem de 3 a 20 letras, números ou _ (sem espaços).", true);
    }
    var btn = formNick.querySelector("button");
    btn.disabled = true;
    msg(nickMsg, "Procurando " + nick + " no Roblox…");
    fetch("/api/roblox?action=user&name=" + encodeURIComponent(nick))
      .then(function (r) { return r.json().then(function (j) { return { s: r.status, j: j }; }); })
      .then(function (r) {
        if (r.s === 404) return msg(nickMsg, "Não encontrei nenhum jogador com o nick “" + nick + "”. Confira a escrita.", true);
        if (r.s !== 200) return msg(nickMsg, "O Roblox não respondeu agora. Tente de novo em alguns instantes.", true);
        state.user = r.j;
        $("#rg-conf-img").src = r.j.headshot || r.j.body || "";
        $("#rg-conf-display").textContent = r.j.displayName;
        $("#rg-conf-user").textContent = "@" + r.j.name + " · ID " + r.j.id;
        msg(nickMsg, "");
        show(2);
      })
      .catch(function () { msg(nickMsg, "Não consegui falar com o servidor. Tente novamente.", true); })
      .then(function () { btn.disabled = false; });
  });

  /* ---------- 2. confirmar ---------- */
  $("#rg-no").addEventListener("click", function () {
    state.user = null; state.back = null;
    show(1);
    $("#rg-nick").select();
  });
  $("#rg-yes").addEventListener("click", function () {
    // começa a montar as costas do personagem enquanto a pessoa assina
    state.back = renderBack(state.user);
    show(3);
  });

  /* ---------- 3. assinatura ---------- */
  var pad = $("#rg-pad"), pctx = pad.getContext("2d"), drawing = false, ink = false, last = null;
  pctx.lineCap = "round"; pctx.lineJoin = "round"; pctx.strokeStyle = "#111";
  function pos(e) {
    var r = pad.getBoundingClientRect();
    return { x: (e.clientX - r.left) * pad.width / r.width, y: (e.clientY - r.top) * pad.height / r.height };
  }
  pad.addEventListener("pointerdown", function (e) {
    drawing = true; ink = true; last = pos(e); pad.setPointerCapture(e.pointerId);
    pctx.lineWidth = 4; pctx.beginPath(); pctx.arc(last.x, last.y, 2, 0, 7); pctx.fillStyle = "#111"; pctx.fill();
    $("#rg-pad-hint").hidden = true;
    e.preventDefault();
  });
  pad.addEventListener("pointermove", function (e) {
    if (!drawing) return;
    var p = pos(e), w = e.pressure && e.pointerType === "pen" ? 2 + e.pressure * 4 : 4;
    pctx.lineWidth = w; pctx.beginPath(); pctx.moveTo(last.x, last.y); pctx.lineTo(p.x, p.y); pctx.stroke();
    last = p; e.preventDefault();
  });
  ["pointerup", "pointercancel", "pointerleave"].forEach(function (n) {
    pad.addEventListener(n, function () { drawing = false; });
  });
  function clearPad() {
    pctx.clearRect(0, 0, pad.width, pad.height); ink = false; $("#rg-pad-hint").hidden = false; msg($("#rg-sign-msg"), "");
  }
  $("#rg-clear").addEventListener("click", clearPad);
  $("#rg-back-1").addEventListener("click", function () { show(2); });

  $("#rg-gen").addEventListener("click", function () {
    var m = $("#rg-sign-msg");
    if (!ink) return msg(m, "Faça a sua assinatura no quadro acima antes de gerar.", true);
    var btn = this; btn.disabled = true;
    msg(m, "Gerando o seu RG-RP…");
    compose().then(function () { msg(m, ""); show(4); })
      .catch(function (err) { console.error(err); msg(m, "Algo deu errado ao montar o documento. Tente de novo.", true); })
      .then(function () { btn.disabled = false; });
  });

  /* ---------- costas do personagem (3D do Roblox) ---------- */
  function renderBack(u) {
    var timeout = new Promise(function (_, no) { setTimeout(function () { no(new Error("timeout 3D")); }, 25000); });
    return Promise.race([render3d(u.id), timeout]).catch(function (err) {
      console.warn("3D indisponível, usando a foto de frente:", err);
      return u.body ? loadImg(u.body).then(function (i) { i.fallback = true; return i; }) : null;
    });
  }

  function render3d(id) {
    var W = 428, H = 400, S = 2;
    return Promise.all([
      fetch("/api/roblox?action=model&id=" + id).then(function (r) { if (!r.ok) throw new Error("model " + r.status); return r.json(); }),
      import("three"),
      import("three/addons/loaders/OBJLoader.js"),
      import("three/addons/loaders/MTLLoader.js"),
    ]).then(function (all) {
      var meta = all[0], THREE = all[1], OBJLoader = all[2].OBJLoader, MTLLoader = all[3].MTLLoader;
      return Promise.all([fetch(meta.mtl).then(function (r) { return r.text(); }), fetch(meta.obj).then(function (r) { return r.text(); })])
        .then(function (txt) {
          var mtl = txt[0];
          Object.keys(meta.textures || {}).forEach(function (h) {
            mtl = mtl.split(h).join(location.origin + meta.textures[h]);
          });
          var started = 0, mgr = new THREE.LoadingManager();
          var loaded = new Promise(function (ok) { mgr.onLoad = ok; });
          mgr.onStart = function () { started++; };
          var mats = new MTLLoader(mgr).parse(mtl, "");
          mats.preload();
          var objLoader = new OBJLoader(); objLoader.setMaterials(mats);
          var obj = objLoader.parse(txt[1]);
          obj.traverse(function (o) { if (o.isMesh) [].concat(o.material).forEach(function (m) { m.side = THREE.DoubleSide; }); });
          return Promise.race([started ? loaded : Promise.resolve(), sleep(8000)]).then(function () {
            var a = meta.aabb, c = meta.camera;
            var min = a.min, max = a.max;
            var center = new THREE.Vector3((min.x + max.x) / 2, (min.y + max.y) / 2, (min.z + max.z) / 2);
            var height = max.y - min.y, width = Math.max(max.x - min.x, max.z - min.z);
            // direção da frente (câmera padrão do Roblox) -> invertida = costas
            var fx = c.position.x - center.x, fz = c.position.z - center.z, fl = Math.hypot(fx, fz) || 1;
            var bx = -fx / fl, bz = -fz / fl;
            var fov = 30, aspect = W / H;
            var dh = (height / 2) / Math.tan(THREE.MathUtils.degToRad(fov / 2));
            var dw = (width / 2) / (Math.tan(THREE.MathUtils.degToRad(fov / 2)) * aspect);
            var dist = Math.max(dh, dw) * 1.12 + width / 2;
            var cam = new THREE.PerspectiveCamera(fov, aspect, 0.1, dist * 10);
            cam.position.set(center.x + bx * dist, center.y, center.z + bz * dist);
            cam.lookAt(center);
            var scene = new THREE.Scene();
            scene.add(obj);
            scene.add(new THREE.AmbientLight(0xffffff, 2.2));
            var dl = new THREE.DirectionalLight(0xffffff, 1.2);
            dl.position.copy(cam.position); scene.add(dl);
            var rd = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
            rd.setPixelRatio(S); rd.setSize(W, H); rd.setClearColor(0xffffff, 0);
            rd.render(scene, cam);
            var out = document.createElement("canvas");
            out.width = W * S; out.height = H * S;
            out.getContext("2d").drawImage(rd.domElement, 0, 0, out.width, out.height);
            rd.dispose();
            return out;
          });
        });
    });
  }

  /* ---------- montar o documento ---------- */
  function rgNumber(id) {
    var n = (BigInt(id) * 2654435761n) % 10000000000n, s = n.toString().padStart(10, "0");
    return s.slice(0, 4) + "." + s.slice(4, 7) + "-" + s.slice(7);
  }
  // escreve texto girado (lê de baixo pra cima) cabendo em length x thickness
  function fitText(ctx, text, cx, cy, length, thick) {
    ctx.save();
    ctx.font = "700 100px 'Courier New', Courier, monospace";
    var m = ctx.measureText(text), h = m.actualBoundingBoxAscent + m.actualBoundingBoxDescent;
    ctx.translate(cx, cy); ctx.rotate(-Math.PI / 2);
    ctx.scale(length / m.width, thick / h);
    ctx.fillStyle = "#111"; ctx.textAlign = "center"; ctx.textBaseline = "alphabetic";
    ctx.fillText(text, 0, (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2);
    ctx.restore();
  }
  function rr(ctx, x, y, w, h, r) {
    ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }

  function compose() {
    var u = state.user, cv = $("#rg-out"), ctx = cv.getContext("2d");
    return Promise.all([loadImg("/assets/img/rg-template.png"), u.headshot ? loadImg(u.headshot) : null, state.back])
      .then(function (r) {
        var tpl = r[0], face = r[1], back = r[2];
        cv.width = tpl.width; cv.height = tpl.height;
        ctx.drawImage(tpl, 0, 0);

        // foto (retrato) — cobre o quadro, recortado com cantos redondos
        var px = 293, py = 134, pw = 428, ph = 622;
        ctx.save(); rr(ctx, px, py, pw, ph, 14); ctx.clip();
        var g = ctx.createLinearGradient(0, py, 0, py + ph); g.addColorStop(0, "#e4edf9"); g.addColorStop(1, "#c9d8ee");
        ctx.fillStyle = g; ctx.fillRect(px, py, pw, ph);
        if (face) {
          var s = Math.max(pw / face.width, ph / face.height), w = face.width * s, h = face.height * s;
          ctx.drawImage(face, px + (pw - w) / 2, py + (ph - h) / 2, w, h);
        }
        ctx.restore();

        // costas do personagem no lugar do dedo
        var bx = 293, by = 872, bw = 428, bh = 400;
        ctx.save(); rr(ctx, 293, 826, 428, 449, 14); ctx.clip();
        if (back) {
          var bwid = back.width, bhei = back.height, k = Math.min(bw / bwid, bh / bhei);
          ctx.drawImage(back, bx + (bw - bwid * k) / 2, by + (bh - bhei * k) / 2, bwid * k, bhei * k);
        }
        ctx.restore();
        state.fallback = !!(back && back.fallback);

        // assinatura: recorta o traço e gira para acompanhar a linha vertical
        var sg = cropInk(pad);
        if (sg) {
          var maxL = 740, maxT = 128, k2 = Math.min(maxL / sg.width, maxT / sg.height, 2.2);
          var L = sg.width * k2, T = sg.height * k2;
          ctx.save(); ctx.translate(892 - T / 2, 716); ctx.rotate(-Math.PI / 2);
          ctx.drawImage(sg, -L / 2, -T / 2, L, T); ctx.restore();
        }

        // número do RG-RP (mesmo jogador = mesmo número)
        var num = rgNumber(u.id);
        fitText(ctx, num, 111.5, 230, 258, 34);
        fitText(ctx, num, 931, 1380, 218, 27);
        $("#rg-num").textContent = num;
        $("#rg-fallback").hidden = !state.fallback; $("#rg-fallback").classList.add("on");
        $("#rg-name").textContent = u.displayName + " (@" + u.name + ")";
      });
  }

  function cropInk(c) {
    var d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data, x0 = c.width, y0 = c.height, x1 = 0, y1 = 0;
    for (var y = 0; y < c.height; y++) for (var x = 0; x < c.width; x++) {
      if (d[(y * c.width + x) * 4 + 3] > 20) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    }
    if (x1 < x0) return null;
    var pad2 = 6, o = document.createElement("canvas");
    o.width = x1 - x0 + 1 + pad2 * 2; o.height = y1 - y0 + 1 + pad2 * 2;
    o.getContext("2d").drawImage(c, x0, y0, x1 - x0 + 1, y1 - y0 + 1, pad2, pad2, x1 - x0 + 1, y1 - y0 + 1);
    return o;
  }

  /* ---------- 4. salvar ---------- */
  $("#rg-save").addEventListener("click", function () {
    $("#rg-out").toBlob(function (b) {
      var a = document.createElement("a");
      a.href = URL.createObjectURL(b);
      a.download = "RG-RP_" + state.user.name + ".png";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
    }, "image/png");
  });
  $("#rg-redo").addEventListener("click", function () {
    clearPad(); state.user = null; state.back = null; $("#rg-nick").value = ""; show(1);
  });
  $("#rg-edit-sign").addEventListener("click", function () { show(3); });
})();
