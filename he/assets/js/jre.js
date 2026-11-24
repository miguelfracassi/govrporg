(function () {
  var $ = function (id) { return document.getElementById(id); };
  var CARGOS = {
    "DEPUTADO FEDERAL (ROBLOXIANO)": 4,
    "DEPUTADO ESTADUAL (ROBLOXIANO)": 5,
    "SENADOR (ROBLOXIANO)": 3,
    "GOVERNADOR (ROBLOXIANO)": 2,
    "PRESIDENTE (ROBLOXIANO)": 2
  };
  function msg(el, t, bad) { el.textContent = t || ""; el.classList.toggle("on", !!t); el.classList.toggle("bad", !!bad); }

  /* ================= inscrição (pública) ================= */
  var root = $("insc");
  if (root) {
    var steps = root.querySelectorAll("[data-step]"), dots = root.querySelectorAll(".rg-steps li");
    var st = { rg: null, cargo: null };
    var show = function (n) {
      steps.forEach(function (s) { s.hidden = s.dataset.step !== String(n); });
      dots.forEach(function (d, i) { d.classList.toggle("on", i + 1 === n); d.classList.toggle("done", i + 1 < n); });
      root.scrollIntoView({ behavior: "smooth", block: "start" });
    };

    // 1. anexo do RG (reduzido no navegador para caber no envio)
    var file = $("in-rg"), m1 = $("in-m1");
    file.addEventListener("change", function () {
      st.rg = null; $("in-prev").hidden = true; msg(m1, "");
      var f = file.files[0]; if (!f) return;
      if (!/^image\//.test(f.type)) return msg(m1, "Anexe uma imagem (PNG ou JPG) do seu RG-RP.", true);
      var url = URL.createObjectURL(f), img = new Image();
      img.onload = function () {
        var k = Math.min(1, 1100 / Math.max(img.width, img.height)), c = document.createElement("canvas");
        c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
        var x = c.getContext("2d"); x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height); x.drawImage(img, 0, 0, c.width, c.height);
        var q = 0.85, out = c.toDataURL("image/jpeg", q);
        while (out.length > 1200000 && q > 0.3) { q -= 0.1; out = c.toDataURL("image/jpeg", q); }
        st.rg = out; $("in-prev").src = out; $("in-prev").hidden = false; URL.revokeObjectURL(url);
      };
      img.onerror = function () { msg(m1, "Não consegui abrir essa imagem. Tente outra.", true); };
      img.src = url;
    });
    $("in-next1").addEventListener("click", function () {
      if (!st.rg) return msg(m1, "Anexe o seu RG-RP para continuar.", true);
      show(2);
    });

    // 2. cargo
    var m2 = $("in-m2");
    $("in-next2").addEventListener("click", function () {
      var r = root.querySelector('input[name="cargo"]:checked');
      if (!r) return msg(m2, "Escolha um cargo.", true);
      st.cargo = r.value; var n = CARGOS[st.cargo];
      $("in-num-label").textContent = "Número do candidato a " + st.cargo + " (" + n + " números)";
      var inp = $("in-num"); inp.value = ""; inp.maxLength = n; inp.placeholder = new Array(n + 1).join("0");
      $("in-agree-cargo").textContent = st.cargo; $("in-terms-cargo").textContent = st.cargo;
      msg(m2, ""); show(3); inp.focus();
    });
    $("in-back2").addEventListener("click", function () { show(1); });

    // 3. número
    var m3 = $("in-m3"), num = $("in-num");
    num.addEventListener("input", function () { num.value = num.value.replace(/\D/g, ""); });
    $("in-next3").addEventListener("click", function () {
      var n = CARGOS[st.cargo];
      if (num.value.length !== n) return msg(m3, st.cargo + " usa exatamente " + n + " números.", true);
      msg(m3, ""); show(4); setTimeout(function () { if (atEnd()) { ck.disabled = false; $("in-agree-wrap").classList.remove("lock"); } }, 50);
    });
    $("in-back3").addEventListener("click", function () { show(2); });

    // 4. termos: só libera o aceite depois de rolar até o fim
    var box = $("in-terms"), ck = $("in-agree"), m4 = $("in-m4");
    function atEnd() { return box.scrollTop + box.clientHeight >= box.scrollHeight - 6; }
    box.addEventListener("scroll", function () { if (atEnd()) { ck.disabled = false; $("in-agree-wrap").classList.remove("lock"); } });
    $("in-back4").addEventListener("click", function () { show(3); });
    $("in-send").addEventListener("click", function () {
      if (!ck.checked) return msg(m4, "Role os termos até o fim e marque a caixa para concordar.", true);
      var btn = this; btn.disabled = true; msg(m4, "Enviando…");
      fetch("/api/inscricoes", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cargo: st.cargo, numero: num.value, rg: st.rg, aceite: true })
      }).then(function (r) { return r.json().then(function (j) { return { s: r.status, j: j }; }); })
        .then(function (r) {
          if (r.s === 201) {
            $("in-ok-cargo").textContent = st.cargo; $("in-ok-num").textContent = num.value; $("in-ok-prot").textContent = r.j.protocolo;
            msg(m4, ""); show(5);
          } else if (r.s === 409) msg(m4, "Esse número já foi usado por outro candidato a " + st.cargo + ". Volte e escolha outro.", true);
          else msg(m4, "Não foi possível enviar agora (" + (r.j.error || r.s) + "). Tente novamente.", true);
        })
        .catch(function () { msg(m4, "Sem conexão com o servidor. Tente novamente.", true); })
        .then(function () { btn.disabled = false; });
    });
  }

  /* ================= painel admin ================= */
  var adm = $("adm");
  if (adm) {
    var pass = null, rows = [];
    try { pass = sessionStorage.getItem("jre_pw"); } catch (e) {}
    function api(path) { return fetch("/api/inscricoes" + (path || ""), { headers: { "x-admin-password": pass || "" } }); }
    function fmt(d) { return new Date(d).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" }); }
    function render() {
      var f = $("adm-filter").value, list = rows.filter(function (r) { return !f || r.cargo === f; });
      $("adm-count").textContent = list.length + " inscrição(ões)" + (f ? " em " + f : " no total");
      var tb = $("adm-body"); tb.innerHTML = "";
      list.forEach(function (r) {
        var tr = document.createElement("tr");
        [r.id, fmt(r.criado_em), r.cargo, r.numero].forEach(function (v) { var td = document.createElement("td"); td.textContent = v; tr.appendChild(td); });
        var td = document.createElement("td"), b = document.createElement("button");
        b.className = "btn b"; b.type = "button"; b.textContent = "Ver RG"; b.style.padding = ".3rem .9rem";
        b.addEventListener("click", function () { openRg(r); });
        td.appendChild(b); tr.appendChild(td); tb.appendChild(tr);
      });
    }
    function openRg(r) {
      var m = $("adm-modal"), img = $("adm-img"); img.removeAttribute("src");
      $("adm-cap").textContent = "#" + r.id + " · " + r.cargo + " · nº " + r.numero; m.hidden = false;
      api("?id=" + r.id).then(function (x) { return x.json(); }).then(function (j) { if (j.rg) img.src = j.rg; });
    }
    function load() {
      var m = $("adm-msg"); msg(m, "Carregando…");
      api().then(function (r) { return r.json().then(function (j) { return { s: r.status, j: j }; }); }).then(function (r) {
        if (r.s === 401) { try { sessionStorage.removeItem("jre_pw"); } catch (e) {} pass = null; $("adm-login").hidden = false; $("adm-panel").hidden = true; return msg($("adm-lmsg"), "Senha incorreta.", true); }
        if (r.s !== 200) { return msg(m, "Erro ao ler o banco (" + (r.j.error || r.s) + ").", true); }
        try { sessionStorage.setItem("jre_pw", pass); } catch (e) {}
        rows = r.j.inscricoes; msg(m, ""); $("adm-login").hidden = true; $("adm-panel").hidden = false;
        var sel = $("adm-filter"), cur = sel.value; sel.length = 1;
        Object.keys(CARGOS).forEach(function (c) { var o = document.createElement("option"); o.textContent = c; o.value = c; sel.appendChild(o); });
        sel.value = cur; render();
      }).catch(function () { msg(m, "Sem conexão com o servidor.", true); });
    }
    $("adm-form").addEventListener("submit", function (e) { e.preventDefault(); pass = $("adm-pw").value; load(); });
    $("adm-filter").addEventListener("change", render);
    $("adm-reload").addEventListener("click", load);
    $("adm-close").addEventListener("click", function () { $("adm-modal").hidden = true; });
    $("adm-modal").addEventListener("click", function (e) { if (e.target === this) this.hidden = true; });
    if (pass) load();
  }
})();
