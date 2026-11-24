// Inscrições de candidatos (banco Neon da Vercel).
// Variável de ambiente: DATABASE_URL (a integração Neon da Vercel já cria) e, opcional, ADMIN_PASSWORD (padrão 2015).
//
//  POST /api/inscricoes            -> {cargo, numero, rg (dataURL de imagem), aceite}   (público)
//  GET  /api/inscricoes            -> lista (header x-admin-password)
//  GET  /api/inscricoes?id=N       -> imagem do RG de uma inscrição (header x-admin-password)

const { neon } = require("@neondatabase/serverless");

const CARGOS = {
  "DEPUTADO FEDERAL (ROBLOXIANO)": 4,
  "DEPUTADO ESTADUAL (ROBLOXIANO)": 5,
  "SENADOR (ROBLOXIANO)": 3,
  "GOVERNADOR (ROBLOXIANO)": 2,
  "PRESIDENTE (ROBLOXIANO)": 2,
};
const SENHA = process.env.ADMIN_PASSWORD || "2015";
const MAX_RG = 1500000; // ~1,5 MB em texto (o navegador já reduz a imagem)

let sql, ready;
function db() {
  if (!sql) {
    const url = process.env.DATABASE_URL || process.env.POSTGRES_URL;
    if (!url) throw new Error("DATABASE_URL não configurada");
    sql = neon(url);
  }
  return sql;
}
function setup() {
  if (!ready) {
    const q = db();
    ready = (async () => {
      await q`CREATE TABLE IF NOT EXISTS inscricoes (
        id SERIAL PRIMARY KEY,
        cargo TEXT NOT NULL,
        numero TEXT NOT NULL,
        rg_imagem TEXT NOT NULL,
        aceitou_termos BOOLEAN NOT NULL DEFAULT TRUE,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )`;
      await q`CREATE UNIQUE INDEX IF NOT EXISTS inscricoes_cargo_numero ON inscricoes (cargo, numero)`;
    })().catch((e) => { ready = null; throw e; });
  }
  return ready;
}

function send(res, status, data) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(data));
}
function readBody(req) {
  if (req.body && typeof req.body === "object") return Promise.resolve(req.body);
  return new Promise((ok, no) => {
    let s = "";
    req.on("data", (c) => { s += c; if (s.length > 3e6) { no(new Error("grande")); req.destroy(); } });
    req.on("end", () => { try { ok(JSON.parse(s || "{}")); } catch (e) { no(e); } });
    req.on("error", no);
  });
}
const autorizado = (req) => String(req.headers["x-admin-password"] || "") === SENHA;

module.exports = async (req, res) => {
  try {
    await setup();
    const q = db();

    if (req.method === "POST") {
      const b = await readBody(req);
      const cargo = String(b.cargo || "");
      const numero = String(b.numero || "");
      const rg = String(b.rg || "");
      if (!(cargo in CARGOS)) return send(res, 400, { error: "cargo_invalido" });
      if (!new RegExp("^\\d{" + CARGOS[cargo] + "}$").test(numero)) return send(res, 400, { error: "numero_invalido" });
      if (!/^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(rg) || rg.length > MAX_RG) return send(res, 400, { error: "rg_invalido" });
      if (b.aceite !== true) return send(res, 400, { error: "sem_aceite" });

      const dup = await q`SELECT 1 FROM inscricoes WHERE cargo = ${cargo} AND numero = ${numero} LIMIT 1`;
      if (dup.length) return send(res, 409, { error: "numero_em_uso" });
      try {
        const r = await q`INSERT INTO inscricoes (cargo, numero, rg_imagem, aceitou_termos) VALUES (${cargo}, ${numero}, ${rg}, TRUE) RETURNING id`;
        return send(res, 201, { ok: true, protocolo: r[0].id });
      } catch (e) {
        if (String(e.message || e).includes("duplicate")) return send(res, 409, { error: "numero_em_uso" });
        throw e;
      }
    }

    if (req.method === "GET") {
      if (!autorizado(req)) return send(res, 401, { error: "senha_incorreta" });
      const id = new URL(req.url, "http://x").searchParams.get("id");
      if (id) {
        if (!/^\d+$/.test(id)) return send(res, 400, { error: "id_invalido" });
        const r = await q`SELECT rg_imagem FROM inscricoes WHERE id = ${Number(id)}`;
        return r.length ? send(res, 200, { rg: r[0].rg_imagem }) : send(res, 404, { error: "nao_encontrado" });
      }
      const rows = await q`SELECT id, cargo, numero, aceitou_termos, criado_em FROM inscricoes ORDER BY id DESC`;
      return send(res, 200, { total: rows.length, inscricoes: rows });
    }

    send(res, 405, { error: "metodo_nao_permitido" });
  } catch (e) {
    console.error(e);
    send(res, 500, { error: "erro_interno", detail: String(e.message || e) });
  }
};
