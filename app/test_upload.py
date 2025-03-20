import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.database.session import Base
from app.models.validacao import ArquivoZip

# Configuração de um banco de dados temporário para testes
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Criar um banco de dados limpo antes dos testes
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=test_engine)  # Cria as tabelas para o teste
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)  # Remove tabelas após os testes

# Cliente de teste para a API
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

# Teste de upload de arquivo ZIP
def test_upload_zip(client, test_db):
    # Simula um arquivo ZIP
    file_content = b"conteudo_simulado_do_zip"
    files = {"arquivo": ("test.zip", file_content, "application/zip")}

    # Faz a requisição POST para o endpoint de upload
    response = client.post("/validacao/upload/", files=files)

    # Verifica se o upload foi bem-sucedido
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Arquivo importado com sucesso!", "sucesso": True}

    # Verifica se o arquivo foi salvo no banco de dados de teste
    db = TestingSessionLocal()
    arquivo_salvo = db.query(ArquivoZip).filter(ArquivoZip.nome_arquivo == "test.zip").first()
    assert arquivo_salvo is not None
    assert arquivo_salvo.dados == file_content
    db.close()

# Teste de upload de arquivo não ZIP
def test_upload_not_zip(client):
    # Simula um arquivo que não é ZIP
    file_content = b"conteudo_simulado"
    files = {"arquivo": ("test.txt", file_content, "text/plain")}

    # Faz a requisição POST para o endpoint de upload
    response = client.post("/validacao/upload/", files=files)

    # Verifica se o upload foi rejeitado corretamente
    assert response.status_code == 400
    assert response.json() == {"detail": "O arquivo deve ser um ZIP."}
