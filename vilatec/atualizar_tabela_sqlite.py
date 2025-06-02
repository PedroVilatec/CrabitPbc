# 02_create_schema.py
import sqlite3
import datetime
import os
import sys
import time
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_ = os.path.join(ROOT_DIR,"../","instance", "banco", "vilatec.db")
DB_BKP = os.path.join(ROOT_DIR,"../", "instance", "banco", "vilatec_bkp.db")

def cria_tabela():
    conn = sqlite3.connect(DB_)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS `consumo_diario` (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            valor    REAL,
            consumo  INTEGER,
            leitura_kwh     INTEGER,
            data     DATE NOT NULL
            );
    """)

    cursor.execute("""
    INSERT INTO consumo_diario (valor, consumo,leitura_kwh, data)
    VALUES (?, ?, ?, ?)
    """,(0.00, 0, 0, datetime.datetime.now().strftime("%Y-%m-%d")))

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS `consumo_mensal` (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            tarifa REAL,
            valor  REAL,
            leitura_kwh INTEGER,
            data     DATE NOT NULL
    );
    """)

    # print('Tabela criada com sucesso.')
    cursor.execute("""
    INSERT INTO consumo_mensal (tarifa, valor, leitura_kwh, data)
    VALUES (?, ?, ?, ?)
    """, (0.54933000, 0.00, 117339, datetime.datetime.now().strftime("%Y-%m-%d")))

    cursor.execute("""
            CREATE TABLE  IF NOT EXISTS `leitura_troca_gasosa` (
            `_id` INTEGER PRIMARY KEY NOT NULL,
            `codigo_cliente` VARCHAR(20),
            `codigo_estacao` VARCHAR(20),
            `codigo_bloco`   VARCHAR(20),
            `codigo_sub_bloco`   VARCHAR(20),
            `data_leitura`    DATETIME,
            `duracao`			TIME,
            `situacao_teste`	VARCHAR(40),
            `mensagem`		VARCHAR(255),
            `fluxo_de_ar`	DECIMAL(10,4),
            `pressao`		DECIMAL(10,4),
            `temperatura_media` DECIMAL(10,4),
            `umidade` DECIMAL(10,4),
            `frequencia`		DECIMAL(10,4),
            `quantidade_sepultados` INTEGER,
            `id_integracao`		INTEGER
            );
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS `leitura_estanqueidade` (
            `_id` INTEGER PRIMARY KEY NOT NULL,
            `codigo_cliente` VARCHAR(20),
            `codigo_estacao` VARCHAR(20),
            `codigo_bloco`   VARCHAR(20),
            `codigo_sub_bloco`   VARCHAR(20),
            `data_leitura`    DATETIME,
            `duracao`			TIME,
            `situacao_teste`	VARCHAR(40),
            `mensagem`		VARCHAR(255),
            `pressao_ideal`	DECIMAL(10,4),
            `pressao_obtida`		DECIMAL(10,4),
            `valor_analogo`		DECIMAL(10,4),
                `id_integracao`		INTEGER
            );
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS `leitura_equipamento` (
            `_id` INTEGER PRIMARY KEY NOT NULL,
            `codigo_cliente` VARCHAR(20),
            `codigo_estacao` VARCHAR(20),
            `codigo_bloco`   VARCHAR(20),
            `codigo_sub_bloco`   VARCHAR(20),
            `codigo_equipamento`   VARCHAR(60),
            `data_leitura`    DATETIME,
            `duracao`			TIME,
            `situacao_teste`	VARCHAR(40),
            `mensagem`		VARCHAR(255),
            `valor`			DECIMAL(10,4),
            `indicacao`		VARCHAR(40),
                `id_integracao`		INTEGER
            );
        """)


    cursor.execute("""
            CREATE TABLE IF NOT EXISTS `leitura_operacao_equipamento` (
            `_id`                 INTEGER PRIMARY KEY NOT NULL,
            `codigo_cliente`      VARCHAR(20),
            `codigo_estacao`      VARCHAR(20),
            `codigo_equipamento`  VARCHAR(60),
            `data_leitura`        DATETIME,
            `situacao_teste`	    VARCHAR(40),
            `mensagem`		    VARCHAR(255),
            `quantidade`			INTEGER,
            `id_integracao`		INTEGER
            );
        """)
    conn.commit()

    print('Dados inseridos com sucesso.')
    conn.close()

def ler_dados():
    global DB_
    global DB_BKP
    conn = sqlite3.connect(DB_)
    cursor = conn.cursor()

    # lendo os dados
    # cursor.execute("""
    # SELECT * FROM obitos;
    # """)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    antiga = False
    for linha in cursor.fetchall():
        if 'obito' in linha:
            antiga = True
    conn.close()
    if antiga:
        os.rename(DB_ , DB_BKP)
        return True
    else:
        return False



# def altera_dados():

#         conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
#         cursor = conn.cursor()


#         # alterando os dados da tabela
#         cursor.execute("""
#         UPDATE consumo_mensal
#         SET data = ?
#         WHERE id = ?
#         """, ('2020-03-03', 1))

#         conn.commit()

#         print('Dados atualizados com sucesso.')

#         conn.close()

if ler_dados():
    cria_tabela()
else:
    print("TABELA ATUALIZADA")


