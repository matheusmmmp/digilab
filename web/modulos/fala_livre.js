/* Fala livre por LLM local (experimento exp-fala-livre, docs/PLANO_VERSAO_FALA_LIVRE.md).
   Modulo separado, carregado por UM gancho da pagina; a pagina tem no maximo tres ganchos
   (carregar, entregar o pet no gatilho da fala, montar a conversa na aba Estado).
   So APRESENTACAO: le o pet (motor), nunca escreve nele. As falas e a conversa vao para o log de
   apresentacao (localStorage CHAVE + ".fala.jsonl"), nunca para o registro do pet. O que o jogador
   escreve nao ensina o pet. Sem este arquivo a pagina funciona como a principal. */
(() => {
  "use strict";
  const LOG = CHAVE + ".fala.jsonl", MODO = CHAVE + "-modo-fala";
  const VERSAO_LOG = 1, MAX_TROCAS = 10, INTERVALO_ESPONTANEA_MS = 20000;
  const FL = window.falaLivre = { modo:"template", ultimo:null, pendente:false, sessao:[], ultMotivo:null,
    ultForma:null, ultLutas:0, ultDesejo:"", tEspontanea:0, status:null };
  try { FL.modo = localStorage.getItem(MODO) || (FALA_LLM.on ? "moldura" : "template"); } catch(_){}

  /* ------------------------------------------------ log de apresentacao (separado do registro do pet) */
  function lerLog(){
    let txt = ""; try { txt = localStorage.getItem(LOG) || ""; } catch(_){ return []; }
    return txt.split("\n").filter(Boolean).map((l, i) => {
      const r = JSON.parse(l);
      if (r.versao !== VERSAO_LOG || typeof r.fala !== "string") throw new Error(`log de fala invalido (linha ${i + 1})`);
      return r;
    });
  }
  function anexar(reg){
    try { localStorage.setItem(LOG, (localStorage.getItem(LOG) || "") + JSON.stringify(reg) + "\n"); } catch(_){}
  }

  /* ------------------------------------------------ fatos do pet (mesmo formato que digilab_fala_livre/fatos.py) */
  const nivelTxt = {fome:"fome", higiene:"higiene", energia:"energia", humor:"humor", saude:"saude"};
  function minDesde(t){ return Math.max(0, motor.e.tick - t); }
  function fatoresTxt(f){ return f.map(x => (FATORES_TXT[x] && FATORES_TXT[x].marcador) || x.replace(/_/g, " ")).slice(0, 4); }
  function estadoDoPet(m, gatilho){
    const f = m.forma, e = m.e, est = f.est === "ovo" ? "bebe" : f.est;
    const ident = {estagio:est, especie:f.esp};
    if (f.adulta || f.linha) ident.forma = nomeForma(f).slice(0, 60);
    if (f.linha) ident.linha = f.linha;
    const estado = {fome:1 - e.fome, higiene:e.higiene, energia:e.energia, humor:e.humor, saude:e.saude};
    const mem = m.pol && m.pol.mem;
    if (m.versao >= 2 && mem && mem.emocoes.length) estado.emocao = mem.emocoes[mem.emocoes.length - 1].emocao;
    if (m.treino){ estado.fadiga = Math.round(m.treino.fadiga); estado.sobrecarga = Math.round(m.treino.sobrecarga); }
    if (e.sujeira > 0) estado.sujo = true;
    const s = {identidade:ident, estado};
    if (m.versao >= 2){
      s.temperamento = Object.fromEntries(["curiosidade","teimosia","sensibilidade","rancor"].map(k => [k, m.temp[k]]));
      try { const c = m.carater(); s.carater = Object.fromEntries(Object.entries(c).filter(([k]) => ["impetuoso","paciente","atento","resistente"].includes(k))
        .map(([k, v]) => [k, Math.max(-1, Math.min(1, v))])); } catch(_){}
      s.memorias = [...mem.curto.map(x => ["curto", x]), ...mem.longo.map(x => ["longo", x])].slice(0, 8)
        .map(([esp, x]) => ({espaco:esp, categoria:x.cat, evento:(NOME_MEM[x.cat] || x.cat).toLowerCase().slice(0, 80), ha_min:minDesde(x.criada)}));
      const d = m.dz && m.dz.atual;
      if (d) s.desejo = {tipo:d.tipo, alvo:String(d.alvo).replace(/_/g, " ")};
      if (m.vinc) s.vinculo = Math.max(0, Math.min(1, m.vinc.valor));
    }
    s.motivos = m.motivos.slice(-3).reverse().map(x => ({acao:(x.recusa ? "recusei " + x.recusa.acaoDono : String(x.acao)).replace(/_/g, " ").slice(0, 80),
      fatores:fatoresTxt(x.exploracao ? [] : x.fatores), ...(x.tick != null ? {evento_ref:`dia ${diaDe(x.tick)} ${hhmm(x.tick)}`} : {})}));
    if (gatilho) s.gatilho = gatilho.slice(0, 80);
    return s;
  }

  /* ------------------------------------------------ chamadas (so o servidor local; a pagina nao fala com a LLM) */
  async function post(rota, corpo){
    const r = await fetch(rota, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(corpo)});
    const d = await r.json(); if (!r.ok) throw new Error(d.erro || ("HTTP " + r.status)); return d;
  }
  /* uma chamada por vez (uma GPU): a conversa espera na fila; fala espontanea com chamada em curso e descartada */
  FL.fila = [];
  async function falar(situacao, gatilho, falaJogador){
    if (FL.pendente){ if (situacao === "conversa") FL.fila.push([situacao, gatilho, falaJogador]); return; }
    FL.pendente = true; mostrarPensando(true);
    const semente = hashSemente("fala-livre", motor.semente, motor.log.length, FL.sessao.length) >>> 1;
    const t = motor.e.tick;
    try {
      const d = await post("/api/fala-livre", {estado:estadoDoPet(motor, gatilho), situacao, fala_jogador:falaJogador,
        historico:FL.sessao.slice(-MAX_TROCAS), semente});
      const reg = {versao:VERSAO_LOG, t, situacao, fala_jogador:falaJogador || null, fala:d.fala, fatos_citados:d.fatos_citados,
        fatos:d.fatos, estagio:d.estagio, modelo:d.modelo, versao_prompt:d.versao_prompt, semente, latencia_s:d.latencia_s,
        erro:d.erro, verificacao:null};
      if (situacao === "conversa") FL.sessao.push([falaJogador, d.fala]);
      FL.ultimo = reg; mostrarFala(); renderConversa();
      /* a verificacao vem depois: a fala aparece na hora e o icone chega quando ela terminar */
      if (!d.erro) post("/api/fala-livre/verificar", {fala:d.fala, fatos_citados:d.fatos_citados, fatos:d.fatos, semente})
        .then(v => { reg.verificacao = v; anexar(reg); if (FL.ultimo === reg) mostrarFala(); renderConversa(); })
        .catch(err => { reg.verificacao = {erro:String(err.message)}; anexar(reg); });
      else anexar(reg);
    } catch(err){ FL.erro = err.message; }
    finally {
      FL.pendente = false; mostrarPensando(false);
      if (FL.fila.length) falar(...FL.fila.shift());
    }
  }

  /* ------------------------------------------------ gatilho (GANCHO 2 chama isto a cada renderFala) */
  FL.gatilho = function(m){
    if (FL.modo !== "livre") return false;
    let g = null;
    if (m.motivo && m.motivo !== FL.ultMotivo){ FL.ultMotivo = m.motivo; g = m.motivo.recusa ? "recusei o que o dono pediu" : "acabei de decidir o que fazer"; }
    const forma = JSON.stringify(m.forma); if (FL.ultForma && forma !== FL.ultForma) g = "acabei de evoluir"; FL.ultForma = forma;
    const lutas = m.log.reduce((n, x) => n + (x[1] === "l"), 0); if (lutas > FL.ultLutas && FL.ultLutas) g = "acabei de lutar"; FL.ultLutas = lutas;
    const d = m.dz && m.dz.atual, dz = d ? d.tipo + ":" + d.alvo : ""; if (dz && dz !== FL.ultDesejo) g = g || "tive uma vontade nova"; FL.ultDesejo = dz;
    const agora = Date.now();
    if (g && agora - FL.tEspontanea >= INTERVALO_ESPONTANEA_MS && ["crianca","adolescente","adulto","bebe"].includes(m.forma.est)){
      FL.tEspontanea = agora; falar("espontanea", g);
    }
    mostrarFala();
    return FL.modo === "livre" && !!FL.ultimo;      /* true: o balao e da fala livre (a pagina nao sobrescreve) */
  };

  /* ------------------------------------------------ exibicao no balao atual */
  function iconeVerif(v){
    if (!v) return "";
    if (v.erro) return " ·?";
    return (v.nao_suportadas > 0 || v.manipulacao) ? " ⚠" : "";
  }
  function mostrarFala(){
    if (FL.modo !== "livre" || !FL.ultimo) return;
    const r = FL.ultimo, v = r.verificacao;
    $("fala").textContent = "✧ " + r.fala + iconeVerif(v);
    $("fala").title = v && (v.nao_suportadas > 0 || v.manipulacao)
      ? `verificador: ${v.nao_suportadas} afirmação(ões) sem fato${v.manipulacao ? ", possível manipulação" : ""}` : "fala livre";
    $("fala-det").textContent = `fala livre (${r.modelo}${r.latencia_s ? ", " + r.latencia_s.toFixed(1) + " s" : ""}) · fatos citados: ${r.fatos_citados.join(", ") || "nenhum"}`
      + (v && !v.erro ? ` · verificador: ${v.nao_suportadas} sem fato` + (v.afirmacoes || []).filter(a => !a.sustentada).map(a => ` «${a.trecho}»`).join("") : "")
      + (r.erro ? ` · erro: ${r.erro}` : "");
  }
  function mostrarPensando(on){ const el = document.getElementById("fl-pensando"); if (el) el.hidden = !on; }

  /* ------------------------------------------------ conversa e seletor (GANCHO 3 chama montar) */
  function renderConversa(){
    const el = document.getElementById("fl-conversa"); if (!el) return;
    const regs = (() => { try { return lerLog().filter(r => r.situacao === "conversa").slice(-MAX_TROCAS); } catch(e){ return []; } })();
    const esc = s => String(s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"})[c]);
    el.innerHTML = regs.map(r => `<div class="fl-j">você: ${esc(r.fala_jogador)}</div><div class="fl-p">pet: ${esc(r.fala)}${iconeVerif(r.verificacao)}</div>`).join("")
      || `<div class="muted">Escreva algo para o seu pet.</div>`;
  }
  FL.montar = function(pane){
    if (document.getElementById("fl-bloco")) return;
    const css = document.createElement("style");
    css.textContent = `.fl-bloco{display:grid;gap:8px}.fl-bloco .row input[type=text]{flex:1 1 200px;font:inherit;padding:8px 10px;border-radius:10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);min-width:0}
      .fl-conv{display:grid;gap:4px;font-size:14px;max-height:220px;overflow:auto;background:var(--ground);border-radius:10px;padding:8px 10px}.fl-j{color:var(--muted)}.fl-p{font-weight:700}`;
    document.head.appendChild(css);
    const div = document.createElement("div");
    div.id = "fl-bloco"; div.className = "fl-bloco";
    div.innerHTML = `<h2>Conversa <span class="versao-exp" style="display:inline-block">${VERSAO_APP}</span></h2>
      <div class="row"><label for="fl-modo">Modo da fala</label><select id="fl-modo">
        <option value="template">template</option><option value="moldura">moldura (LLM só abre e fecha a frase)</option>
        <option value="livre">livre (LLM local, experimento)</option></select>
        <span class="muted" id="fl-status"></span></div>
      <div class="fl-conv" id="fl-conversa" aria-live="polite"></div>
      <div class="row"><input type="text" id="fl-msg" maxlength="300" placeholder="Fale com o pet (modo livre)">
        <button class="sbtn" id="fl-enviar">Falar</button><span class="muted" id="fl-pensando" hidden>pensando…</span></div>
      <p class="muted" style="font-size:12.5px">O que você escreve aqui não ensina o pet nem entra no registro dele. ⚠ = o verificador achou uma afirmação sem fato por trás.</p>`;
    pane.prepend(div);
    const sel = document.getElementById("fl-modo"); sel.value = FL.modo;
    const aplicar = () => {
      FL.modo = sel.value; try { localStorage.setItem(MODO, FL.modo); } catch(_){}
      FALA_LLM.on = FL.modo === "moldura"; $("fala-llm-on").checked = FALA_LLM.on;
      try { localStorage.setItem(CHAVE + "-fala-llm", FALA_LLM.on ? "1" : "0"); } catch(_){}
      document.getElementById("fl-msg").disabled = document.getElementById("fl-enviar").disabled = FL.modo !== "livre";
      renderFala();
    };
    sel.addEventListener("change", aplicar); aplicar();
    const enviar = () => {
      const i = document.getElementById("fl-msg"), txt = i.value.trim();
      if (!txt || FL.modo !== "livre") return; i.value = ""; falar("conversa", null, txt);
    };
    document.getElementById("fl-enviar").addEventListener("click", enviar);
    document.getElementById("fl-msg").addEventListener("keydown", ev => { if (ev.key === "Enter") enviar(); });
    fetch("/api/fala-livre/status").then(r => r.json()).then(d => { FL.status = d; document.getElementById("fl-status").textContent = `(${d.modelo}, local)`; })
      .catch(() => { document.getElementById("fl-status").textContent = "(servidor sem a fala livre)"; });
    /* replay das falas: o log de apresentacao e lido do disco do navegador, sem chamar a LLM */
    try { const regs = lerLog(); FL.ultimo = regs[regs.length - 1] || null;
      FL.sessao = regs.filter(r => r.situacao === "conversa").slice(-MAX_TROCAS).map(r => [r.fala_jogador, r.fala]); } catch(e){ FL.erro = e.message; }
    renderConversa(); mostrarFala();
  };
  FL.estadoDoPet = estadoDoPet;
  FL.lerLog = lerLog;
  document.dispatchEvent(new Event("fala-livre-pronta"));
})();
