# 02_create_schema.py
import sqlite3
import datetime
import os
import sys

if os.path.exists('/home/pi/Crabit/instance/banco/vilatec.db_bkp'):
    escolha = input("Deseja restaurar o banco atual? (s/n)")
    if escolha == 's' or escolha == 'S':
        os.system('cp /home/pi/Crabit/instance/banco/vilatec.db_bkp /home/pi/Crabit/instance/banco/vilatec.db')
    else:
        print("Nada foi alterado!")
        sys.exit()
        
else:
    os.system('cp /home/pi/Crabit/instance/banco/vilatec.db /home/pi/Crabit/instance/banco/vilatec.db_bkp')
# conectando...
def cria_tabela():
    conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE consumo_diario (
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
    CREATE TABLE consumo_mensal (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            tarifa REAL,
            valor  REAL,
            leitura_kwh INTEGER,
            data     DATE NOT NULL
    );
    """)
    
    print('Tabela criada com sucesso.')
    cursor.execute("""
    INSERT INTO consumo_mensal (tarifa, valor, leitura_kwh, data)
    VALUES (?, ?, ?, ?)
    """, (0.54933000, 0.00, 117339, datetime.datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    
    print('Dados inseridos com sucesso.')
    conn.close()
        
def ler_dados():
    conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
    cursor = conn.cursor()
    
    # lendo os dados
    cursor.execute("""
    SELECT * FROM consumo_diario;
    """)
    
    for linha in cursor.fetchall():
        print(linha)
    
    conn.close()

def altera_dados():

        conn = sqlite3.connect('/home/pi/Crabit/instance/banco/vilatec.db')
        cursor = conn.cursor()
        
        
        # alterando os dados da tabela
        cursor.execute("""
        UPDATE consumo_mensal
        SET data = ? 
        WHERE id = ?
        """, ('2020-03-03', 1))
        
        conn.commit()
        
        print('Dados atualizados com sucesso.')
        
        conn.close()
        
#~ ler_dados()
cria_tabela()
