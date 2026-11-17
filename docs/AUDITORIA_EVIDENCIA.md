# AUDITORIA DA EVIDÊNCIA — fase A0 (2026-11-16, Claude Code, Opus 5.5)

**O que é:** o inventário do que já rodou, do que está versionado e do que falta para reproduzir, para os oito experimentos com resultado
registrado (C1, C2, C3, C4, AN4, GVN2, PET_VIVO, COOP A1). **Nenhuma vida nova, nenhum número novo:** todo número daqui é copiado de um
artefato que já existia, e todo sha256 e commit sai do [`auditoria.json`](../artifacts_v3_auditoria_evidencia/auditoria.json).

**O snapshot auditado:** `f8fa9ad2647ad9d4164dced1aeeec8d6697de611` (a `main` de 2026-11-13, merge do #934). Os links permanentes abaixo
apontam para esse commit (`blob/f8fa9ad…`) ou para o commit do plano (`blob/<commit do plano>`).

**Como refazer:** `python tools/auditar_evidencia.py f8fa9ad2647ad9d4164dced1aeeec8d6697de611 <saida.json>`. A ferramenta só lê o git (nunca
o disco de trabalho) e falha alto se um caminho esperado faltar. Duas execuções seguidas deram o mesmo arquivo, sha256
`c9a85f5f39ea8ae0a062662b314366cbc3af31699ece3fb5810dceba31ecf6b3` (Python 3.13.0, git 2.45.1.windows.1). O teste é o
`tests/test_auditar_evidencia.py`.

**O que a ferramenta confere, por run:**
1. o meta (ou o manifesto): o SHA do código, a árvore limpa, o Python, o Node, se o comando está gravado, o início;
2. o plano: o commit **mais antigo** em que o blob do plano tem o sha256 gravado no meta (com LF ou CRLF), e se esse commit é ancestral do
   código da run;
3. os artefatos versionados: o sha256 do blob (e o do conteúdo descomprimido, num `.gz`), contra o gravado no meta;
4. o commit que pôs cada artefato no git.

Ela **não** refaz nenhuma run e **não** confere que o número do documento sai do artefato (isso é a A3 e a A4).

## 1. A tabela

Legenda do status: **positivo** (o primário passa pela regra escrita antes), **negativo** (falha ou "≈ 0"), **indeterminado** (IC que
contém 0 e não fecha "≈ 0"), **descritivo** (sem confirmação pela regra; gerador de hipótese). "Plano → código" é o commit do plano com o
sha256 do meta e se ele é ancestral do código da run (o horário é o do commit; o início é o do meta).

### 1.1 C1, o longe regular

| campo | valor |
|---|---|
| pergunta | M3\* − M2, a taxa de fechamento por episódio de fome, nas 4 células do `longe_fixo` (o primário); o mesmo no `longe` sorteado |
| plano | [`PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`](https://github.com/matheusmmmp/digilab/blob/7683c0e1f83a9526421208b4a23d90cd476148ff/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md), adendo 6, no commit `7683c0e1f83a9526421208b4a23d90cd476148ff` (2026-10-31 13:10) |
| plano → código | o commit do plano **é** o código da run (`git_head`); a run começou às 14:18:10; árvore limpa |
| células e N | 8 células (4 donos × `longe`, `longe_fixo`), braços M0, M2, M3; 150 unidades nas bases 71101–71505 (5 bases); 3 600 vidas |
| comando | não gravado no meta; o do plano (adendo 6): `python experiments/run_v2_longe_regular.py --config experiments/configs/v2_longe_regular/longe_regular.json --saida artifacts_v2_digibrain_prototipo/longe_regular/run --processos 4`; o meta grava o `config_arquivo` e o `config_sha256` |
| ambiente | Python 3.13.0; 4 processos; Node não se aplica |
| artefatos | `longe_regular/run/resultado.json` `b18727455922c2fb3047694e1228620ab136014796a68c008c20cac014a21209`; `medidas.json` `5a4fb207eaa11750ba40ffc80da1879febd822a5305545356fb091b664a4722d`; `vidas.tar.gz` `a1fb0010435d450935aa69b800a0c5fae5202671b1d55d5dd5fb6dfc28b3f7ee`; os três no commit `9a1fdfcf`, e os dois primeiros conferem com o meta |
| resultado | [RESULTADO, seção 13](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): M3\* − M2 = +0,0489 [+0,0355; +0,0624], n = 150, t = 7,20, "> 0"; o sorteado −0,0106 [−0,0236; +0,0024], "indeterminado" |
| status | **positivo** no `longe_fixo`; indeterminado no sorteado |
| reproduzido | a primeira tentativa caiu (#507); a repetição, depois do conserto (#508), deu os mesmos logs (o PAINEL_V3, linha C1). É uma repetição interna, na mesma máquina; nenhuma replicação de fora |
| falta para reproduzir | o comando no meta; a versão do Python é a única do ambiente gravada (nenhuma lista de pacotes, nenhum SO) |

### 1.2 C2, o crédito na intenção

| campo | valor |
|---|---|
| pergunta | P-A: M2c − M2, o índice "ganhou, fica", nas 8 células do `longe_fixo` e do `comedouro` |
| plano | o mesmo arquivo, adendo 7, no commit [`4be65a03bcefa20bb9e51f3e6fae9da5ef0cb210`](https://github.com/matheusmmmp/digilab/blob/4be65a03bcefa20bb9e51f3e6fae9da5ef0cb210/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md) (2026-10-31 22:10:47) |
| plano → código | o commit do plano é o código da run; início 22:11:09 (22 s depois); árvore limpa |
| células e N | 12 células (4 donos × 3 lugares), braços M1, M2, M2c; 150 unidades, bases 75101–75505; 5 400 vidas |
| comando | não gravado no meta; o do plano: `python experiments/run_v2_habito_intencao.py --config experiments/configs/v2_habito_intencao/habito_intencao.json --processos 4` |
| ambiente | Python 3.13.0; 4 processos |
| artefatos | `habito_intencao/run/resultado.json` `5c7e51a50d6280d632c2c05fe9c980f9f47164cd0d3bf23b8703ed22080ed5eb`; `medidas.json` `93b136d6d94872e7788d354112ee4679e84abcf40e6f42d885387a7bdfb85a33`; `vidas.tar.gz` `261d1fbc32c1679a0ba9e63183f2620d7535880d3e6497319dd9283a146a572b`; commit `6b5d7e3d`; conferem com o meta |
| resultado | [RESULTADO, seção 14](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): P-A +0,0028 [−0,0003; +0,0060], n = 150, "≈ 0"; S1 "< 0" |
| status | **negativo** (registrado como negativo pelas D-C2-4-1 a 4) |
| reproduzido | não |
| falta para reproduzir | o comando no meta; o `vidas.tar.gz` nunca foi aberto por um script versionado (seção 2) |

### 1.3 C3, redecidir por evento

| campo | valor |
|---|---|
| pergunta | P-R: M3\*R − M3\*, a taxa por episódio, nas 4 células do `longe_fixo` |
| plano | adendo 8, no commit [`d0aff83e6cf9c4f23b8c2783f51a5b455a2e2fe9`](https://github.com/matheusmmmp/digilab/blob/d0aff83e6cf9c4f23b8c2783f51a5b455a2e2fe9/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md) (2026-11-01 01:21) |
| plano → código | o commit do plano é o código da run; início 01:45:19; árvore limpa |
| células e N | 12 células, braços M2, M2R, M3, M3R; 150 unidades, bases 76101–76505; 7 200 vidas |
| comando | não gravado no meta; o do plano: `python experiments/run_v2_redecidir_evento.py --config experiments/configs/v2_redecidir_evento/redecidir_evento.json --processos 4` |
| ambiente | Python 3.13.0; 4 processos |
| artefatos | `redecidir_evento/run/resultado.json` `41869752bccb39cec5a91d667a16839a34e34622898345d290c0e11da0337b5b`; `medidas.json` `d5b7c9748941972e5529f02fdd545c4a2e95b90ee32a48fe325e220b1cd050bf`; `vidas.tar.gz` `217add771f256fc8def2afefe2e30c97e7bb1f9d23b2baafba198aae7e396ba0`; commit `7747485b`; conferem com o meta |
| resultado | [RESULTADO, seção 15](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): P-R +0,0124 [−0,0060; +0,0308], n = 150, "indeterminado"; a guarda G-COMEDOURO "indeterminado" (não falha) |
| status | **indeterminado**; a `redecidir_evento` fica desligada |
| reproduzido | não (D-C3-4-1: sem repetir na 76xxx) |
| falta para reproduzir | o comando no meta; o `vidas.tar.gz` nunca foi aberto por um script versionado |

### 1.4 C4, a memória autobiográfica

| campo | valor |
|---|---|
| pergunta | REL − SEM, REL − REC, REL − EMB (Holm), a taxa por episódio, nas 4 células do `longe_fixo`; a guarda G-COMEDOURO, REL − SEM no `comedouro` |
| plano | adendo 9, no commit [`a287ba20fafdc1fbbf9be7100f89d9c90f466948`](https://github.com/matheusmmmp/digilab/blob/a287ba20fafdc1fbbf9be7100f89d9c90f466948/docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md) (2026-11-01 18:45:24) |
| plano → código | o commit do plano é o código da run; início 18:45:37 (13 s depois); árvore limpa |
| células e N | **12 células: 4 donos (atencioso, relapso, aleatório, incoerente) × 3 lugares (`longe_fixo`, `comedouro`, `longe`)**; braços REL, SEM, REC, EMB, RELsN, REL+F; 200 unidades, bases 77101–77505 (5 bases × 40); 14 400 vidas; 11 609 s de parede |
| comando | não gravado no meta; o do plano (A9.13): `python experiments/run_v2_memoria_autobio.py --config experiments/configs/v2_memoria_autobio/memoria_autobio.json --processos 4`, com `PYTHONIOENCODING=utf-8` (só o console) |
| ambiente | Python 3.13.0; 4 processos |
| artefatos | `memoria_autobio/run/resultado.json` `6f8c91d8e2b857194de1de00145a4da817efca76eb882bcd2d090dd3101cd6d3`; `medidas.json.gz` `8b48d0a234afc69adfaf72d150d0d4317d4f7dd9abfa7fc2e49908a6758fd93b` (descomprimido `869ff3971b91e6d848f3f9e16d1798049105442bde1968a6852daa852c153023`, o do meta); `vidas.tar.gz` `aa0c398716bf9b285889c3e3f490f9d3538b41d1135d9ee3b788fd28cfa50aed`; commit `1df2e328` |
| resultado | [RESULTADO, seção 16](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): REL − SEM +0,0646 [+0,0515; +0,0778]; REL − REC +0,0560 [+0,0427; +0,0693]; REL − EMB +0,0636 [+0,0507; +0,0764]; n = 200 cada; Holm rejeita os três; guarda +0,1981 [+0,1861; +0,2101], n = 200 |
| status | **positivo**, com a ressalva já registrada (o REL inclui o lugar lembrado do M-MEM; a D-C1-3 fechou como descritiva) |
| reproduzido | as vidas foram rejogadas e conferidas por dois leitores (o `descritivo_dc13_rel.py`, adendo 11, e o `auditoria_pet_vivo.py`), que conferem o sha256 do `vidas.tar.gz` e do `medidas.json.gz`; a run inteira nunca foi refeita do zero |
| falta para reproduzir | o comando no meta; saber se o `medidas.json.gz` sai igual byte a byte (o meta só grava o sha256 do descomprimido; um `.gz` com data no cabeçalho muda a cada gravação); a 14 400 vidas e ~3,2 h de parede, a A3 precisa do ok do Matheus para a máquina (V3-D8) |

### 1.5 AN4, o passeio

| campo | valor |
|---|---|
| pergunta | a guarda G-COMEDOURO-AN (LAB+P − LAB no `comedouro`) e o MOV (a fração das decisões que saem do lugar) |
| plano | [`PLANO_ANALISE_V3_ACOES_NOVAS.md`](https://github.com/matheusmmmp/digilab/blob/d3d993ba0ad3168448c8814e7a66ce3338a5d070/docs/PLANO_ANALISE_V3_ACOES_NOVAS.md) no commit `d3d993ba0ad3168448c8814e7a66ce3338a5d070` (2026-11-05 13:19) |
| plano → código | o plano é ancestral do código `cff554fda2ee8cafc1d8879ffcb74fab40ccbfa9`; início 15:59:31; árvore limpa |
| células e N | 8 células (4 donos × `comedouro`, `longe_fixo`), braços LAB, LAB+P; 200 unidades; 3 200 vidas |
| comando | não gravado no meta; o do plano: `python experiments/run_v3_acoes_novas.py --config experiments/configs/v3_acoes_novas/acoes_novas.json --processos 4` |
| ambiente | Python 3.13.0; 4 processos |
| artefatos | `artifacts_v3_acoes_novas/run/resultado.json` `70b7fc969af040e78e3d3667fc77e1b04886af623b248a26f5603e71285f1a16`; `medidas.json` `9f992e9cc9d503f77cfa9a0161f105be757e21f9515dc27427bcdd4f496196f5`; `vidas.tar.gz` `3fe40da49892abd83e1dc91fce424bbbe994c29e492f94dacb6b7cf7dc7adccd`; commit `a1399c05`; conferem com o meta |
| resultado | [RESULTADO_V3_ACOES_NOVAS](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/RESULTADO_V3_ACOES_NOVAS.md): G-COMEDOURO-AN −0,0263 [−0,0362; −0,0164], n = 200, t = −5,22, "< 0", falha; MOV +0,0236 [+0,0203; +0,0269], n = 200 |
| status | **negativo**; a `passeio` fica desligada |
| reproduzido | não |
| falta para reproduzir | o comando no meta; o `vidas.tar.gz` nunca foi aberto por um leitor (só o `tests/test_hooks.py` cita o caminho) |

### 1.6 GVN2, o gosto visual (leitura das vidas da GV3 e da GV3b)

| campo | valor |
|---|---|
| pergunta | descritiva: Spearman(Δ_I, dif_fica) e as saídas da TV, nas vidas gravadas das duas runs; nenhuma vida nova |
| plano | [`PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md`](https://github.com/matheusmmmp/digilab/blob/cb9803321bf0a50ca146a9b9c4618c167bdeeb08/docs/PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md), commit `cb9803321bf0a50ca146a9b9c4618c167bdeeb08` (2026-11-12 16:20:28) |
| plano → leitura | o plano é ancestral do commit da leitura `5b4c0fa3eea4380ea1f4b09d9d00417a61e2c747` (16:49:26). Não há meta: a hora em que a leitura rodou não está gravada; o plano diz que foi empurrado antes de abrir os `.tar.gz` |
| as runs de base | GV3: plano `487360403e720857c6096254aab33f8e8cb85084` = código, início 2026-11-11 23:37:47; GV3b: plano (adendo 2) `fd755ddfdb04405bd450aab5405614c510ee881a`, ancestral do código `597638b2e2b896b1f51c8ecd347c8085f070cd7e`, início 2026-11-12 12:23:30; as duas com árvore limpa, Python 3.13.0 |
| comando | `python artifacts_v3_gosto_visual/gvn2/leitura.py <raiz>` (plano, seção 1); um processo |
| artefatos | `gvn2/leitura.json` `67eb6e8bec4c8bc5b74a2caa5176698d8d765149fb8b60d649c0d70bead5a68a`; `gvn2/leitura.py` `92c0eeaa1f17c108e8cb32f5f3e11d0d02510d4cd79b449cc748b169636eb724`; as vidas lidas: GV3 `vidas.tar.gz` `e10f2dc09b2789f38de2e382fc4c6ac3b28e570302559fcc2225f76e5cd955b5`, GV3b `f2ce4a5f24bd674db21893202bf4c47c337f9e3f258ac6c6c80bd5790afbf08d` |
| resultado | [gosto_visual_porque_negativo.md, seção 6](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/futuro/gosto_visual_porque_negativo.md) (não há `RESULTADO_V3_*` próprio): Spearman 0,823 [0,694; 0,886] na GV3 e 0,645 [0,485; 0,743] na GV3b (`leitura.json`, `M2_proprio.spearman_di_dif_fica`) |
| status | **descritivo** (o plano diz: sem correção para comparações múltiplas; um IC que não contém 0 não é "o efeito apareceu"). As runs GV3 e GV3b ficam negativas |
| reproduzido | o `tests/test_gosto_visual_gvn2.py` confere que a leitura sai igual byte a byte |
| falta para reproduzir | nada para refazer a leitura; o resultado mora em `docs/futuro/`, fora do lugar dos resultados |

### 1.7 PET_VIVO, etapa 0 (a auditoria da escolha e "age pelo estado")

| campo | valor |
|---|---|
| pergunta | pós hoc, descritiva: a linha HA/HC/HP por grupo (C4 REL e SEM × 3 lugares, e a AN0) |
| plano | [`PLANO_ANALISE_V3_PET_VIVO.md`](https://github.com/matheusmmmp/digilab/blob/545a4a8624ad8b6f3783923f76644db2ebb4d4cd/docs/PLANO_ANALISE_V3_PET_VIVO.md), com o registro da run (seção 11) no commit `545a4a8624ad8b6f3783923f76644db2ebb4d4cd` (2026-11-08 10:43) |
| plano → código | o registro é ancestral do branch da run `58c282776a4743fdfe2b74e233feae045e766026`; a C4 rejogada com o código `a287ba20`. **Não há meta.json**: o `auditoria.json` grava o `commit_da_c4` (completo), os sha256 das fontes e dos scripts, os processos (4) e a parede, mas não o commit do script, o Python nem o início. O início (19:51:31) só está declarado no RESULTADO |
| células e N | 4 800 vidas da C4 (REL e SEM, 3 lugares, 800 por grupo) e 10 da AN0; o contrafactual em 970 |
| comando | o do plano, seção 11: `python experiments/auditoria_pet_vivo.py --codigo D:\Trab\digilab\v3-pet-vivo-a287ba2 --processos 4`; o `PASTA_C4_PADRAO` aponta para `D:\Trab\digilab\v3-memoria-run\…`, fora do repositório, mas o script confere o sha256 dos arquivos de lá contra os versionados da C4 (`aa0c3987…`, `8b48d0a2…`) |
| artefatos | `artifacts_v3_pet_vivo/auditoria/auditoria.json` `3bb42d95eb415ebe2bc3db6ef402478cb742f2ecc4a30b2224b7d1cf054fa780` (no git, LF; o do disco com CRLF é outro, como o RESULTADO diz); `auditoria_vidas.json.gz` `14a4b75f0887952ecb355fbe50f8a7fb2f74ee42245da557d4e57e95b0d0b63b`; commit `b3aead22` |
| resultado | [RESULTADO_V3_PET_VIVO](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/RESULTADO_V3_PET_VIVO.md): a linha "indeterminado" nos 6 grupos da C4; a AN0 e as SE-C e RV como lá estão |
| status | **descritivo**, pós hoc, gerador de hipótese (seção 6 do plano) |
| reproduzido | não |
| falta para reproduzir | um meta com o commit do script e o Python; o comando com caminhos do repositório (`--pasta-c4 artifacts_v2_digibrain_prototipo/memoria_autobio/run`), em vez das pastas locais `D:\Trab\digilab\v3-*` |

### 1.8 COOP A1, a cooperação com o irmão aleatório

| campo | valor |
|---|---|
| pergunta | A1-EMERGE (B1 − B0 no P1), A1-DOSE (a inclinação D0 → B1 → DM), A1-CUSTO, com o irmão aleatório (adendo 1) |
| plano | [`PLANO_ANALISE_V3_COOPERACAO.md`](https://github.com/matheusmmmp/digilab/blob/c3b930fc9801750d6d21b6c97f93484b52f1d402/docs/PLANO_ANALISE_V3_COOPERACAO.md), seção 12, aprovado no commit `c3b930fc9801750d6d21b6c97f93484b52f1d402` (2026-11-12 16:19:29); o registro da análise (A1-CB3, N = 80) no `0eb511d4` (16:22:47), na `main` pelo merge `0d1013003ea911bfec19236e4a7339258731c2d4` (#923, 16:24:34) |
| plano → código | o manifesto grava `codigo` **curto**, `0b33fb86` (resolve a `0b33fb86be5f098b202ecb7b5e11b6888d7404f9`, o merge #922 das 16:21:15), e o `registro` `0d101300`. O plano aprovado é ancestral do código; o registro **não** é (veio 3 min depois do commit gravado como código). O `--registro` é exigido pelo orquestrador para a faixa principal, o que põe a run depois do registro, mas o manifesto não grava o início, a árvore limpa nem o Python |
| células e N | 80 sementes (92201–92280), 7 braços, 560 vidas de 8 dias; os testes com n = 69 (vidas com oportunidade) e 80 |
| comando | não gravado; o orquestrador é o `experiments/run_v3_cooperacao_bancada.py --mundo irmao_aleatorio --registro … --saida …` e a análise o `experiments/analisar_v3_cooperacao_bancada.py`; os argumentos exatos não estão no repositório |
| artefatos | `artifacts_v3_cooperacao_bancada/resultado_ad1.json` `d693f0466c784ebb3ce6a4434959fd865da3ea00bb631a4e07d7527e3453f28c` e `manifesto_ad1.json`, commit `98b48241`. **As vidas não estão no git:** `experiments/runs/cooperacao_bancada/principal_ad1.jsonl`, sha256 `d9c0b5c4…` no manifesto |
| resultado | [cooperacao_bancada_resultado.md, seção 5](https://github.com/matheusmmmp/digilab/blob/f8fa9ad2647ad9d4164dced1aeeec8d6697de611/docs/futuro/cooperacao_bancada_resultado.md): A1-EMERGE +0,0008 [−0,0014; +0,0039], n = 69, NÃO CONFIRMA; A1-DOSE inclinação +0,0008 [−0,0014; +0,0039], n = 69, NÃO CONFIRMA; A1-CUSTO +0,0009 [−0,0012; +0,0034], n = 80, CONFIRMA; o P1_neg 0,081 no B0 e 0,072 no B1 |
| status | **negativo** para EMERGE e DOSE; CUSTO pela regra do plano |
| reproduzido | não |
| falta para reproduzir | **o arquivo das vidas** (o resultado não se refaz a partir do repositório); o SHA completo do código, o comando, o Python e o início no manifesto |

## 2. As lacunas pedidas

### (a) Os binários (`.gz`, `.tar.gz`) em `artifacts_*/`

São 16 no snapshot (lista completa no `auditoria.json`, `gz_em_artifacts`). "Aberto" quer dizer: um script versionado lê o arquivo e confere o
sha256 dele.

| arquivo | aberto por |
|---|---|
| `artifacts_v2_digibrain_prototipo/longe_regular/run/vidas.tar.gz` (C1) | `experiments/descritivo_dc13_longe_fixo.py` |
| `artifacts_v2_digibrain_prototipo/memoria_autobio/run/vidas.tar.gz` e `medidas.json.gz` (C4) | `experiments/descritivo_dc13_rel.py`, `experiments/auditoria_pet_vivo.py`; o `medidas.json.gz` também pelo `experiments/plano_an3_poder_acoes_novas.py` |
| `artifacts_v3_gosto_visual/gosto_visual/vidas.tar.gz` (GV3) e `gosto_visual_enjoo2/vidas.tar.gz` (GV3b) | `artifacts_v3_gosto_visual/gvn2/leitura.py`, `fala_limiares/extrair_sinais.py` |
| `artifacts_v3_gosto_visual/fala_limiares/sinais.json.gz` | `artifacts_v3_gosto_visual/fala_limiares/calibrar.py` |
| `artifacts_v3_conversa_dc3/run/vidas.tar.gz` | `experiments/d_comida_dc4.py` |
| `artifacts_v3_individualidade/vidas.tar.gz` | os `experiments/run_v3_individualidade_i5/i7*.py` |
| **`artifacts_v2_digibrain_prototipo/habito_intencao/run/vidas.tar.gz` (C2)** | **nenhum** |
| **`artifacts_v2_digibrain_prototipo/redecidir_evento/run/vidas.tar.gz` (C3)** | **nenhum** |
| **`artifacts_v3_acoes_novas/run/vidas.tar.gz` (AN4)** | **nenhum** (só o `tests/test_hooks.py` cita o caminho) |
| **`artifacts_v3_pet_vivo/auditoria/auditoria_vidas.json.gz`** | **nenhum** (só gravado) |
| **`artifacts_v3_gosto_visual/gosto_visual_enjoo/vidas.tar.gz`** (a GV3b que caiu, `LEIA.md` ao lado) | **nenhum** |
| **`artifacts_v3_gosto_visual/piloto*/vidas.tar.gz`** (3 pilotos) | **nenhum** |

A busca é textual (o caminho no `.py`), conferida à mão nos leitores acima; um leitor que monte o caminho sem citá-lo escaparia, e não achei
nenhum.

### (b) Os meta sem SHA do código

Dos oito experimentos, **só o COOP A1** não tem o SHA completo (o manifesto grava `0b33fb86`). O GVN2 e o PET_VIVO não têm meta.json; o PET_VIVO
grava o commit da C4, não o do script.

No repositório inteiro, dos 190 `meta.json`/`manifesto*.json` em `artifacts_*/`, **145 não gravam commit nenhum** e 2 gravam o SHA curto (os dois
manifestos da cooperação). Os 145 são das runs da v1 e da V2 (`artifacts_v2_pet_que_pensa` 56, `artifacts_v2_calibracao_conjunta` 20,
`artifacts_v2_revisao` 11, `artifacts_v2_validacao_unica` 10, e outras), e quase todos gravam o sha256 das fontes (`fontes_sha256`,
`engine_sha256`, `bancada_sha256`…), que prende o código pelo conteúdo, não pelo commit. Nenhum deles é dos oito.

**Nenhum dos oito grava o comando exato no meta.** O que prende a run é o `config_arquivo` com o `config_sha256` e o comando escrito no
plano.

### (c) Plano commitado depois da primeira vida

**Nenhum caso achado entre os oito.** Em C1, C2, C3, C4 e GV3 o commit do plano é o próprio código da run, e o início vem depois (de 13 s na
C4 a 1 h 08 min na C1). Em AN4 e GV3b o plano é ancestral do código. Dois casos ficam **não verificáveis pelo artefato**:
- **GVN2 e PET_VIVO:** o plano é ancestral do commit do resultado, mas sem meta não há o início gravado;
- **COOP A1:** o registro da análise não é ancestral do código gravado e o manifesto não tem o início; a ordem só se infere do `--registro`
  exigido pelo orquestrador e dos horários dos commits (registro 16:24:34, resultado 16:29:45, 1 065 s de vidas em 4 processos).

## 3. O que a auditoria achou fora da lista pedida

- **As células da C4 não são "3 lugares × 2 doadores":** são 4 donos × 3 lugares (12), com o primário só nas 4 do `longe_fixo`. O plano da A1
  vai usar as células como estão no meta da C4.
- **Dois resultados moram em `docs/futuro/`** (a GVN2 e a COOP A1), não num `RESULTADO_V3_*`.
- **O `medidas.json` da C4 está versionado** (como `.gz`), embora a linha das worktrees do PAINEL_V3 diga que ele ficou fora do git na
  `v3-memoria-run`. O que ficou fora são as pastas locais; o arquivo no git confere com o meta.
- **O PET_VIVO rodou de caminhos absolutos locais** (`D:\Trab\digilab\v3-pet-vivo-a287ba2`, `v3-memoria-run`), conferidos por sha256. Um
  terceiro precisa trocar os dois argumentos.

## 4. O que esta auditoria não demonstra

- Que os números dos documentos saem dos artefatos (a ferramenta confere os sha256, não refaz as contas).
- Que alguma run se reproduz: nenhuma foi refeita aqui.
- Que os planos não foram ajustados entre o commit e a run por fora do git: a auditoria só vê o que foi commitado.

## 5. O que muda para as fases seguintes

- **A1 (baseline):** o contraste primário vai no `longe_fixo`, como a C1 a C4; as células são as 12 da C4 (4 donos × 3 lugares). O meta da
  run nova grava o comando, o Python, o Node (se usar) e o sha256 do `resultado.json` e do `medidas.json`.
- **A3 (replicação da C4):** a C4 tem tudo versionado (código `a287ba20`, config com sha256, `resultado.json`, `medidas.json.gz`,
  `vidas.tar.gz`). O risco conhecido é o `.gz`: a comparação justa é pelo conteúdo descomprimido (`869ff397…`), como o meta grava, e o
  `.gz` em si pode divergir sem que a run divirja. A C4 custa ~3,2 h com 4 processos.
- **COOP A1:** não se replica a partir do repositório enquanto o `principal_ad1.jsonl` não estiver versionado.

## 6. Para o Matheus (CHECKPOINT A1)

- **Aprovar esta auditoria** como a base da A1. Recomendação: aprovar. Custo de errar: uma lacuna que eu não vi passa para o pré-registro
  da A3.
- **As células da A1:** as 12 da C4 (4 donos × 3 lugares, o primário no `longe_fixo`), e não "3 × 2" como no prompt. Recomendação: as 12
  da C4, para o baseline ficar na mesma régua. Custo de errar: um baseline em células diferentes não compara com o modular.
- **Versionar o `principal_ad1.jsonl` da COOP A1** (se ainda estiver no disco) num PR à parte. Recomendação: sim, se couber; senão, a COOP
  A1 fica registrada como "não reproduzível pelo repositório". Custo de errar: nenhum resultado muda; só a replicação.
