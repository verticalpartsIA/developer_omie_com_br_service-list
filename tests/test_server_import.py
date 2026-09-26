def test_server_importa_sem_erro():
    import omie_mcp.server as server

    assert server.mcp is not None
