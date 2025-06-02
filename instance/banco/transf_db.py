#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import sys
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vilatec.db'

db = SQLAlchemy(app)

class Obito(db.Model):

    __tablename__ = "obito"

    _id = db.Column(db.INT, primary_key=True, autoincrement=True, nullable=False)
    nome = db.Column(db.VARCHAR(200), nullable=False)
    data_sepultamento = db.Column(db.DATE, nullable=False)
    hora_sepultamento = db.Column(db.TIME, nullable=False)

    loculo = db.Column(db.INT, nullable=False)
    def __init__(self, nome, data_sepult, hora_sepult, loculo):
        self.nome = nome
        self.data_sepultamento = data_sepult
        self.hora_sepultamento = hora_sepult
        self.loculo = loculo


class Historico_Obito(db.Model):
    """

    Tabela do banco espelho da tabela 'obito', onde os registros não são apagados

    """
    __tablename__ = "historico_obito"
    _id = db.Column(db.INT, primary_key=True, autoincrement=True, nullable=False)
    loculo = db.Column(db.INT, nullable=False)
    nome = db.Column(db.VARCHAR(200), nullable=False)
    data_sepultamento = db.Column(db.DATE, nullable=False)
    hora_sepultamento = db.Column(db.TIME, nullable=False)

    def __init__(self, nome, data_sepult, hora_sepult, loculo):
        self.nome = nome
        self.data_sepultamento = data_sepult
        self.hora_sepultamento = hora_sepult
        self.loculo = loculo


origem = open(sys.argv[1], 'r')

linhas = origem.readlines()

conn = sqlite3.connect("vilatec.db")
c = conn.cursor()

for registro in linhas:
    try:
        dados = registro.split('\t')
        for i in range(len(dados)):
            dados[i] = dados[i].strip()
        if len(dados) > 2:
            data = dados[2]
            data = data[:6] + '2' + '0' + data[6:]
            dataS = ''.join(data)
            dados[2] = dataS
            dataDB = datetime.date(int(dados[2][6:]), int(dados[2][3:5]), int(dados[2][0:2]))
            hora = datetime.time(10,00)
            c = Obito(dados[1], dataDB, hora, dados[0])
            hc = Historico_Obito(dados[1], dataDB, hora, dados[0])
            db.session.add(c)
            db.session.add(hc)
            db.session.commit()
    except:
        print("Error\n")
        print(registro)
