import os
import json
import atributos
locals().update(atributos.disp)
class Devices():
    CONTROLADORES = {
# "ARDUINO":json.loads(arduino),

# "EVAPORADOR_CABINE":json.loads(evaporadora_sem_valvula),
# "VALVULA_CABINE":json.loads(valvula_cabine),
# "VALVULA_CABINE_2":json.loads(valvula_cabine),
# "VALVULA_CABINE_3":json.loads(valvula_cabine),
# "VALVULA_CABINE_4":json.loads(valvula_cabine),
# "VALVULA_CABINE_5":json.loads(valvula_cabine),
# "VALVULA_CABINE_6":json.loads(valvula_cabine),
# "VALVULA_CABINE_7":json.loads(valvula_cabine),
# "ACESSO_ETEN":json.loads(acesso_eten),
# "ACESSO_ETEN_1":json.loads(acesso_eten),
# "BOMBA":json.loads(bomba),
# "VALVULA_AM_1EA":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AM_1EB":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AM_1EC":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AM_1ED":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AM_1EE":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AM_1EF":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AM_1EG":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AM_1EH":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AM_1EI":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AM_1EJ":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AM_1EK":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AM_1EL":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AM_1EM":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AM_1EN":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AM_BY":json.loads(valvula_simples),

# "VALVULA_AZ_1EA":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AZ_1EB":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_001", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AZ_1EC":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AZ_1ED":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_002", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AZ_1EE":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AZ_1EF":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_003", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AZ_1EG":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AZ_1EH":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_007", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AZ_1EI":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AZ_1EJ":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_008", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AZ_1EK":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AZ_1EL":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_009", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AZ_1EM":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_PAR"}},
# "VALVULA_AZ_1EN":{**json.loads(valvula_simples), **{"COD_BLOCO":"BL_010", "COD_SUB_BLOCO":"SUB_IMPAR"}},
# "VALVULA_AZ_BY":json.loads(valvula_simples),


# "EVAPORADOR_1EAB":json.loads(evaporadora),
# "EVAPORADOR_1ECD":json.loads(evaporadora),
# "EVAPORADOR_1EEF":json.loads(evaporadora),
# "EVAPORADOR_1EIJ":json.loads(evaporadora),
# "EVAPORADOR_1EKL":json.loads(evaporadora),
# "EVAPORADOR_1EGH":json.loads(evaporadora),
# "EVAPORADOR_1EMN":json.loads(evaporadora)

}
