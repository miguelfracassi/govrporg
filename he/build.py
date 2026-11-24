# -*- coding: utf-8 -*-
# Gerador do portal "Governo do Roleplay" (site fictício). Rode: python3 build.py
import os, json, shutil

# ====== CONFIGURAÇÕES (edite aqui) ======
NOME = "Governo do Roleplay"
DISCORD = "#"  # troque pelo link do Discord do seu servidor
PRESIDENTE = "Nome do(a) Presidente"
VICE = "Nome do(a) Vice-Presidente"
OUT = "dist"

ICONS = {
 "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
 "vote": '<path d="M3 14h18v6H3zM7 14V5h10v9"/><path d="M10 9l1.5 1.5L14.5 7"/>',
 "gov": '<path d="M3 21h18M5 21V10M9 21V10M15 21V10M19 21V10M3 10l9-6 9 6z"/>',
 "scale": '<path d="M12 3v18M6 21h12M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
 "news": '<path d="M4 5h14v14H6a2 2 0 0 1-2-2zM18 9h2v8a2 2 0 0 1-2 2M8 9h6M8 13h6"/>',
 "id": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16c.5-2 5.5-2 6 0M15 10h3M15 14h3"/>',
 "chart": '<path d="M4 20V4M4 20h16M8 16v-5M12 16V8M16 16v-3"/>',
 "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-4 3-6 6-6s6 2 6 6M16 5a3 3 0 0 1 0 6M18 14c2 .8 3 3 3 6"/>',
 "brief": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 13h18"/>',
 "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
 "book": '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3zM5 17a3 3 0 0 1 3-3h11"/>',
 "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
 "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "flag": '<path d="M5 21V4M5 4h12l-2 4 2 4H5"/>',
 "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
 "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
 "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
 "access": '<circle cx="12" cy="5" r="2"/><path d="M5 9l7 1 7-1M12 10v5l-3 5M12 15l3 5"/>',
 "map": '<path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2zM9 4v14M15 6v14"/>',
 "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7M12 17v.5"/>',
 "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.5 4-7 8-7s8 2.5 8 7"/>',
 "warn": '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16.5v.5"/>',
}
def ICONS_SVG(n): return '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % ICONS[n]
def ic(n, cls="", wrap=True):
    s = '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % ICONS[n]
    return '<span class="ico %s">%s</span>' % (cls, s) if wrap else s

# ====== helpers de conteúdo ======
def P(*t): return "".join("<p>%s</p>" % x for x in t)
def H2(t): return "<h2>%s</h2>" % t
def H3(t): return "<h3>%s</h3>" % t
def UL(i): return "<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in i)
def STEPS(i): return '<ol class="steps">%s</ol>' % "".join("<li>%s</li>" % x for x in i)
def ALERT(t, info=False): return '<div class="alert%s">%s</div>' % (" i" if info else "", t)
def TABLE(h, rows):
    th = "".join("<th>%s</th>" % x for x in h)
    tr = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r) for r in rows)
    return '<div class="table"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, tr)
def FAQ(q): return "".join("<details><summary>%s</summary><p>%s</p></details>" % (a, b) for a, b in q)
def U(slug): return "/pt-br/%s/" % slug if slug else "/"
def CARDS(items):
    out = ""
    for ico, col, t, d, slug in items:
        tag = "a" if slug else "div"
        href = ' href="%s"' % U(slug) if slug else ""
        out += '<%s class="card"%s>%s<h3>%s</h3><p>%s</p></%s>' % (tag, href, ic(ico, col), t, d, tag)
    return '<div class="grid">%s</div>' % out

DISCLAIMER = "Este é um site <strong>fictício</strong>, criado apenas para fins de <strong>roleplay (RP)</strong>. Não tem qualquer ligação com o Governo do Brasil, com o gov.br ou com qualquer órgão público real. Nomes, cargos, leis, números e eventos são inventados; qualquer semelhança com a realidade é mera coincidência."

NEWS = [
 ("Eleições", "23/11/2026", "Calendário das Eleições RP é divulgado", "O Tribunal Superior Eleitoral do Roleplay publicou as datas de registro de candidaturas, campanha e votação.", "vote", "var(--blue)"),
 ("Serviços", "20/11/2026", "Nova emissão de RG-RP já está disponível", "Cidadãos podem solicitar o documento de identidade do Roleplay direto pelo portal, sem fila.", "id", "var(--green)"),
 ("Congresso", "18/11/2026", "Congresso aprova o Código de Conduta do RP", "O texto define regras de convivência e prevê penalidades proporcionais para infrações.", "gov", "var(--red)"),
 ("Concursos", "14/11/2026", "Abertas as inscrições para novas vagas públicas", "Há oportunidades em diversos ministérios para quem quer atuar no governo.", "brief", "var(--navy)"),
 ("Transparência", "10/11/2026", "Portal da Transparência ganha painel de gastos", "Qualquer cidadão pode acompanhar como o orçamento fictício é aplicado.", "chart", "var(--blue)"),
 ("Justiça", "05/11/2026", "Poder Judiciário amplia atendimento a denúncias", "Casos agora podem ser abertos por formulário e acompanhados por protocolo.", "scale", "var(--green)"),
]

# slug: (título, descrição, grupo, ícone, cor, corpo)
PAGES = {}
def add(slug, title, desc, group, icon, color, body): PAGES[slug] = (title, desc, group, icon, color, body)

add("servicos", "Serviços", "Catálogo com todos os serviços oferecidos ao cidadão do Roleplay.", "Cidadão", "search", "",
 P("Encontre abaixo os serviços do portal. Todos são simulados e fazem parte da brincadeira de roleplay.") +
 CARDS([
  ("id", "c-g", "Emitir RG-RP", "Gere o seu documento com nick, foto e assinatura.", "gerar-rg-rp"),
  ("id", "", "Documentos", "RG-RP, título de eleitor, CNH-RP e certidões.", "cidadania"),
  ("vote", "c-g", "Eleições RP", "Calendário, candidatos e situação eleitoral.", "eleicoes-rp"),
  ("brief", "c-y", "Concursos e vagas", "Inscreva-se para trabalhar no governo.", "concursos-e-vagas"),
  ("scale", "c-r", "Justiça", "Abra uma denúncia ou consulte um processo.", "justica-rp"),
  ("book", "c-n", "Leis e decretos", "Consulte a legislação vigente do RP.", "leis-e-decretos"),
  ("chart", "", "Transparência", "Gastos, servidores e pedidos de informação.", "transparencia"),
  ("chat", "c-g", "Ouvidoria", "Elogios, sugestões, reclamações e denúncias.", "ouvidoria"),
  ("users", "c-y", "Partidos políticos", "Conheça os partidos e como fundar um.", "partidos-politicos"),
 ]))

add("cidadania", "Documentos e cidadania", "Como emitir RG-RP, título de eleitor, CNH-RP e certidões.", "Cidadão", "id", "", 
 H2("Documentos disponíveis") +
 TABLE(["Documento", "Para que serve", "Prazo"], [
  ["RG-RP", "Identificação oficial dentro do roleplay (<a href=\"/pt-br/gerar-rg-rp/\">emitir agora</a>)", "Imediato"],
  ["Título de eleitor RP", "Votar e se candidatar nas eleições", "Imediato"],
  ["CNH-RP", "Dirigir veículos nos servidores que exigirem habilitação", "Até 24 horas"],
  ["Certidão de cidadania", "Comprovar tempo de residência no RP", "Até 48 horas"],
 ]) + H2("Como emitir seu RG-RP") +
 STEPS(["Abra a página <a href=\"/pt-br/gerar-rg-rp/\">Emitir RG-RP</a>.", "Digite o seu nick do Roblox e confirme que é você.", "Faça a sua assinatura.", "Baixe o seu RG-RP em imagem."]) +
 ALERT("Cada pessoa pode ter um documento por personagem. Dados falsos de pessoas reais são proibidos.", True))

RG_BODY = (
 P("Crie o seu RG-RP em poucos passos: digite o seu nick do Roblox, confirme que é você, faça a sua assinatura e baixe o documento.") +
 ALERT("O RG-RP é um documento <strong>fictício</strong>, só para roleplay. Não tem ligação com o RG real nem com nenhum órgão do Governo Federal.", True) +
 '''<div class="rg" id="rg">
<ol class="rg-steps" aria-label="Etapas"><li class="on"><span>1</span>Nick</li><li><span>2</span>Confirmar</li><li><span>3</span>Assinar</li><li><span>4</span>Pronto</li></ol>

<section data-step="1">
 <h2>Qual é o seu nick do Roblox?</h2>
 <form class="f" id="rg-nick-form" autocomplete="off">
  <label>Nick (nome de usuário)<input id="rg-nick" required maxlength="21" placeholder="Ex.: Builderman" autocapitalize="none" spellcheck="false"></label>
  <button class="btn b" type="submit">Buscar no Roblox</button>
 </form>
 <div class="alert i result" id="rg-nick-msg" role="status"></div>
</section>

<section data-step="2" hidden>
 <h2>É você mesmo?</h2>
 <div class="rg-conf"><img id="rg-conf-img" alt="Foto do avatar encontrado" width="140" height="140"><div><strong id="rg-conf-display"></strong><br><span id="rg-conf-user"></span></div></div>
 <div class="rg-actions"><button class="btn b" id="rg-yes" type="button">Sim, sou eu</button><button class="btn rg-ghost" id="rg-no" type="button">Não, buscar outro nick</button></div>
</section>

<section data-step="3" hidden>
 <h2>Faça a sua assinatura</h2>
 <p>Desenhe com o mouse, o dedo ou a caneta no quadro abaixo.</p>
 <div class="rg-padbox"><canvas id="rg-pad" width="900" height="300" aria-label="Quadro de assinatura"></canvas><span id="rg-pad-hint">Assine aqui</span></div>
 <div class="alert i result" id="rg-sign-msg" role="status"></div>
 <div class="rg-actions"><button class="btn b" id="rg-gen" type="button">Gerar meu RG-RP</button><button class="btn rg-ghost" id="rg-clear" type="button">Limpar</button><button class="btn rg-ghost" id="rg-back-1" type="button">Voltar</button></div>
</section>

<section data-step="4" hidden>
 <h2>Seu RG-RP está pronto</h2>
 <p><strong id="rg-name"></strong> · Nº <span id="rg-num"></span></p>
 <div class="rg-preview"><canvas id="rg-out" width="1007" height="1562" aria-label="Seu RG-RP gerado"></canvas></div>
 <div class="alert result" id="rg-fallback" role="status" hidden>Não deu para montar as costas do personagem agora, então usei a imagem de frente. Gere de novo mais tarde se quiser.</div>
 <div class="rg-actions"><button class="btn b" id="rg-save" type="button">Baixar RG-RP (PNG)</button><button class="btn rg-ghost" id="rg-edit-sign" type="button">Refazer assinatura</button><button class="btn rg-ghost" id="rg-redo" type="button">Gerar outro</button></div>
</section>
</div>''')

add("gerar-rg-rp", "Emitir RG-RP", "Gere o seu RG-RP com o nick do Roblox, foto do avatar e assinatura.", "Cidadão", "id", "c-g", RG_BODY)

add("eleicoes-rp", "Eleições RP", "Calendário, candidatos, como votar e consulta de situação eleitoral.", "Cidadão", "vote", "c-g",
 P("As Eleições RP escolhem, de forma democrática, quem vai governar o roleplay. Todo cidadão com título regular pode votar e se candidatar.") +
 H2("Calendário eleitoral") +
 TABLE(["Fase", "Período"], [["Filiação a partidos", "A definir"], ["Registro de candidaturas", "A definir"], ["Campanha eleitoral", "A definir"], ["Votação", "A definir"], ["Divulgação do resultado", "A definir"], ["Posse", "A definir"]]) +
 H2("Cargos em disputa") +
 TABLE(["Cargo", "Mandato", "Vagas"], [["Presidente da República", "A definir", "1"], ["Vice-Presidente", "Chapa do presidente", "1"], ["Senadores", "A definir", "3"], ["Deputados", "A definir", "10"]]) +
 H2("Candidatos") +
 '<div class="cands">' + "".join('<div class="cand"><div class="ph"><svg viewBox="0 0 24 24">%s</svg></div><strong>Candidato(a) %d</strong><br><small>Partido a definir · Nº 0%d</small></div>' % (ICONS["user"], i, i) for i in range(1, 5)) + "</div>" +
 H2("Como votar") +
 STEPS(["Confira se seu título de eleitor RP está regular.", "Na data da votação, acesse o canal de votação no Discord.", "Escolha o número do seu candidato.", "Confirme seu voto. Ele é secreto e só pode ser dado uma vez."]) +
 H2("Quer ser candidato?") + P("Cadastre a sua candidatura em poucos passos.") + '<p><a class="btn b" href="/jre/eleicoes/inscricoes/">Inscrever candidatura</a></p>' + H2("Consulte sua situação eleitoral") +
 '<form class="f" id="elegivel"><label>Nome do personagem<input required autocomplete="off"></label><label>Número do título<input required inputmode="numeric" placeholder="0000 0000 0000"></label><button class="btn b" type="submit">Consultar</button></form><div class="alert i result" id="res" role="status"></div>')

add("partidos-politicos", "Partidos políticos", "Partidos registrados e como fundar o seu.", "Cidadão", "users", "c-y",
 P("Os partidos reúnem cidadãos com ideias parecidas. Os nomes abaixo são exemplos: troque pelos partidos do seu roleplay.") +
 TABLE(["Partido", "Sigla", "Número"], [["Partido Progressista do Roleplay", "PPR", "11"], ["Partido Democrático Roleplay", "PDR", "22"], ["União Cívica RP", "UCRP", "33"], ["Movimento Cidadão RP", "MCRP", "44"]]) +
 H2("Como fundar um partido") + STEPS(["Reúna pelo menos 5 cidadãos fundadores.", "Escolha nome, sigla e número.", "Escreva o estatuto com ideias e regras internas.", "Envie o pedido de registro ao Tribunal Eleitoral."]))

add("concursos-e-vagas", "Concursos e vagas", "Vagas abertas para trabalhar no governo do Roleplay.", "Cidadão", "brief", "c-y",
 TABLE(["Cargo", "Órgão", "Vagas", "Situação"], [["Analista de Atendimento", "Ouvidoria", "3", "Inscrições abertas"], ["Assessor de Imprensa", "Secretaria de Comunicação", "2", "Inscrições abertas"], ["Fiscal Eleitoral", "Tribunal Eleitoral", "5", "Em breve"], ["Oficial de Justiça", "Poder Judiciário", "2", "Encerrado"]]) +
 H2("Como se inscrever") + STEPS(["Tenha um RG-RP válido.", "Escolha a vaga e abra um chamado no Discord.", "Envie seu pequeno currículo de personagem.", "Aguarde a avaliação e o resultado."]))

add("justica-rp", "Poder Judiciário", "Tribunais, denúncias e como acompanhar processos.", "Governo", "scale", "c-r",
 P("O Poder Judiciário do Roleplay garante que as regras da comunidade sejam cumpridas com justiça e imparcialidade.") +
 H2("Órgãos") + UL(["<strong>Supremo Tribunal do RP:</strong> guarda a Constituição do roleplay.", "<strong>Tribunal Eleitoral:</strong> organiza e fiscaliza as eleições.", "<strong>Varas comuns:</strong> julgam conflitos entre cidadãos."]) +
 H2("Como abrir uma denúncia") + STEPS(["Reúna provas, como prints e links de mensagens.", "Abra um chamado de denúncia no Discord.", "Receba o número de protocolo.", "Acompanhe o andamento pelo mesmo canal."]) +
 ALERT("Denúncias falsas podem gerar penalidades para quem as fez."))

add("presidencia", "Presidência da República", "Chefia do governo do Roleplay.", "Governo", "flag", "",
 P("A Presidência é responsável por dirigir o governo, nomear ministros e sancionar leis aprovadas no Congresso.") +
 TABLE(["Cargo", "Ocupante"], [["Presidente da República", PRESIDENTE], ["Vice-Presidente", VICE]]) +
 H2("Atribuições") + UL(["Chefiar o governo e a administração pública.", "Nomear e demitir ministros.", "Sancionar ou vetar leis.", "Representar o RP em relações com outros servidores."]) +
 ALERT("Para trocar os nomes, edite PRESIDENTE e VICE no início do arquivo build.py.", True))

add("congresso-nacional", "Congresso Nacional", "Senado, Câmara dos Deputados e como as leis são criadas.", "Governo", "gov", "c-g",
 P("O Congresso é formado pelo Senado e pela Câmara dos Deputados. É lá que propostas viram leis.") +
 H2("Como uma lei é criada") + STEPS(["Um parlamentar ou cidadão apresenta um projeto.", "A Câmara debate e vota.", "O Senado revisa e vota.", "A Presidência sanciona ou veta.", "A lei é publicada no Diário Oficial."]) +
 H2("Composição") + TABLE(["Casa", "Membros"], [["Senado Federal do RP", "3"], ["Câmara dos Deputados do RP", "10"]]))

add("ministerios", "Ministérios", "Conheça os ministérios e o que cada um faz.", "Governo", "gov", "c-n",
 CARDS([
  ("chart", "", "Fazenda", "Economia e orçamento do RP.", None), ("scale", "c-r", "Justiça e Segurança", "Ordem e proteção aos cidadãos.", None),
  ("users", "c-g", "Saúde", "Bem-estar da população.", None), ("book", "c-y", "Educação", "Escolas, cursos e eventos de aprendizado.", None),
  ("map", "c-n", "Cidades e Obras", "Construções e espaços públicos.", None), ("flag", "", "Relações Exteriores", "Parcerias com outros servidores.", None),
  ("shield", "c-r", "Defesa", "Proteção do território do RP.", None), ("mic", "c-g", "Comunicação", "Imprensa e divulgação oficial.", None),
 ]))

add("noticias", "Notícias", "Últimas notícias do governo do Roleplay.", "Informação", "news", "",
 "".join('<article class="card" style="margin-bottom:1rem"><span class="tag">%s</span> <time>%s</time><h3>%s</h3><p>%s</p></article>' % (t, d, h, x) for t, d, h, x, _, _ in NEWS))

add("diario-oficial", "Diário Oficial", "Publicações oficiais de leis, decretos e nomeações.", "Informação", "doc", "c-y",
 P("O Diário Oficial reúne os atos do governo. Veja as edições mais recentes (exemplos).") +
 TABLE(["Edição", "Data", "Conteúdo"], [["Nº 12", "23/11/2026", "Decreto de convocação das eleições"], ["Nº 11", "18/11/2026", "Lei do Código de Conduta"], ["Nº 10", "10/11/2026", "Nomeações do Ministério da Fazenda"], ["Nº 09", "02/11/2026", "Portaria sobre atendimento ao cidadão"]]))

add("leis-e-decretos", "Leis e decretos", "Consulte a legislação do Roleplay.", "Informação", "book", "c-n",
 TABLE(["Número", "Assunto", "Situação"], [["Lei nº 001/2026", "Constituição do Roleplay", "Em vigor"], ["Lei nº 002/2026", "Código de Conduta", "Em vigor"], ["Decreto nº 001/2026", "Regulamento das eleições", "Em vigor"], ["Lei nº 003/2026", "Lei de Acesso à Informação", "Em vigor"]]) +
 ALERT("Os textos acima são exemplos. Substitua pelas regras reais do seu servidor.", True))

add("transparencia", "Transparência", "Dados abertos, gastos e pedidos de informação.", "Informação", "eye", "",
 P("Todo cidadão tem direito de saber como o governo funciona.") +
 '<div class="nums"><div><b>10</b>ministérios</div><div><b>48</b>servidores</div><div><b>12</b>leis publicadas</div><div><b>96%</b>pedidos respondidos</div></div>' +
 H2("Pedido de informação") + P("Envie sua pergunta pela Ouvidoria. A resposta é dada em até 20 dias.") + '<p><a class="btn b" href="/pt-br/ouvidoria/">Fazer um pedido</a></p>')

add("imprensa", "Sala de imprensa", "Contatos e materiais para jornalistas e criadores de conteúdo.", "Informação", "mic", "c-r",
 P("Jornalistas e criadores de conteúdo do RP podem solicitar entrevistas, notas e materiais oficiais.") + UL(["Logotipo oficial em PNG", "Calendário de eventos", "Notas à imprensa"]) +
 '<p><a class="btn b" href="/pt-br/ouvidoria/">Falar com a assessoria</a></p>')

add("ouvidoria", "Ouvidoria", "Registre elogios, sugestões, reclamações e denúncias.", "Institucional", "chat", "c-g",
 P("Sua opinião ajuda o governo a melhorar. Preencha o formulário abaixo.") +
 '<form class="f" id="ouv"><label>Nome<input required></label><label>Tipo<select><option>Sugestão</option><option>Elogio</option><option>Reclamação</option><option>Denúncia</option><option>Pedido de informação</option></select></label><label>Mensagem<textarea rows="5" required></textarea></label><button class="btn b" type="submit">Enviar</button></form><div class="alert i result" id="res" role="status"></div>' +
 P('Prefere falar ao vivo? Entre no <a href="%s">Discord oficial</a>.' % DISCORD))

add("sobre", "Sobre o portal", "O que é o Governo do Roleplay.", "Institucional", "info", "",
 P("O Governo do Roleplay é um portal fictício que organiza serviços, leis, eleições e informações de uma sociedade criada para brincar de roleplay.") + ALERT(DISCLAIMER))

add("perguntas-frequentes", "Perguntas frequentes", "Respostas rápidas sobre o portal.", "Institucional", "help", "c-y",
 FAQ([("Este site é oficial?", "Não. Ele é fictício e feito apenas para roleplay."), ("Preciso pagar por algum serviço?", "Não. Todos os serviços são gratuitos e simulados."), ("Como falo com a equipe?", "Pela Ouvidoria ou pelo Discord oficial."), ("Posso me candidatar?", "Sim, desde que tenha título de eleitor RP regular.")]))

add("acessibilidade", "Acessibilidade", "Recursos para facilitar a leitura e a navegação.", "Institucional", "access", "",
 P("O portal oferece ajustes de tamanho de letra (A+ e A-) e alto contraste, na faixa amarela no topo de todas as páginas. A navegação funciona com teclado e há link para pular direto ao conteúdo."))

add("privacidade", "Política de privacidade", "Como tratamos os dados no portal.", "Institucional", "shield", "c-g",
 P("Este portal não coleta dados reais. Os formulários são simulados e nada é enviado a servidores. Preferências de acessibilidade ficam apenas no seu navegador."))

add("termos-de-uso", "Termos de uso", "Regras para usar o portal.", "Institucional", "doc", "c-n",
 UL(["Use o portal apenas para fins de roleplay.", "Não se passe por pessoas ou órgãos reais.", "Não publique dados pessoais reais.", "Respeite as regras do servidor."]) + ALERT(DISCLAIMER))

add("mapa-do-site", "Mapa do site", "Lista de todas as páginas do portal.", "Institucional", "map", "c-y", "@@MAPA@@")

# ====== template ======
NAV = [("", "Início"), ("servicos", "Serviços"), ("eleicoes-rp", "Eleições RP"), ("presidencia", "Governo"), ("noticias", "Notícias"), ("transparencia", "Transparência"), ("ouvidoria", "Ouvidoria")]
GROUPS = ["Cidadão", "Governo", "Informação", "Institucional"]

def head(title, desc):
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — {NOME} (fictício)</title><meta name="description" content="{desc}"><meta name="theme-color" content="#06194d">
<link rel="icon" href="/assets/img/favicon.png"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/rawline-200.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="/assets/css/style.css"></head><body>
<a class="skip" href="#main">Ir para o conteúdo</a>
'''

def header(cur):
    nav = "".join('<li><a href="%s"%s>%s</a></li>' % (U(s), ' aria-current="page"' if s == cur else "", t) for s, t in NAV)
    return f'''<header class="site"><div class="wrap hrow"><a class="brand" href="/"><img src="/assets/img/logo.png" alt=""><div><span>{NOME}</span><small>Portal oficial (fictício)</small></div></a>
<form class="hsearch" action="/pt-br/busca/" role="search"><input name="q" placeholder="O que você procura?" aria-label="Buscar no portal"><button aria-label="Buscar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">{ICONS["search"]}</svg></button></form>
<a class="hs-ico" href="/pt-br/busca/" aria-label="Buscar"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">{ICONS["search"]}</svg></a><a class="enter" href="{DISCORD}">Entrar no Discord</a><button class="menu-btn" data-act="menu" aria-expanded="false" aria-controls="nav"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg><span>Menu</span></button></div>
<nav class="nav" id="nav" aria-label="Principal"><div class="wrap"><ul>{nav}</ul></div></nav></header>'''

def footer():
    def col(t, items): return "<div><h2>%s</h2><ul>%s</ul></div>" % (t, "".join('<li><a href="%s">%s</a></li>' % (U(s), PAGES[s][0]) for s in items))
    return f'''<div class="stripe"><i></i><i></i><i></i><i></i></div><footer class="site"><div class="wrap fgrid">
<div><a class="brand" href="/"><img src="/assets/img/logo.png" alt=""><div><span>{NOME}</span><small>Portal fictício</small></div></a><p>Serviços, leis, eleições e notícias de uma sociedade criada para o roleplay.</p></div>
{col("Cidadão", ["servicos", "gerar-rg-rp", "cidadania", "eleicoes-rp", "concursos-e-vagas"])}{col("Governo", ["presidencia", "congresso-nacional", "ministerios", "justica-rp"])}{col("Institucional", ["sobre", "ouvidoria", "acessibilidade", "privacidade", "termos-de-uso", "mapa-do-site"])}</div>
<div class="acc"><div class="wrap"><strong>Acessibilidade</strong><div class="tools"><button data-act="fm" aria-label="Diminuir letra">A-</button><button data-act="fp" aria-label="Aumentar letra">A+</button><button data-act="hc">Alto contraste</button></div></div></div><div class="fict"><div class="wrap"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS["warn"]}</svg><p style="margin:0"><strong>Aviso importante:</strong> {DISCLAIMER}</p></div></div></footer><script src="/assets/js/main.js"></script></body></html>'''

def write(path, html):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(html)

def page(slug, title, desc, group, body, extra=""):
    side = ""
    if group:
        li = "".join('<li><a href="%s"%s>%s</a></li>' % (U(s), ' aria-current="page"' if s == slug else "", v[0]) for s, v in PAGES.items() if v[2] == group)
        side = '<aside class="side"><h2>%s</h2><ul>%s</ul></aside>' % (group, li)
    return head(title, desc) + header(slug) + f'''<main id="main"><div class="pagehead"><div class="wrap"><div class="crumb"><a href="/">Início</a><span>/</span>{title}</div><h1>{title}</h1><p>{desc}</p></div></div><div class="stripe"><i></i><i></i><i></i><i></i></div>
<div class="wrap layout">{side}<div class="content">{body}</div></div></main>''' + extra + footer()

# mapa do site
mapa = "".join(H2(g) + UL(['<a href="%s">%s</a> — %s' % (U(s), v[0], v[1]) for s, v in PAGES.items() if v[2] == g]) for g in GROUPS)
mapa += H2("Outras") + UL(['<a href="/">Página inicial</a>', '<a href="/pt-br/busca/">Busca</a>'])
t, d, g, i, c, b = PAGES["mapa-do-site"]; PAGES["mapa-do-site"] = (t, d, g, i, c, mapa)

# ====== gerar ======
shutil.rmtree(OUT, ignore_errors=True)
shutil.copytree("assets", os.path.join(OUT, "assets"))
EXTRA = {"gerar-rg-rp": '<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script><script src="/assets/js/rg.js"></script>'}
for slug, (t, d, g, i, c, b) in PAGES.items():
    write("pt-br/%s/index.html" % slug, page(slug, t, d, g, b, EXTRA.get(slug, "")))

index = [{"t": v[0], "d": v[1], "u": U(s)} for s, v in PAGES.items()]
busca = '<form class="f" action="/pt-br/busca/" role="search"><label>Buscar no portal<input id="bq" name="q" autofocus></label><button class="btn b" type="submit">Buscar</button></form><p id="scount" role="status"></p><ul class="sres" id="sres"></ul>'
write("pt-br/busca/index.html", page("busca", "Busca", "Pesquise páginas e serviços do portal.", None, busca, "<script>window.SITE_INDEX=%s</script>" % json.dumps(index, ensure_ascii=False)).replace('<div class="wrap layout">', '<div class="wrap layout" style="grid-template-columns:1fr">'))


# ====== inscrições de candidatos (/jre/eleicoes/inscricoes) e painel admin ======
CARGOS = [("DEPUTADO FEDERAL (ROBLOXIANO)", 4), ("DEPUTADO ESTADUAL (ROBLOXIANO)", 5), ("SENADOR (ROBLOXIANO)", 3), ("GOVERNADOR (ROBLOXIANO)", 2), ("PRESIDENTE (ROBLOXIANO)", 2)]
TERMOS = [
 "Ao enviar esta inscrição, a pessoa que se candidata declara que leu e entendeu todos os itens abaixo, escritos e ditos a partir deste termo de envio para candidato a <b id=\"in-terms-cargo\">o cargo escolhido</b>.",
 "1. Este é um processo eleitoral <b>fictício</b>, criado apenas para o jogo de roleplay. Ser eleito(a) <b>não torna ninguém presidente, governador, senador ou deputado do Roblox, nem da vida real</b>. O cargo existe somente dentro do nosso jogo.",
 "2. Nenhum cargo, título ou resultado obtido aqui tem valor legal, político ou financeiro fora do roleplay, e não tem ligação com o Roblox Corporation, com a Justiça Eleitoral, com o Governo do Brasil ou com qualquer órgão real.",
 "3. O documento anexado deve ser o <b>RG-RP</b> gerado neste portal. É proibido enviar documentos reais, fotos de pessoas reais ou dados pessoais reais (nome completo, CPF, endereço, telefone etc.).",
 "4. Cada pessoa pode inscrever apenas um personagem por cargo. Inscrições com RG-RP de outra pessoa, números repetidos ou informações falsas poderão ser recusadas e a candidatura cancelada, sem aviso prévio.",
 "5. O número de candidato é definido pelo cargo (Deputado Federal: 4 números; Deputado Estadual: 5; Senador: 3; Governador: 2; Presidente: 2) e não pode ser igual ao de outro candidato do mesmo cargo.",
 "6. A organização das eleições pode analisar, aprovar, recusar ou cancelar qualquer inscrição, e alterar datas e regras do calendário eleitoral do roleplay, sempre divulgando as mudanças no portal.",
 "7. É proibido fazer campanha com ofensas, discriminação, ameaças, golpes, promessas de dinheiro real ou de itens reais (Robux, contas, etc.) em troca de votos. Quem descumprir poderá perder a candidatura.",
 "8. A imagem do RG-RP e as informações enviadas ficam guardadas apenas para a organização das eleições do roleplay e podem ser apagadas quando o evento terminar.",
 "9. Ao marcar a caixa de aceite, a pessoa concorda com todos os termos acima e confirma que a candidatura é uma brincadeira de roleplay.",
 "Fim dos termos.",
]
INSC_BODY = (
 P("Cadastre a sua candidatura para as Eleições RP. Você vai precisar do seu <a href=\"/pt-br/gerar-rg-rp/\">RG-RP</a>, escolher o cargo, informar o número e ler os termos.") +
 '<div class="rg" id="insc"><ol class="rg-steps" aria-label="Etapas"><li class="on"><span>1</span>RG</li><li><span>2</span>Cargo</li><li><span>3</span>Número</li><li><span>4</span>Termos</li></ol>'
 '<section data-step="1"><h2>Anexe o seu RG-RP</h2><p>Envie a imagem do RG-RP gerado no portal (PNG ou JPG).</p>'
 '<div class="f"><label>Imagem do RG-RP<input type="file" id="in-rg" accept="image/*"></label></div><img id="in-prev" class="in-prev" alt="Prévia do RG anexado" hidden>'
 '<div class="alert i result" id="in-m1" role="status"></div><div class="rg-actions"><button class="btn b" type="button" id="in-next1">Continuar</button><a class="btn rg-ghost" href="/pt-br/gerar-rg-rp/">Ainda não tenho RG-RP</a></div></section>'
 '<section data-step="2" hidden><h2>Escolha o cargo</h2><div class="cargos">' +
 "".join('<label class="cg"><input type="radio" name="cargo" value="%s"><span><b>%s</b><small>%d números</small></span></label>' % (c, c, n) for c, n in CARGOS) +
 '</div><div class="alert i result" id="in-m2" role="status"></div><div class="rg-actions"><button class="btn b" type="button" id="in-next2">Continuar</button><button class="btn rg-ghost" type="button" id="in-back2">Voltar</button></div></section>'
 '<section data-step="3" hidden><h2>Número do candidato</h2><div class="f" style="max-width:360px"><label><span id="in-num-label">Número</span><input id="in-num" inputmode="numeric" autocomplete="off"></label></div>'
 '<div class="alert i result" id="in-m3" role="status"></div><div class="rg-actions"><button class="btn b" type="button" id="in-next3">Continuar</button><button class="btn rg-ghost" type="button" id="in-back3">Voltar</button></div></section>'
 '<section data-step="4" hidden><h2>Leia os termos</h2><p>Role até o final para poder concordar.</p><div class="terms" id="in-terms" tabindex="0" role="region" aria-label="Termos">' +
 "".join("<p>%s</p>" % t for t in TERMOS) +
 '</div><label class="agree lock" id="in-agree-wrap"><input type="checkbox" id="in-agree" disabled><span>Li e concordo com todos os termos escritos e ditos a partir desse termo de envio para candidato à <b id="in-agree-cargo">(Cargo)</b>.</span></label>'
 '<div class="alert i result" id="in-m4" role="status"></div><div class="rg-actions"><button class="btn b" type="button" id="in-send">Enviar candidatura</button><button class="btn rg-ghost" type="button" id="in-back4">Voltar</button></div></section>'
 '<section data-step="5" hidden><h2>Candidatura enviada!</h2><div class="alert i on">Sua inscrição para <b id="in-ok-cargo"></b>, número <b id="in-ok-num"></b>, foi enviada. Protocolo nº <b id="in-ok-prot"></b>. Guarde esse número.</div><p><a class="btn b" href="/pt-br/eleicoes-rp/">Voltar às Eleições RP</a></p></section></div>'
)
ADM_BODY = (
 '<div id="adm"><div id="adm-login"><p>Área restrita da organização das eleições.</p><form class="f" id="adm-form" style="max-width:320px"><label>Senha<input id="adm-pw" type="password" required autocomplete="current-password" inputmode="numeric"></label><button class="btn b" type="submit">Entrar</button></form><div class="alert i result" id="adm-lmsg" role="status"></div></div>'
 '<div id="adm-panel" hidden><div class="adm-bar"><strong id="adm-count"></strong><select id="adm-filter" aria-label="Filtrar por cargo"><option value="">Todos os cargos</option></select><button class="btn rg-ghost" type="button" id="adm-reload">Atualizar</button></div>'
 '<div class="table"><table><thead><tr><th>#</th><th>Enviado em</th><th>Cargo</th><th>Número</th><th>RG</th></tr></thead><tbody id="adm-body"></tbody></table></div></div>'
 '<div class="alert i result" id="adm-msg" role="status"></div>'
 '<div class="adm-modal" id="adm-modal" hidden><div><button type="button" class="btn rg-ghost" id="adm-close">Fechar</button><p id="adm-cap"></p><img id="adm-img" alt="RG anexado"></div></div></div>'
)
JRE = '<script src="/assets/js/jre.js"></script>'
write("jre/eleicoes/inscricoes/index.html", page("eleicoes-rp", "Inscrição de candidatos", "Cadastre a sua candidatura nas Eleições RP: anexe o RG-RP, escolha o cargo e o número.", None, INSC_BODY, JRE).replace('<div class="wrap layout">', '<div class="wrap layout" style="grid-template-columns:1fr">'))
write("presidencia/admin/jre/eleicoes/inscricoes/index.html", page("", "Inscrições de candidatos", "Painel da organização: todas as candidaturas registradas no banco de dados.", None, ADM_BODY, JRE).replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow">', 1).replace('<div class="wrap layout">', '<div class="wrap layout" style="grid-template-columns:1fr">').replace('class="content"', 'class="content" style="max-width:none"'))
open("package.json","w",encoding="utf-8").write(json.dumps({"name": "governo-roleplay", "private": True, "dependencies": {"@neondatabase/serverless": "^0.10.4"}}, indent=1))

# home (na raiz: "/")
shapes = '<svg class="shapes" viewBox="0 0 1024 1024" role="img" aria-label="Formas da logotipo"><path class="s s1" fill="#00a83b" d="M0 0H512A512 512 0 0 1 0 512Z"/><circle class="s s2" fill="#0c4eff" cx="768" cy="256" r="256"/><path class="s s3" fill="#ffd100" d="M256 512L512 1024H0Z"/><path class="s s4" fill="#ed1c24" d="M1024 512V1024H512A512 512 0 0 1 1024 512Z"/></svg>'
chips = "".join('<a href="%s">%s</a>' % (U(s), PAGES[s][0]) for s in ["eleicoes-rp", "cidadania", "concursos-e-vagas", "leis-e-decretos", "ouvidoria"])
quick = CARDS([("id", "", "Emitir RG-RP", "Seu documento de identidade do roleplay.", "gerar-rg-rp"), ("vote", "c-g", "Eleições RP", "Calendário e candidatos.", "eleicoes-rp"), ("brief", "c-y", "Vagas públicas", "Trabalhe no governo.", "concursos-e-vagas"), ("scale", "c-r", "Denunciar", "Abra um processo na Justiça.", "justica-rp"), ("book", "c-n", "Leis e decretos", "Consulte a legislação.", "leis-e-decretos"), ("chart", "", "Transparência", "Veja os números do governo.", "transparencia"), ("chat", "c-g", "Ouvidoria", "Fale com o governo.", "ouvidoria"), ("users", "c-y", "Partidos", "Conheça os partidos.", "partidos-politicos")])
news = '<div class="news n6">' + "".join('<article><div class="th" style="background:%s"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">%s</svg></div><div class="tx"><span class="tag">%s</span> <time>%s</time><h3>%s</h3><p>%s</p></div></article>' % (col, ICONS[ico], t, d, h, x) for t, d, h, x, ico, col in NEWS) + "</div>"
def tile(cls, shape, title, text, slug):
    return '<a class="tile %s" href="%s"><svg viewBox="0 0 100 100" aria-hidden="true">%s</svg><h3>%s</h3><p>%s</p></a>' % (cls, U(slug), shape, title, text)
poderes = '<div class="pw">' + \
  tile("t-y", '<path d="M50 5L95 95H5Z"/>', "Cidadão", "Documentos, vagas e serviços para quem vive no RP.", "servicos") + \
  tile("t-b", '<circle cx="50" cy="50" r="46"/>', "Executivo", "Presidência e ministérios que tocam o dia a dia.", "presidencia") + \
  tile("t-g", '<path d="M0 0H100A100 100 0 0 1 0 100Z"/>', "Legislativo", "Senado e Câmara, onde as leis nascem.", "congresso-nacional") + \
  tile("t-r", '<path d="M100 0V100H0A100 100 0 0 1 100 0Z"/>', "Judiciário", "Tribunais, denúncias e processos.", "justica-rp") + '</div>'
passos = '<div class="how">' + "".join('<div><span>%d</span><h3>%s</h3><p>%s</p></div>' % (n, t, x) for n, (t, x) in enumerate([("Crie seu personagem", "Entre no Discord oficial e escolha nome, história e profissão."), ("Emita seus documentos", "Peça o RG-RP e o título de eleitor RP direto pelo portal."), ("Participe da vida pública", "Vote, candidate-se, assuma uma vaga ou abra um partido.")], 1)) + '</div>'
cargos = "".join('<div><b>%s</b><span>%s</span></div>' % c for c in [("Presidente", "1 vaga"), ("Vice", "na chapa"), ("Senadores", "3 vagas"), ("Deputados", "10 vagas")])
faq = FAQ([("Este site é oficial?", "Não. É um portal fictício, feito só para roleplay."), ("Tenho que pagar por algo?", "Nada. Todos os serviços são gratuitos e simulados."), ("Como entro no RP?", "Pelo Discord oficial: crie seu personagem e abra um chamado de documentos.")])

MAIS = [("Emitir RG-RP","gerar-rg-rp"),("Consultar situação eleitoral","eleicoes-rp"),("Ver vagas públicas","concursos-e-vagas"),("Abrir uma denúncia","justica-rp"),("Consultar leis e decretos","leis-e-decretos"),("Falar com a Ouvidoria","ouvidoria")]
DEST = [("Eleições","Calendário das Eleições RP","eleicoes-rp",True),("Documentos","Emitir RG-RP sem fila","gerar-rg-rp",True),("Concursos","Inscrições abertas para vagas públicas","concursos-e-vagas",False),("Transparência","Painel de gastos do governo","transparencia",False)]
PERFIS = [("user","","Cidadão","servicos"),("vote","c-g","Eleitor","eleicoes-rp"),("flag","c-y","Candidato","partidos-politicos"),("brief","c-r","Servidor","concursos-e-vagas"),("mic","c-n","Jornalista","imprensa"),("scale","","Denunciante","justica-rp")]
CATS = [("id","Documentos e cidadania","cidadania"),("vote","Eleições RP","eleicoes-rp"),("flag","Presidência","presidencia"),("gov","Congresso Nacional","congresso-nacional"),("brief","Ministérios","ministerios"),("scale","Justiça","justica-rp"),("book","Leis e decretos","leis-e-decretos"),("eye","Transparência","transparencia"),("news","Notícias","noticias"),("doc","Diário Oficial","diario-oficial"),("users","Partidos políticos","partidos-politicos"),("chat","Ouvidoria","ouvidoria"),("mic","Imprensa","imprensa"),("help","Perguntas frequentes","perguntas-frequentes"),("access","Acessibilidade","acessibilidade"),("map","Mapa do site","mapa-do-site")]
mais = '<ol class="gv-list">' + "".join('<li><a href="%s"><i>%d</i>%s</a></li>' % (U(s), n, t) for n, (t, s) in enumerate(MAIS, 1)) + '</ol>'
dest = '<ul class="gv-list gv-dest">' + "".join('<li><a href="%s"><small>%s%s</small>%s</a></li>' % (U(s), c, ' <em>Novo</em>' if n else '', t) for c, t, s, n in DEST) + '</ul>'
perfis = '<div class="perfis">' + "".join('<a href="%s">%s<span>%s</span></a>' % (U(s), ic(i, c), t) for i, c, t, s in PERFIS) + '</div>'
cats = '<div class="cats">' + "".join('<a href="%s">%s<span>%s</span></a>' % (U(s), ICONS_SVG(i), t) for i, t, s in CATS) + '</div>'
news = '<div class="news n6">' + "".join('<article><div class="th" style="background:%s"><svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">%s</svg></div><div class="tx"><span class="tag">%s</span> <time>%s</time><h3>%s</h3><p>%s</p></div></article>' % (col, ICONS[ico], t, d, h, x) for t, d, h, x, ico, col in NEWS) + "</div>"
home = head("Início", "Portal do Governo do Roleplay (site fictício): serviços, eleições, leis e notícias.") + header("") + f'''<div class="stripe"><i></i><i></i><i></i><i></i></div><main id="main">
<section class="gv-top"><div class="wrap"><p class="gv-kicker">Serviços e informações do Roleplay</p>
<form class="bigsearch" action="/pt-br/busca/" role="search"><input name="q" placeholder="O que você procura?" aria-label="Buscar"><button aria-label="Buscar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">{ICONS["search"]}</svg></button></form></div></section>
<section class="blk gv"><div class="wrap"><h2 class="gv-t">Serviços para você</h2><div class="gv-two"><div class="gv-panel"><h3 class="gv-h"><span>Mais acessados</span></h3>{mais}</div><div class="gv-panel"><h3 class="gv-h"><span>Destaques</span></h3>{dest}</div></div></div></section>
<section class="blk gv" style="padding-top:0"><div class="wrap"><h3 class="gv-h"><span>Serviços por perfil</span></h3>{perfis}</div></section>
<section class="blk alt"><div class="wrap"><h2 class="gv-t">Navegue por categoria</h2><p class="sub c">Encontre o serviço ou a informação desejada pelas opções abaixo.</p>{cats}</div></section>
<section class="blk"><div class="wrap"><h2>Últimas notícias</h2>{news}<p style="margin-top:1.2rem"><a href="/pt-br/noticias/">Ver todas as notícias</a></p></div></section>
<section class="blk" style="padding-top:0"><div class="wrap"><div class="elec"><div><h2>Eleições RP</h2><p>Calendário, candidatos e como votar. Cada voto decide quem governa o roleplay.</p><p><a class="btn" href="/pt-br/eleicoes-rp/">Acessar eleições</a></p></div><div class="cargos">{cargos}</div></div></div></section>
<section class="blk alt"><div class="wrap faqw"><div><h2>Dúvidas rápidas</h2><a href="/pt-br/perguntas-frequentes/">Ver todas as perguntas</a></div><div>{faq}</div></div></section>
<section class="blk"><div class="wrap"><div class="band"><div><h2>Venha fazer parte</h2><p>Entre no Discord oficial e comece sua vida no Governo do Roleplay.</p></div><a class="btn" href="{DISCORD}">Entrar no Discord</a></div></div></section></main>''' + footer()
write("index.html", home)


# raiz e 404
write("pt-br/index.html", '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/"><title>%s</title><a href="/">Ir para o portal</a>' % NOME)
write("404.html", page("404", "Página não encontrada", "O endereço que você acessou não existe neste portal.", None, P('Confira o endereço ou volte para a <a href="/">página inicial</a>. Você também pode ver o <a href="/pt-br/mapa-do-site/">mapa do site</a>.')))
open("vercel.json", "w", encoding="utf-8").write(json.dumps({"buildCommand": "python3 build.py", "outputDirectory": "dist", "cleanUrls": True, "trailingSlash": True, "redirects": [{"source": "/pt-br", "destination": "/", "permanent": False}, {"source": "/pt-br/", "destination": "/", "permanent": False}]}, indent=1))
print(len(PAGES) + 3, "páginas geradas em", OUT)
