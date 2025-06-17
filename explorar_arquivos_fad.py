import os
from dbfread import DBF
import subprocess

# Caminhos dos arquivos
arquivos = [
    r"C:\Users\vinic\OneDrive\Imagens\Documentos\07.ARQUIVO SHAPEFILE MODELO DER 2024\arquivo_modelo_2025\arquivo_modelo_fad.dbf",
    r"C:\Users\vinic\OneDrive\Imagens\Documentos\fad_db.backup",
    r"C:\Users\vinic\OneDrive\Imagens\Documentos\fad_db.backup1",
    r"C:\Users\vinic\OneDrive\backup_POSTGRE_FAD_20250513.sql"
]

def explorar_dbf(path):
    print(f"\nExplorando DBF: {path}")
    try:
        dbf = DBF(path, encoding='latin1')
        print(f"Campos: {[field.name for field in dbf.fields]}")
        for i, record in enumerate(dbf):
            print(record)
            if i >= 4:
                print("... (mostrando apenas os 5 primeiros registros)")
                break
    except Exception as e:
        print(f"Erro ao ler DBF: {e}")

def explorar_backup_pg(path):
    print(f"\nExplorando backup PostgreSQL: {path}")
    if not os.path.exists(path):
        print("Arquivo não encontrado.")
        return
    # Tenta listar conteúdo com pg_restore
    try:
        result = subprocess.run([
            "pg_restore", "-l", path
        ], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout[:2000])  # Mostra só o início
        else:
            print(f"Erro ao executar pg_restore: {result.stderr}")
    except Exception as e:
        print(f"pg_restore não encontrado ou erro: {e}")

def explorar_sql(path):
    print(f"\nExplorando arquivo SQL: {path}")
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for i in range(20):
                print(f.readline().strip())
    except Exception as e:
        print(f"Erro ao ler SQL: {e}")

if __name__ == "__main__":
    for arquivo in arquivos:
        if arquivo.lower().endswith('.dbf'):
            explorar_dbf(arquivo)
        elif arquivo.lower().endswith('.sql'):
            explorar_sql(arquivo)
        elif arquivo.lower().endswith('.backup') or arquivo.lower().endswith('.backup1'):
            explorar_backup_pg(arquivo)
        else:
            print(f"Tipo de arquivo não reconhecido: {arquivo}")
