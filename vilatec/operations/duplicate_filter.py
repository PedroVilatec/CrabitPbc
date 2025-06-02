import logging
class FiltraDuplicidade(logging.Filter):
	def __init__(self):
		self.last_log = None

	def filtro(self, record):
		"""
		Retorna True se a mensagem de registro é diferente da última mensagem de registro.
		"""
		current_log = record.getMessage()
		if current_log != self.last_log:
			self.last_log = current_log
			return True
		else:
			return False