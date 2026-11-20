"""O resumo descritivo da marcacao da DC4 encerrada (experiments/resumo_marcacao_dc4.py): conta certo e falha alto se faltar resposta."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

import resumo_marcacao_dc4 as rm  # noqa: E402


def _pasta(tmp_path: Path, leg: dict, par: dict) -> Path:
    itens = {"legibilidade": [{"id": i} for i in ("L0", "L1", "L2", "L3")], "pares": [{"id": "P0"}, {"id": "P1"}],
             "referencia": [{"id": "F0"}], "injecao": [{"id": "I0"}]}
    chave = {"L0": {"braco": "G", "certa": "fome"}, "L1": {"braco": "G", "certa": "solidao"}, "L2": {"braco": "H", "certa": "higiene"},
             "L3": {"braco": "S", "certa": "fome"},
             "P0": {"comparacao": "HxG", "esquerda": "H", "direita": "G"}, "P1": {"comparacao": "SxG", "esquerda": "G", "direita": "S"}}
    (tmp_path / "itens.json").write_text(json.dumps(itens), encoding="utf-8")
    (tmp_path / "chave.json").write_text(json.dumps(chave), encoding="utf-8")
    resp = tmp_path / "respostas"
    resp.mkdir()
    for nome, d in (("legibilidade", leg), ("pares", par)):
        linhas = [json.dumps({"id": i, "resposta": r, "quando": "x"}) for i, r in d.items()]
        (resp / f"{nome}.jsonl").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return tmp_path


def test_conta_por_braco(tmp_path):
    p = _pasta(tmp_path, {"L0": {"resposta": "fome"}, "L1": {"resposta": "nada"}, "L2": {"resposta": "higiene"},
                   "L3": {"resposta": "solidao"}},
               {"P0": {"escolha": "esquerda"}, "P1": {"escolha": "esquerda"}})
    r = rm.resumir(p)
    assert r["legibilidade"]["G"]["acertos"] == 1 and r["legibilidade"]["G"]["nada"] == 1 and r["legibilidade"]["G"]["n"] == 2
    assert r["legibilidade"]["H"]["acerto"] == 1.0
    assert r["pares"]["HxG"]["escolhas"] == {"H": 1} and r["pares"]["SxG"]["escolhas"] == {"G": 1}
    assert r["nao_marcado"] == {"referencia": "0 de 1", "injecao": "0 de 1"}


def test_falha_alto_se_falta_resposta(tmp_path):
    p = _pasta(tmp_path, {"L0": {"resposta": "fome"}}, {"P0": {"escolha": "esquerda"}, "P1": {"escolha": "direita"}})
    with pytest.raises(SystemExit):
        rm.resumir(p)
