# main.py
from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from datajud_client import DatajudClient, TribunalDatajud
from jusbrasil_client import JusbrasilClient


app = FastAPI(title="Jul.IA – Integração DataJud + Jusbrasil")


class TribunalEnum(str, Enum):
    TJAC = "TJAC"
    TJAL = "TJAL"
    TJAM = "TJAM"
    TJAP = "TJAP"
    TJBA = "TJBA"
    TJCE = "TJCE"
    TJDFT = "TJDFT"
    TJES = "TJES"
    TJGO = "TJGO"
    TJMA = "TJMA"
    TJMG = "TJMG"
    TJMS = "TJMS"
    TJMT = "TJMT"
    TJPA = "TJPA"
    TJPB = "TJPB"
    TJPE = "TJPE"
    TJPI = "TJPI"
    TJPR = "TJPR"
    TJRJ = "TJRJ"
    TJRN = "TJRN"
    TJRO = "TJRO"
    TJRR = "TJRR"
    TJRS = "TJRS"
    TJSC = "TJSC"
    TJSE = "TJSE"
    TJSP = "TJSP"
    TJTO = "TJTO"


class ConsultaDatajudRequest(BaseModel):
    numero_processo_cnj: str
    tribunal: TribunalEnum


class ConsultaDatajudAutoRequest(BaseModel):
    numero_processo_cnj: str


class ConsultaDatajudResponse(BaseModel):
    mensagem: str
    numero_processo_cnj: Optional[str] = None
    tribunal: Optional[str] = None


def _map_tribunal_enum_to_client(t: TribunalEnum) -> TribunalDatajud:
    mapping = {
        TribunalEnum.TJAC: TribunalDatajud.TJAC,
        TribunalEnum.TJAL: TribunalDatajud.TJAL,
        TribunalEnum.TJAM: TribunalDatajud.TJAM,
        TribunalEnum.TJAP: TribunalDatajud.TJAP,
        TribunalEnum.TJBA: TribunalDatajud.TJBA,
        TribunalEnum.TJCE: TribunalDatajud.TJCE,
        TribunalEnum.TJDFT: TribunalDatajud.TJDFT,
        TribunalEnum.TJES: TribunalDatajud.TJES,
        TribunalEnum.TJGO: TribunalDatajud.TJGO,
        TribunalEnum.TJMA: TribunalDatajud.TJMA,
        TribunalEnum.TJMG: TribunalDatajud.TJMG,
        TribunalEnum.TJMS: TribunalDatajud.TJMS,
        TribunalEnum.TJMT: TribunalDatajud.TJMT,
        TribunalEnum.TJPA: TribunalDatajud.TJPA,
        TribunalEnum.TJPB: TribunalDatajud.TJPB,
        TribunalEnum.TJPE: TribunalDatajud.TJPE,
        TribunalEnum.TJPI: TribunalDatajud.TJPI,
        TribunalEnum.TJPR: TribunalDatajud.TJPR,
        TribunalEnum.TJRJ: TribunalDatajud.TJRJ,
        TribunalEnum.TJRN: TribunalDatajud.TJRN,
        TribunalEnum.TJRO: TribunalDatajud.TJRO,
        TribunalEnum.TJRR: TribunalDatajud.TJRR,
        TribunalEnum.TJRS: TribunalDatajud.TJRS,
        TribunalEnum.TJSC: TribunalDatajud.TJSC,
        TribunalEnum.TJSE: TribunalDatajud.TJSE,
        TribunalEnum.TJSP: TribunalDatajud.TJSP,
        TribunalEnum.TJTO: TribunalDatajud.TJTO,
    }
    return mapping[t]


@app.post("/api/datajud/consulta-processo", response_model=ConsultaDatajudResponse)
def consultar_processo_datajud(payload: ConsultaDatajudRequest):
    client = DatajudClient()
    tribunal_client = _map_tribunal_enum_to_client(payload.tribunal)

    try:
        data = client.consultar_por_cnj(
            numero_cnj=payload.numero_processo_cnj,
            tribunal=tribunal_client,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao consultar a API Pública do DataJud: {exc}",
        )

    source = client.extrair_primeiro_resultado(data)
    if not source:
        msg = (
            "❌ Nenhum processo público encontrado no DataJud "
            f"para o número informado ({payload.numero_processo_cnj}) "
            f"no tribunal {payload.tribunal.value}."
        )
        return ConsultaDatajudResponse(
            mensagem=msg,
            numero_processo_cnj=payload.numero_processo_cnj,
            tribunal=payload.tribunal.value,
        )

    resumo = client.montar_resumo_processo(source)
    return ConsultaDatajudResponse(
        mensagem=resumo,
        numero_processo_cnj=source.get("numeroProcesso"),
        tribunal=source.get("tribunal"),
    )


@app.post("/api/datajud/consulta-processo-auto", response_model=ConsultaDatajudResponse)
def consultar_processo_datajud_auto(payload: ConsultaDatajudAutoRequest):
    client = DatajudClient()

    prioridade: List[TribunalDatajud] = [
        TribunalDatajud.TJPR,
        TribunalDatajud.TJSP,
        TribunalDatajud.TJMG,
    ]

    todos = list(TribunalDatajud)
    restantes = [t for t in todos if t not in prioridade]
    ordem_busca = prioridade + restantes

    ultimo_erro: Optional[Exception] = None

    for trib in ordem_busca:
        try:
            data = client.consultar_por_cnj(
                numero_cnj=payload.numero_processo_cnj,
                tribunal=trib,
            )
        except Exception as exc:
            ultimo_erro = exc
            continue

        source = client.extrair_primeiro_resultado(data)
        if source:
            resumo = client.montar_resumo_processo(source)
            return ConsultaDatajudResponse(
                mensagem=resumo,
                numero_processo_cnj=source.get("numeroProcesso"),
                tribunal=source.get("tribunal") or trib.name,
            )

    if ultimo_erro:
        detail = (
            "Não foi possível localizar o processo em nenhum tribunal via DataJud. "
            f"Último erro da API: {ultimo_erro}"
        )
    else:
        detail = (
            "Não foi encontrado nenhum processo público no DataJud para "
            f"o número informado ({payload.numero_processo_cnj}) "
            "em nenhum Tribunal de Justiça."
        )

    raise HTTPException(status_code=404, detail=detail)


class ConsultaJusbrasilCPFRequest(BaseModel):
    document_number: str
    cursor: str = ""
    size: int = 50
    segment: str = "civil"


class ConsultaJusbrasilCNJRequest(BaseModel):
    numero_processo_cnj: str


class ConsultaJusbrasilResponse(BaseModel):
    mensagem: str


@app.post("/api/jusbrasil/consulta-cpf", response_model=ConsultaJusbrasilResponse)
async def consultar_jusbrasil_por_cpf(payload: ConsultaJusbrasilCPFRequest):
    client = JusbrasilClient()

    doc_limpo = "".join(ch for ch in payload.document_number if ch.isdigit())

    try:
        data = await client.consultar_processos_por_documento(
            document_number=doc_limpo,
            cursor=payload.cursor,
            size=payload.size,
            segment=payload.segment,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao consultar a API do Jusbrasil (CPF/CNPJ): {exc}",
        )

    msg = client.montar_resumo_processos_documento(data)
    return ConsultaJusbrasilResponse(mensagem=msg)


@app.post("/api/jusbrasil/consulta-cnj", response_model=ConsultaJusbrasilResponse)
async def consultar_jusbrasil_por_cnj(payload: ConsultaJusbrasilCNJRequest):
    client = JusbrasilClient()

    try:
        data = await client.consultar_processo_por_cnj(payload.numero_processo_cnj)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao consultar a base judicial do Jusbrasil (CNJ): {exc}",
        )

    msg = client.montar_resumo_processo_cnj(data)
    return ConsultaJusbrasilResponse(mensagem=msg)
