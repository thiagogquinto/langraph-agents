"""MCP server com tools simples para prototipar planejamento de cultivo."""

import json
from typing import Any

from ddgs import DDGS
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Planejamento de Cultivo")


CULTIVARES_DB = {
    "soja_precoce": {
        "cultura": "soja",
        "janela_plantio": "setembro-novembro",
        "temp_ideal_min": 20,
        "temp_ideal_max": 30,
        "chuva_ideal_min": 350,
        "chuva_ideal_max": 700,
        "regioes_parana": ["norte", "noroeste", "oeste"],
    },
    "milho_safrinha": {
        "cultura": "milho",
        "janela_plantio": "janeiro-março",
        "temp_ideal_min": 18,
        "temp_ideal_max": 32,
        "chuva_ideal_min": 280,
        "chuva_ideal_max": 550,
        "regioes_parana": ["oeste", "sudoeste", "centro-oeste"],
    },
    "trigo_ciclo_medio": {
        "cultura": "trigo",
        "janela_plantio": "abril-junho",
        "temp_ideal_min": 12,
        "temp_ideal_max": 22,
        "chuva_ideal_min": 250,
        "chuva_ideal_max": 450,
        "regioes_parana": ["sul", "centro-sul", "sudoeste"],
    },
}


PERMITIDOS_DB = {
    "soja": ["glifosato", "fomesafen", "clethodim"],
    "milho": ["atrazina", "nicosulfuron", "mesotriona"],
    "trigo": ["2,4-d", "metsulfuron", "tebuconazol"],
}


def _normalizar(texto: str) -> str:
    return (texto or "").strip().lower()


def _to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def listar_cultivares_por_regiao(regiao: str) -> str:
    """Lista cultivares cadastradas que fazem sentido para a região informada.

    Args:
        regiao: Região do Paraná (ex.: norte, oeste, centro-sul).
    """
    # Extrai apenas o nome principal da região (ex: 'norte' de 'norte do Paraná')
    regiao_norm = _normalizar(regiao)
    for palavra in ["norte", "noroeste", "oeste", "sudoeste", "centro-oeste", "centro-sul", "sul"]:
        if palavra in regiao_norm:
            regiao_norm = palavra
            break
    aptas = []

    for nome, dados in CULTIVARES_DB.items():
        regioes = [_normalizar(item) for item in dados.get("regioes_parana", [])]
        if regiao_norm in regioes:
            aptas.append(
                {
                    "cultivar": nome,
                    "cultura": dados["cultura"],
                    "janela_plantio": dados["janela_plantio"],
                }
            )

    return _to_json(
        {
            "regiao": regiao,
            "quantidade": len(aptas),
            "cultivares": aptas,
            "observacao": "Base simplificada para protótipo (não substitui recomendação agronômica).",
        }
    )


@mcp.tool()
def validar_agrotoxicos_permitidos(cultura: str, produtos: str) -> str:
    """Valida se os produtos informados aparecem na lista simplificada de permitidos por cultura.

    Args:
        cultura: Nome da cultura (ex.: soja, milho, trigo).
        produtos: Lista separada por vírgula (ex.: "glifosato, atrazina").
    """
    cultura_norm = _normalizar(cultura)
    permitidos = [_normalizar(p) for p in PERMITIDOS_DB.get(cultura_norm, [])]

    if not permitidos:
        return _to_json({"erro": f"Cultura '{cultura}' não cadastrada na base simplificada."})

    itens = [_normalizar(item) for item in produtos.split(",") if item.strip()]
    ok = [item for item in itens if item in permitidos]
    nao_ok = [item for item in itens if item not in permitidos]

    return _to_json(
        {
            "cultura": cultura,
            "permitidos_encontrados": ok,
            "nao_encontrados_na_base": nao_ok,
            "referencia_base": PERMITIDOS_DB[cultura_norm],
            "observacao": "Validar sempre em bases oficiais (ex.: AGROFIT/MAPA) antes da decisão final.",
        }
    )

@mcp.tool()
def web_search(query: str) -> str:
    """Perform a web search using DuckDuckGo and return the top 10 results as JSON.

    Args:
        query: The search query.
    """
    try:
        results = DDGS().text(query, max_results=10)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error performing web search: {e}"
    

if __name__ == "__main__":
    mcp.run()
