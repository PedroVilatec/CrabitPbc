import sqlite3


conn = sqlite3.connect('vilatec.db')
cursor = conn.cursor()

cursor.execute("""
        CREATE TABLE `obito` (
          `_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          `nome` VARCHAR(200) NOT NULL,
          `data_sepultamento` DATE NOT NULL,
          `hora_sepultamento` TIME NOT NULL,
          `loculo` INTEGER NOT NULL UNIQUE
        );
    """)

cursor.execute("""
        CREATE TABLE `historico_obito` (
          `_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          `nome` VARCHAR(200) NOT NULL,
          `data_sepultamento` DATE NOT NULL,
          `hora_sepultamento` TIME NOT NULL,
          `loculo` INTEGER NOT NULL
        );
    """)


cursor.execute("""
        CREATE TABLE `usuario` (
          `_id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          `nome` VARCHAR(200) NOT NULL,
          `email` VARCHAR(200) NOT NULL UNIQUE
        );
    """)

cursor.execute("""
        CREATE TABLE `sensor` (
          `_id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          `nome` VARCHAR(100) NOT NULL,
          `valor_ideal` VARCHAR(100),
          `intervalo` VARCHAR(100)
        );
    """)

cursor.execute("""
        CREATE TABLE `tipo_sensor` (
          `_id` VARCHAR(100) PRIMARY KEY NOT NULL,
          `tipo` VARCHAR(100) NOT NULL
        );
    """)

cursor.execute("""INSERT INTO `tipo_sensor` (`_id`, `tipo`) VALUES (?, ?);""", ('sensor1', 'Temperatura'))
cursor.execute("""INSERT INTO `tipo_sensor` (`_id`, `tipo`) VALUES (?, ?);""", ('sensor2', 'Umidade'))
cursor.execute("""INSERT INTO `tipo_sensor` (`_id`, `tipo`) VALUES (?, ?);""", ('sensor3', 'Pressao'))

conn.commit()

print("Tabela criada com sucesso!")

cursor.close()
conn.close()