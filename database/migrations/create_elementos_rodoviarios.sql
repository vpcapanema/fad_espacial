-- Criação do schema se não existir
CREATE SCHEMA IF NOT EXISTS "Elementos_rodoviarios";

-- Tabela: trecho_rodoviario
CREATE TABLE IF NOT EXISTS "Elementos_rodoviarios".trecho_rodoviario (
    id4 SERIAL PRIMARY KEY,
    codigo VARCHAR(255) NOT NULL UNIQUE,
    denominacao VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    municipio VARCHAR(255),
    extensao_km FLOAT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: rodovia
CREATE TABLE IF NOT EXISTS "Elementos_rodoviarios".rodovia (
    id4 SERIAL PRIMARY KEY,
    codigo VARCHAR(255) NOT NULL UNIQUE,
    denominacao VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    municipio VARCHAR(255),
    extensao_km FLOAT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: obra_arte
CREATE TABLE IF NOT EXISTS "Elementos_rodoviarios".obra_arte (
    id4 SERIAL PRIMARY KEY,
    codigo VARCHAR(255) NOT NULL UNIQUE,
    denominacao VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    municipio VARCHAR(255),
    extensao_km FLOAT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: dispositivo
CREATE TABLE IF NOT EXISTS "Elementos_rodoviarios".dispositivo (
    id4 SERIAL PRIMARY KEY,
    codigo VARCHAR(255) NOT NULL UNIQUE,
    denominacao VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    municipio VARCHAR(255),
    extensao_km FLOAT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
