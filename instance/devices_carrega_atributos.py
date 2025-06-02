import json
class Devices:
	def __init__(self, **kwargs):
		self.kwargs = kwargs
		self.CONTROLADORES = {
					"ARDUINO": self.carrega('arduino'),
					"EVAPORADOR_CABINE_2":self.carrega('evaporador_cabine_nivel_eten'),
					"BOMBA":self.carrega('bomba'),
					"VALVULA_CABINE_1":self.carrega('valvula_cabine'),
					"ACESSO_ETEN":self.carrega('acesso_eten'),
					"679EE0_BOMBA":self.carrega('bomba'),
					#~ "COMANDOS":{"ABRE TODAS":"", "FECHA TODAS":"", "ABRE_AMARELA":"", "FECHA AMARELA":"", "ABRE AZUL":"", "FECHA AZUL":"" , "ABRE CABINE":"", "FECHA CABINE":"", "STATUS":""} ,
					"VALVULA_AM_ESQ":{**self.carrega('valvula_simples'), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_001"}},
					"VALVULA_AM_DIR":{**self.carrega('valvula_simples'), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_001"}},
					"VALVULA_AZ_DIR":{**self.carrega('valvula_simples'), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_001"}},
					"VALVULA_AZ_ESQ":{**self.carrega('valvula_simples'), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_001"}},
					"VALVULA_AZ_2":{**self.carrega('valvula_simples'), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_001"}},
				}

	def carrega(self, key):
		return json.loads(json.dumps(self.kwargs[key]))
