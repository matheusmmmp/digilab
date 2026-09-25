"""Alerta por e-mail do gasto com a API do Claude (so biblioteca padrao).

Configuracao so por variaveis de ambiente (senha nunca em arquivo, git ou linha de comando):
    DIGILAB_SMTP_USUARIO   conta que ENVIA (ex.: um Gmail com senha de app)
    DIGILAB_SMTP_SENHA     senha de app dessa conta
    DIGILAB_SMTP_HOST      padrao smtp.gmail.com
    DIGILAB_SMTP_PORTA     padrao 587 (STARTTLS)
Destino: --alerta-email do servidor (padrao EMAIL_ALERTA_PADRAO).

Sem usuario/senha o alerta fica DESLIGADO e o servidor avisa na partida; o teto de
gasto continua valendo do mesmo jeito (o alerta so avisa, quem bloqueia e o ControleGasto).
"""

from __future__ import annotations

import os
import smtplib
import ssl
import threading
from email.message import EmailMessage

EMAIL_ALERTA_PADRAO = "matheusmmmp@hotmail.com"   # pedido do pesquisador, 2026-09-24
NIVEIS_ALERTA = (0.5, 0.8, 1.0)                   # fracao do teto que dispara um aviso
TIMEOUT_SMTP_S = 20.0


class AlertaEmail:
    def __init__(self, destino: str = EMAIL_ALERTA_PADRAO, ambiente: dict | None = None) -> None:
        amb = os.environ if ambiente is None else ambiente
        self.destino = destino
        self.usuario = amb.get("DIGILAB_SMTP_USUARIO", "")
        self.senha = amb.get("DIGILAB_SMTP_SENHA", "")
        self.host = amb.get("DIGILAB_SMTP_HOST", "smtp.gmail.com")
        self.porta = int(amb.get("DIGILAB_SMTP_PORTA", "587"))

    @property
    def ativo(self) -> bool:
        return bool(self.usuario and self.senha and self.destino)

    def motivo_inativo(self) -> str:
        return "" if self.ativo else "faltam DIGILAB_SMTP_USUARIO e/ou DIGILAB_SMTP_SENHA no ambiente"

    def enviar(self, assunto: str, texto: str) -> None:
        """Envia agora (levanta erro se falhar). Use `avisar` para nao travar o servidor."""
        if not self.ativo:
            raise RuntimeError("alerta por e-mail desligado: " + self.motivo_inativo())
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = self.usuario, self.destino, assunto
        msg.set_content(texto)
        with smtplib.SMTP(self.host, self.porta, timeout=TIMEOUT_SMTP_S) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(self.usuario, self.senha)
            s.send_message(msg)

    def avisar(self, nivel: float, gasto: dict) -> None:
        """Chamado pelo ControleGasto ao cruzar um nivel; manda em segundo plano e loga no console."""
        assunto = f"Digilab: gasto da fala por LLM em {nivel:.0%} do teto"
        texto = (f"O gasto acumulado com a API do Claude chegou a US$ {gasto['gasto_usd']:.4f} "
                 f"de US$ {gasto['limite_usd']:.2f} ({gasto['chamadas']} chamadas).\n"
                 + ("O teto foi atingido: o servidor parou de chamar a API e usa so as frases prontas.\n"
                    if nivel >= 1.0 else "")
                 + "Para liberar mais, aumente --limite-usd ou apague servidor/gasto_fala.json.")
        print(f"  ALERTA DE GASTO: {assunto} (US$ {gasto['gasto_usd']:.4f})", flush=True)
        if not self.ativo:
            print(f"  e-mail NAO enviado: {self.motivo_inativo()}", flush=True)
            return

        def _enviar():
            try:
                self.enviar(assunto, texto)
                print(f"  e-mail de alerta enviado para {self.destino}", flush=True)
            except Exception as err:   # nao derruba o servidor; o teto continua valendo
                print(f"  FALHA ao enviar o e-mail de alerta ({type(err).__name__}: {err})", flush=True)

        threading.Thread(target=_enviar, daemon=True).start()
