# jusbrasil_client.py
import os
from typing import Any, Dict, List, Optional

import httpx


JUSBRASIL_BG_BASE_URL = "https://api.jusbrasil.com.br"
JUSBRASIL_BASE_JUDICIAL_URL = "https://op.digesto.com.br"

JUSBRASIL_API_KEY = os.getenv("JUSBRASIL_API_KEY")


class JusbrasilClient:
    """Cliente simples para API do Jusbrasil."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or JUSBRASIL_API_KEY
        if not self.api_key:
            raise RuntimeError(
                "JUSBRASIL_API_KEY não configurada. "
                "Defina a variável de ambiente JUSBRASIL_API_KEY."
            )

    @property
    def _bg_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apikey": self.api_key,
        }

    @property
    def _base_judicial_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "apikey": self.api_key,
        }

    async def consultar_processos_por_documento(
        self,
        document_number: str,
        cursor: str = "",
        size: int = 50,
        segment: str = "civil",
    ) -> Dict[str, Any]:
        url = f"{JUSBRASIL_BG_BASE_URL}/background-check/lawsuits/{segment}"

        payload = {
            "documentNumber": document_number,
            "pagination": {"cursor": cursor, "size": size},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._bg_headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def montar_resumo_processos_documento(data: Dict[str, Any]) -> str:
        lawsuits: List[Dict[str, Any]] = data.get("lawsuits") or data.get("results") or []

        if not lawsuits:
            return "Nenhum processo encontrado para este CPF/CNPJ na base do Jusbrasil."

        linhas = ["📑 *Processos encontrados no Jusbrasil:*", ""]

        for idx, proc in enumerate(lawsuits, start=1):
            numero = proc.get("number") or proc.get("numeroProcesso") or "N/D"
            tribunal = proc.get("court") or proc.get("tribunal") or "N/D"
            uf = proc.get("state") or proc.get("uf") or ""
            instancia = proc.get("instance") or proc.get("instancia") or "N/D"
            status_ = proc.get("status") or proc.get("situacao") or "N/D"
            assunto = proc.get("subject") or proc.get("assunto") or "N/D"
            last_update = proc.get("lastUpdate") or proc.get("dataUltimaMovimentacao") or "N/D"

            linhas.append(
                f"*{idx}.* [{tribunal}{('/' + uf) if uf else ''}] {numero}\n"
                f"   - Instância: {instancia}\n"
                f"   - Status: {status_}\n"
                f"   - Assunto: {assunto}\n"
                f"   - Última atualização: {last_update}"
            )

        return "\n".join(linhas)

    async def consultar_processo_por_cnj(self, numero_cnj: str) -> Dict[str, Any]:
        numero_limpo = (
            numero_cnj.replace("-", "")
            .replace(".", "")
            .replace("_", "")
            .replace("/", "")
            .strip()
        )

        url = (
            f"{JUSBRASIL_BASE_JUDICIAL_URL}"
            f"/api/base-judicial/tribproc/{numero_limpo}?tipo_numero=5"
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._base_judicial_headers)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def montar_resumo_processo_cnj(data: Dict[str, Any]) -> str:
        if not data:
            return "Nenhum dado retornado pela API do Jusbrasil para este processo."

        numero = data.get("numeroProcesso") or data.get("numero") or "N/D"
        tribunal = data.get("tribunal") or "N/D"
        uf = data.get("uf") or ""
        instancia = data.get("instancia") or data.get("grau") or "N/D"
        classe = data.get("classe") or data.get("classeProcessual") or "N/D"
        assunto = data.get("assuntoPrincipal") or data.get("assunto") or "N/D"
        data_dist = data.get("dataDistribuicao") or data.get("dataAjuizamento") or "N/D"
        ultima_atualizacao = (
            data.get("ultimaAtualizacao") or data.get("dataHoraUltimaAtualizacao") or "N/D"
        )

        movimentos = data.get("movimentos") or data.get("andamentos") or []
        ultimo_mov = movimentos[-1] if movimentos else None
        if ultimo_mov:
            mov_data = (
                ultimo_mov.get("dataHora")
                or ultimo_mov.get("data")
                or ultimo_mov.get("dataMovimentacao")
                or "N/D"
            )
            mov_desc = (
                ultimo_mov.get("descricao")
                or ultimo_mov.get("nome")
                or ultimo_mov.get("texto")
                or "N/D"
            )
            resumo_mov = f"{mov_data} – {mov_desc}"
        else:
            resumo_mov = "Nenhuma movimentação encontrada (ou não disponibilizada)."

        msg = (
            "⚖️ *Processo via Jusbrasil*\n\n"
            f"*Número CNJ:* {numero}\n"
            f"*Tribunal:* {tribunal}{('/' + uf) if uf else ''}\n"
            f"*Instância:* {instancia}\n"
            f"*Classe:* {classe}\n"
            f"*Assunto principal:* {assunto}\n"
            f"*Data de distribuição/ajuizamento:* {data_dist}\n"
            f"*Última atualização:* {ultima_atualizacao}\n\n"
            "*Última movimentação conhecida:*\n"
            f"{resumo_mov}"
        )

        return msg
