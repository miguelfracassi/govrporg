// Função serverless (Vercel) que conversa com a API pública do Roblox.
// O navegador não pode chamar o Roblox direto (CORS), então o site chama /api/roblox.
//
//  GET /api/roblox?action=user&name=NICK   -> acha o jogador e devolve id, nome, foto e corpo
//  GET /api/roblox?action=model&id=123     -> metadados do avatar 3D (usado para as costas)
//  GET /api/roblox?action=file&u=URL       -> repassa imagens/arquivos do CDN do Roblox (só rbxcdn.com)

const UA = { "User-Agent": "Mozilla/5.0 (RG-RP generator)", Accept: "application/json" };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function send(res, status, data, cache) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", cache || "no-store");
  res.end(JSON.stringify(data));
}

const fileUrl = (u) => "/api/roblox?action=file&u=" + encodeURIComponent(u);

function cdnUrl(hash) {
  let i = 31;
  for (let k = 0; k < hash.length; k++) i ^= hash.charCodeAt(k);
  return "https://t" + (i % 8) + ".rbxcdn.com/" + hash;
}

async function getJson(url, opts) {
  const r = await fetch(url, Object.assign({ headers: UA }, opts));
  if (!r.ok) throw new Error("HTTP " + r.status + " em " + url);
  return r.json();
}

// miniaturas podem vir como "Pending": tenta algumas vezes
async function thumb(url) {
  for (let i = 0; i < 6; i++) {
    const j = await getJson(url);
    const d = j.data && j.data[0];
    if (d && d.state === "Completed" && d.imageUrl) return d.imageUrl;
    if (d && (d.state === "Blocked" || d.state === "Error")) break;
    await sleep(600);
  }
  return null;
}

async function user(name, res) {
  if (!/^[A-Za-z0-9_]{3,20}$/.test(name || "")) return send(res, 400, { error: "invalid_name" });
  const found = await getJson("https://users.roblox.com/v1/usernames/users", {
    method: "POST",
    headers: Object.assign({ "Content-Type": "application/json" }, UA),
    body: JSON.stringify({ usernames: [name], excludeBannedUsers: true }),
  });
  const u = found.data && found.data[0];
  if (!u) return send(res, 404, { error: "not_found" });

  const [head, body] = await Promise.all([
    thumb("https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" + u.id + "&size=720x720&format=Png&isCircular=false"),
    thumb("https://thumbnails.roblox.com/v1/users/avatar?userIds=" + u.id + "&size=720x720&format=Png&isCircular=false"),
  ]);
  send(res, 200, {
    id: u.id,
    name: u.name,
    displayName: u.displayName,
    headshot: head ? fileUrl(head) : null,
    body: body ? fileUrl(body) : null,
  }, "public, s-maxage=300");
}

async function model(id, res) {
  if (!/^\d{1,15}$/.test(id || "")) return send(res, 400, { error: "invalid_id" });
  let meta = null;
  for (let i = 0; i < 8 && !meta; i++) {
    const j = await getJson("https://thumbnails.roblox.com/v1/users/avatar-3d?userId=" + id);
    if (j.state === "Completed" && j.imageUrl) meta = await getJson(j.imageUrl);
    else await sleep(700);
  }
  if (!meta) return send(res, 504, { error: "model_pending" });
  const textures = {};
  (meta.textures || []).forEach((h) => (textures[h] = fileUrl(cdnUrl(h))));
  send(res, 200, {
    camera: meta.camera,
    aabb: meta.aabb,
    mtl: fileUrl(cdnUrl(meta.mtl)),
    obj: fileUrl(cdnUrl(meta.obj)),
    textures,
  }, "public, s-maxage=300");
}

async function file(u, res) {
  let url;
  try { url = new URL(u); } catch (e) { return send(res, 400, { error: "invalid_url" }); }
  if (url.protocol !== "https:" || !/^[a-z0-9-]+\.rbxcdn\.com$/i.test(url.hostname)) {
    return send(res, 400, { error: "host_not_allowed" });
  }
  const r = await fetch(url.href, { headers: { "User-Agent": UA["User-Agent"] } });
  if (!r.ok) return send(res, 502, { error: "upstream_" + r.status });
  const buf = Buffer.from(await r.arrayBuffer());
  res.statusCode = 200;
  res.setHeader("Content-Type", r.headers.get("content-type") || "application/octet-stream");
  res.setHeader("Cache-Control", "public, max-age=86400, s-maxage=86400");
  res.end(buf);
}

module.exports = async (req, res) => {
  const q = new URL(req.url, "http://x").searchParams;
  try {
    const a = q.get("action");
    if (a === "user") return await user((q.get("name") || "").trim(), res);
    if (a === "model") return await model(q.get("id"), res);
    if (a === "file") return await file(q.get("u"), res);
    send(res, 400, { error: "invalid_action" });
  } catch (e) {
    send(res, 502, { error: "roblox_unavailable", detail: String(e.message || e) });
  }
};
