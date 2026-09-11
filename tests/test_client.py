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
