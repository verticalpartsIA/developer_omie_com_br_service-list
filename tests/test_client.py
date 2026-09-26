import pytest

from omie_mcp.client import OmieClient, OmieError


def test_normalize_relative_endpoint():
    assert OmieClient.normalize_endpoint("geral/clientes").endswith("/api/v1/geral/clientes/")


def test_reject_external_endpoint():
    with pytest.raises(OmieError):
        OmieClient.normalize_endpoint("https://example.com/api/v1/geral/clientes/")


@pytest.mark.parametrize(
    "call",
    [
        "ListarClientes",
        "ConsultarCliente",
        "ObterDocumento",
        "PesquisarTitulos",
        "ResumoFinancas",
        "BuscarAlgo",
    ],
)
def test_read_call_detection(call):
    assert OmieClient.is_read_call(call) is True


@pytest.mark.parametrize(
    "call",
    [
        "IncluirCliente",
        "AlterarCliente",
        "ExcluirCliente",
        "CancelarBoleto",
        "FaturarPedido",
    ],
)
def test_write_call_detection(call):
    assert OmieClient.is_read_call(call) is False


def test_read_cache_returns_copy():
    cli = OmieClient()
    cli._set_cached("abc", {"cadastros": [{"codigo": 1}]})
    primeiro = cli._get_cached("abc")
    assert primeiro == {"cadastros": [{"codigo": 1}]}
    primeiro["cadastros"][0]["codigo"] = 99
    segundo = cli._get_cached("abc")
    assert segundo["cadastros"][0]["codigo"] == 1


def test_redundant_fault_detection():
    assert OmieClient._is_redundant_fault("Consumo redundante detectado") is True
    assert OmieClient._is_redundant_fault("Falha de validação") is False
