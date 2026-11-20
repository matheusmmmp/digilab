/* O save na nuvem (CN3): as rotas /nuvem com a sessão e o CSRF da conta, e o e2e dos quatro casos do portão F3 (docs/ROADMAP_V3_CONTA.md):
   o mesmo pet em dois aparelhos, jogar offline e voltar sem perder nada, a divergência com a escolha, e restaurar uma cópia.
   Os dois aparelhos são duas instâncias do cliente do jogo (web/app/src/nuvem/cliente.ts, importado de novo depois do vi.resetModules),
   cada uma com o seu armazenamento e o seu navegador, contra o servidor de verdade no processo. Os registros são da vida do gabarito
   (test/gabaritos/vida_101.json): um começo dela, e o resto feito pelo motor. Nenhum evento pode se perder: cada caso confere o registro. */
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Motor, type EventoRegistro } from "../../web/app/motor/index.ts";
import { CHAVE } from "../../web/app/src/chave.ts";
import { PROTOCOLO_NUVEM, VEZ_EXPIRA_MS, idDoSave, pontaFirme, type SaveNuvem } from "../../web/app/src/nuvem/protocolo.ts";
import { hashRegistro } from "../src/envio/conferir.ts";
import { contar, criarConta, montar, Navegador, type Montado } from "./navegador.ts";

type Cliente = typeof import("../../web/app/src/nuvem/cliente.ts");
const VIDA: SaveNuvem = JSON.parse(readFileSync(new URL("./gabaritos/vida_101.json", import.meta.url), "utf-8"));
const UA_CEL = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Mobile Safari/537.36";
const DIA = 86_400_000;

/** o save de um começo da vida do gabarito */
const comeco = (n: number): SaveNuvem => ({ semente: VIDA.semente, log: VIDA.log.slice(0, n), versao: VIDA.versao });
/** o save depois de mais cuidados pelo motor (eventos válidos, que o servidor refaz) */
function jogar(s: SaveNuvem, acoes: readonly string[]): SaveNuvem {
  const m = Motor.reproduzir(s.semente, s.log as EventoRegistro[], s.versao);
  for (const a of acoes) { m.avancar(7); m.observar(a as never); }
  return { semente: s.semente, log: m.log as unknown as unknown[][], versao: s.versao };
}
const caminho = (url: string): string => { const u = new URL(url); return u.pathname + u.search; };

/** entra numa conta que já existe pelo provedor falso (o segundo aparelho) */
async function entrar(nav: Navegador, usuario = "ana", ua?: string): Promise<void> {
  const h = ua ? { "User-Agent": ua } : undefined;
  const ida = await nav.pedir("/auth/falso?volta=%23%2Fconfig%2Fconta", { headers: h });
  const a = new URL(ida.headers.get("location")!);
  const form = new URLSearchParams({ state: a.searchParams.get("state")!, code_challenge: a.searchParams.get("code_challenge")!,
    redirect_uri: a.searchParams.get("redirect_uri")!, usuario });
  const dado = await nav.pedir("/auth/falso/autorizar", { method: "POST", body: form.toString(), headers: { "Content-Type": "application/x-www-form-urlencoded", ...h } });
  const cb = await nav.pedir(caminho(dado.headers.get("location")!), { headers: h });
  expect(new URL(cb.headers.get("location")!).searchParams.get("conta")).toBe("entrou");
}

/** um aparelho: o navegador (os cookies), o armazenamento do jogo, a rede (que cai e volta) e uma instância própria do cliente */
interface Aparelho {
  nav: Navegador; dados: Map<string, string>; c: Cliente; travado: boolean; recargas: number; rede: boolean;
  save: () => SaveNuvem; gravarSave: (s: SaveNuvem) => void;
}
async function aparelho(M: Montado, nav: Navegador, ua?: string): Promise<Aparelho> {
  vi.resetModules();
  const c = await import("../../web/app/src/nuvem/cliente.ts") as Cliente;
  const dados = new Map<string, string>();
  const ap: Aparelho = {
    nav, dados, c, travado: false, recargas: 0, rede: true,
    save: () => JSON.parse(dados.get(CHAVE)!) as SaveNuvem,
    gravarSave: s => { dados.set(CHAVE, c.textoDoSave(s)); },
  };
  c.conhecerVersoes([VIDA.versao]);
  c.ligarNuvem({
    api: "http://127.0.0.1:8766",
    buscar: async (url, init) => {
      if (!ap.rede) throw new TypeError("Failed to fetch");
      const headers = { ...(init?.headers as Record<string, string> | undefined), ...(ua ? { "User-Agent": ua } : {}) };
      return nav.pedir(caminho(url), { method: init?.method, body: init?.body as string | undefined, headers });
    },
    armaz: { getItem: k => dados.get(k) ?? null, setItem: (k, v) => { dados.set(k, v); }, removeItem: k => { dados.delete(k); } },
    chaves: () => [...dados.keys()],
    agora: () => M.relogio.t,
    aoMudarLocal: () => { ap.recargas++; },
    travar: sim => { ap.travado = sim; },
  });
  return ap;
}

/** o pet da nuvem, lido do banco */
const daNuvem = (M: Montado): { log: unknown[][]; eventos: number; hash: string; extras: Record<string, string> } => {
  const l = M.banco.prepare("SELECT log, eventos, hash, extras FROM nuvem_pets").get() as { log: string; eventos: number; hash: string; extras: string };
  return { log: JSON.parse(l.log), eventos: l.eventos, hash: l.hash, extras: JSON.parse(l.extras) };
};

let M: Montado, navA: Navegador, csrf: string;
beforeEach(async () => {
  M = montar();
  navA = new Navegador(M.app);
  csrf = await criarConta(navA);
});

/* ---------------------------------------------------------------------------------------------------------------- as rotas */
describe("as rotas /nuvem", () => {
  const levar = (corpo: unknown, token: string | undefined = csrf) => navA.json("POST", "/nuvem/levar", corpo, token);
  const pacote = (save: SaveNuvem = comeco(300), extras: Record<string, string> = {}) => ({ save, extras });

  it("sem sessão: 401; sem o CSRF: 403; o estado da conta sem pet é sem_pet", async () => {
    const outro = new Navegador(M.app);
    expect((await outro.pedir("/nuvem")).status).toBe(401);
    expect((await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote() }, "")).status).toBe(403);
    expect(await (await navA.pedir("/nuvem")).json()).toMatchObject({ situacao: "sem_pet", base: null });
  });
  it("levar grava o pacote, a posição (o hash do registro), a cópia diária e a vez deste aparelho", async () => {
    const s = comeco(300), x = { [CHAVE + "-tamer"]: '{"versao":10,"log":[]}' };
    const r = await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote(s, x) });
    expect(r.status).toBe(201);
    const d = await r.json() as any;
    const firme = pontaFirme(s.log);   // o "t" do fim ainda cresce: a base para antes dele
    expect(firme).toBe(299);
    expect(d).toMatchObject({ situacao: "ok", base: { id: idDoSave(s), eventos: firme, hash: hashRegistro(s.log.slice(0, firme)) }, vez: { minha: true } });
    expect(daNuvem(M).extras).toEqual(x);
    expect(contar(M.banco, "nuvem_copias")).toBe(1);
    /* a conta já tem pet: levar de novo pede a escolha */
    const de_novo = await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote() });
    expect(de_novo.status).toBe(409);
    expect(await de_novo.json()).toMatchObject({ ja_tem: true });
  });
  it("recusa o registro que não reproduz (422), a chave que não sobe (400), o protocolo e a versão de outro jogo (426)", async () => {
    const quebrado = comeco(300);
    quebrado.log = [...quebrado.log, [quebrado.log[299]![0], "acao_que_nao_existe"]];
    expect((await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote(quebrado) })).status).toBe(422);
    expect((await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote(comeco(300), { [CHAVE + "-fala-llm"]: "1" }) })).status).toBe(400);
    expect((await levar({ protocolo: 99, escolha: "levar", pacote: pacote() })).status).toBe(426);
    expect((await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote({ ...comeco(300), versao: 16 }) })).status).toBe(426);
    expect(contar(M.banco, "nuvem_pets")).toBe(0);
  });
  it("a vez: o outro aparelho fica com 'outro'; 'jogar aqui' toma a vez; ela expira sozinha em 10 min", async () => {
    await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote() });
    const navB = new Navegador(M.app);
    await entrar(navB, "ana", UA_CEL);
    const csrfB = (await (await navB.pedir("/conta", { headers: { "User-Agent": UA_CEL } })).json() as { csrf: string }).csrf;
    const vezB = (corpo: unknown) => navB.json("POST", "/nuvem/vez", corpo, csrfB, { "User-Agent": UA_CEL });
    const r = await vezB({ protocolo: PROTOCOLO_NUVEM });
    expect(r.status).toBe(409);
    expect(await r.json()).toMatchObject({ situacao: "outro", vez: { minha: false, aparelho: "Chrome no Windows" } });
    expect((await vezB({ protocolo: PROTOCOLO_NUVEM, jogar_aqui: true })).status).toBe(200);
    const a = await navA.json("POST", "/nuvem/vez", { protocolo: PROTOCOLO_NUVEM }, csrf);
    expect(await a.json()).toMatchObject({ situacao: "outro", vez: { aparelho: "Chrome no Android" } });
    M.relogio.t += VEZ_EXPIRA_MS + 1;
    expect((await navA.json("POST", "/nuvem/vez", { protocolo: PROTOCOLO_NUVEM }, csrf)).status).toBe(200);
  });
  it("as cópias passam dos 30 dias e saem; apagar a conta leva tudo da nuvem", async () => {
    await levar({ protocolo: PROTOCOLO_NUVEM, escolha: "levar", pacote: pacote() });
    expect(contar(M.banco, "nuvem_copias")).toBe(1);
    M.relogio.t += 30 * DIA;
    await entrar(navA);          // a sessão também dura 30 dias
    csrf = (await (await navA.pedir("/conta")).json() as { csrf: string }).csrf;
    expect(await (await navA.pedir("/nuvem/copias")).json()).toEqual([]);
    const dados = await (await navA.pedir("/conta/dados")).json() as any;
    expect(dados.nuvem.pet).toMatchObject({ eventos: 300 });
    expect(JSON.stringify(dados.nuvem)).not.toContain('"log"');
    expect((await navA.json("DELETE", "/conta", { confirmar: "apagar" }, csrf)).status).toBe(200);
    for (const t of ["nuvem_pets", "nuvem_copias", "nuvem_historias", "nuvem_divergencias"]) expect(contar(M.banco, t)).toBe(0);
  });
});

/* ---------------------------------------------------------------------------------------------------------------- o e2e dos quatro casos */
describe("o e2e dos quatro casos (portão F3)", () => {
  /** o PC leva o pet; o celular entra na mesma conta e escolhe "os da nuvem" */
  async function doisAparelhos(): Promise<[Aparelho, Aparelho]> {
    const A = await aparelho(M, navA);
    A.gravarSave(comeco(300));
    A.dados.set(CHAVE + "-tamer", '{"versao":10,"log":[]}');
    await A.c.abrirNuvem();
    expect(A.c.NV.estado).toBe("sem_pet");
    await A.c.levarParaConta("levar");
    expect(A.c.NV.estado).toBe("ok");
    expect(A.travado).toBe(false);
    const navB = new Navegador(M.app);
    await entrar(navB, "ana", UA_CEL);
    const B = await aparelho(M, navB, UA_CEL);
    await B.c.abrirNuvem();
    expect(B.c.NV.estado).toBe("ja_tem");
    B.gravarSave(comeco(10));         // o celular tinha um pet de exemplo
    await B.c.levarParaConta("nuvem");
    return [A, B];
  }

  it("1. o mesmo pet abre no PC e no celular; o celular fica só para ver até 'Jogar aqui'; o que um joga chega ao outro", async () => {
    const [A, B] = await doisAparelhos();
    expect(B.save()).toEqual(A.save());
    expect(B.dados.get(CHAVE + "-tamer")).toBe('{"versao":10,"log":[]}');
    expect(B.c.NV.estado).toBe("outro");
    expect(B.travado).toBe(true);
    /* o PC joga e sincroniza; o celular, só vendo, recebe os eventos */
    A.gravarSave(jogar(A.save(), ["alimentar", "brincar"]));
    await A.c.sincronizar();
    expect(daNuvem(M).log).toEqual(A.save().log);
    await B.c.sincronizar();
    expect(B.save()).toEqual(A.save());
    expect(B.recargas).toBeGreaterThan(0);
    /* "Jogar aqui": o celular toma a vez e destrava; o PC fica só para ver na próxima sincronização */
    await B.c.jogarAqui();
    expect(B.c.NV.estado).toBe("ok");
    expect(B.travado).toBe(false);
    /* o PC ainda anda o tempo até saber (só "t", nenhuma ação): não vira outra história, e ele recebe o da nuvem */
    const m = Motor.reproduzir(A.save().semente, A.save().log as EventoRegistro[], A.save().versao);
    m.avancar(9); m.avancar(3);
    A.gravarSave({ ...A.save(), log: m.log as unknown as unknown[][] });
    await A.c.sincronizar();
    expect(contar(M.banco, "nuvem_divergencias")).toBe(0);
    expect(A.save()).toEqual(B.save());
    expect(A.c.NV.estado).toBe("outro");
    expect(A.travado).toBe(true);
    B.gravarSave(jogar(B.save(), ["limpar"]));
    await B.c.sincronizar();
    await A.c.sincronizar();
    expect(A.save()).toEqual(B.save());
    expect(daNuvem(M).hash).toBe(hashRegistro(B.save().log));
  });

  it("o tempo andando (o 't' do fim cresce no lugar) não é divergência, e o aparelho atrás não apaga os minutos", async () => {
    const [A, B] = await doisAparelhos();
    for (let i = 0; i < 3; i++) {
      const m = Motor.reproduzir(A.save().semente, A.save().log as EventoRegistro[], A.save().versao);
      m.avancar(5);
      A.gravarSave({ ...A.save(), log: m.log as unknown as unknown[][] });
      await A.c.sincronizar();
      expect(A.c.NV.estado).toBe("ok");
    }
    expect(daNuvem(M).log).toEqual(A.save().log);
    await B.c.sincronizar();
    expect(B.save()).toEqual(A.save());
    expect(contar(M.banco, "nuvem_divergencias")).toBe(0);
  });

  it("2. jogar offline no aparelho com a vez e voltar não perde nada", async () => {
    const [A] = await doisAparelhos();
    A.rede = false;
    A.gravarSave(jogar(A.save(), ["alimentar", "brincar", "limpar"]));
    await A.c.sincronizar();
    expect(A.c.NV.estado).toBe("offline");
    expect(A.travado).toBe(false);        // offline o jogo segue (5.1)
    A.gravarSave(jogar(A.save(), ["acariciar"]));
    M.relogio.t += 2 * VEZ_EXPIRA_MS;      // a vez expirou, e ninguém a tomou
    A.rede = true;
    await A.c.sincronizar();
    expect(A.c.NV.estado).toBe("ok");
    expect(daNuvem(M).log).toEqual(A.save().log);
    expect(contar(M.banco, "nuvem_divergencias")).toBe(0);
  });

  it("3. a divergência mostra a escolha; o pet fica só para ver nos dois até escolher; a outra história vai para Gerações; nenhum evento se perde", async () => {
    const [A, B] = await doisAparelhos();
    /* o PC joga sem rede; a vez dele expira; o celular toma a vez e joga */
    A.rede = false;
    A.gravarSave(jogar(A.save(), ["alimentar", "brincar", "limpar"]));
    await A.c.sincronizar();
    const historiaA = A.save();
    M.relogio.t += VEZ_EXPIRA_MS + 1;
    await B.c.sincronizar();
    expect(B.c.NV.estado).toBe("ok");            // a vez ficou livre: o celular destrava
    B.gravarSave(jogar(B.save(), ["acariciar"]));
    await B.c.sincronizar();
    const historiaB = B.save();
    expect(daNuvem(M).log).toEqual(historiaB.log);
    /* o PC volta: duas histórias */
    A.rede = true;
    await A.c.sincronizar();
    expect(A.c.NV.estado).toBe("divergiu");
    expect(A.travado).toBe(true);
    expect(A.c.NV.divergencia).toMatchObject({ nuvem: { aparelho: "Chrome no Android", eventos_novos: 1 }, outra: { aparelho: "Chrome no Windows", eventos_novos: 5 } });
    await B.c.sincronizar();
    expect(B.c.NV.estado).toBe("divergiu");
    expect(B.travado).toBe(true);
    /* "Decidir depois": nada muda até a escolha; o PC tenta de novo e não cria outra divergência */
    await A.c.sincronizar();
    expect(contar(M.banco, "nuvem_divergencias")).toBe(1);
    expect(M.banco.prepare("SELECT motivo FROM nuvem_copias ORDER BY feita_em").all().map((r: any) => r.motivo)).toEqual(["diaria", "nao_escolhido"]);
    /* o celular escolhe a história do PC */
    await B.c.escolherHistoria("outra");
    expect(daNuvem(M).log).toEqual(historiaA.log);
    expect(B.save()).toEqual(historiaA);
    await A.c.sincronizar();
    expect(A.save()).toEqual(historiaA);
    expect(A.c.NV.estado).not.toBe("divergiu");
    /* a do celular foi para Gerações (só para ver) e para as cópias: inteira */
    const hs = await B.c.listarHistorias();
    expect(hs).toHaveLength(1);
    expect((await B.c.saveDaHistoria(hs[0]!.id)).log).toEqual(historiaB.log);
    expect((await B.c.listarCopias()).map(c => c.motivo)).toContain("historia");
  });

  it("3b. o que um aparelho faz com a escolha pendente vira uma cópia", async () => {
    const [A, B] = await doisAparelhos();
    A.rede = false;
    A.gravarSave(jogar(A.save(), ["alimentar"]));
    await A.c.sincronizar();
    M.relogio.t += VEZ_EXPIRA_MS + 1;
    await B.c.sincronizar();
    B.gravarSave(jogar(B.save(), ["brincar"]));
    await B.c.sincronizar();
    A.rede = true;
    await A.c.sincronizar();
    expect(A.c.NV.estado).toBe("divergiu");
    /* o celular tinha eventos que não subiram antes de saber da divergência */
    B.gravarSave(jogar(B.save(), ["limpar"]));
    await B.c.sincronizar();
    const motivos = (await B.c.listarCopias()).map(c => c.motivo);
    expect(motivos).toContain("durante_divergencia");
  });

  it("4. restaurar uma cópia: a de agora vira uma cópia, e o outro aparelho recebe a restaurada", async () => {
    const [A, B] = await doisAparelhos();
    const diaria = A.save();
    M.relogio.t += DIA;
    A.gravarSave(jogar(A.save(), ["alimentar", "brincar"]));
    await A.c.sincronizar();
    const agora = A.save();
    const copias = await A.c.listarCopias();
    expect(copias.filter(c => c.motivo === "diaria")).toHaveLength(2);
    const ontem = copias.find(c => c.motivo === "diaria" && c.eventos === diaria.log.length)!;
    await A.c.restaurarCopia(ontem.id);
    expect(A.save()).toEqual(diaria);
    expect(daNuvem(M).log).toEqual(diaria.log);
    const depois = await A.c.listarCopias();
    expect(depois.find(c => c.motivo === "antes_de_restaurar")?.eventos).toBe(agora.log.length);
    await B.c.sincronizar();
    expect(B.save()).toEqual(diaria);
  });

  it("trocar o pet ativo manda o save inteiro, e o de antes vai para as cópias", async () => {
    const [A] = await doisAparelhos();
    const antes = A.save();
    const outro: SaveNuvem = { semente: 202, log: [], versao: VIDA.versao };
    A.gravarSave(outro);
    await A.c.sincronizar();
    expect(A.c.NV.estado).toBe("ok");
    expect(daNuvem(M).eventos).toBe(0);
    expect((await A.c.listarCopias()).find(c => c.motivo === "troca")?.eventos).toBe(antes.log.length);
  });

  it("'Guardar os dois': o pet deste aparelho segue ativo e o da nuvem entra nos guardados", async () => {
    const A = await aparelho(M, navA);
    A.gravarSave(comeco(300));
    await A.c.abrirNuvem();
    await A.c.levarParaConta("levar");
    const navB = new Navegador(M.app);
    await entrar(navB, "ana", UA_CEL);
    const B = await aparelho(M, navB, UA_CEL);
    B.gravarSave(comeco(40));
    await B.c.abrirNuvem();
    await B.c.levarParaConta("os_dois");
    expect(B.c.NV.estado).toBe("ok");
    expect(daNuvem(M).eventos).toBe(40);
    const g = JSON.parse(B.dados.get(CHAVE + "-guardados")!) as SaveNuvem[];
    expect(g.map(x => x.log.length)).toEqual([300]);
    expect(JSON.parse(daNuvem(M).extras[CHAVE + "-guardados"]!)).toEqual(g);
    expect((await B.c.listarCopias()).map(c => c.motivo)).toContain("nao_escolhido");
  });

  it("a sessão que acabou pede 'Entre de novo'; o servidor fora do ar dá 'Offline' sem travar", async () => {
    const A = await aparelho(M, navA);
    A.gravarSave(comeco(300));
    A.rede = false;
    await A.c.abrirNuvem();
    expect(A.c.NV.estado).toBe("offline");
    expect(A.travado).toBe(false);
    A.rede = true;
    /* sem sessão, o aparelho que nunca sincronizou é o "salvo" de sempre; o que já sincronizava pede "Entre de novo" */
    const sem = new Navegador(M.app), B = await aparelho(M, sem);
    B.gravarSave(comeco(20));
    await B.c.abrirNuvem();
    expect(B.c.NV.estado).toBe("sem_conta");
    expect(B.travado).toBe(false);
    await A.c.abrirNuvem();
    await A.c.levarParaConta("levar");
    navA.cookies.clear();
    await A.c.abrirNuvem();
    expect(A.c.NV.estado).toBe("sessao");
  });
});
