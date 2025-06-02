void TESTE_PRESSAO() {
 
  /***************ATUALIZA O VALOR DA PRESSAO, E SETA O CONTADOR PARA MILLIS()***/

  
  
  if (libera_teste_pressao)
   {
    if (pressao_mais_alta > pressao_mais_alta_anterior) {
    pressao_mais_alta_anterior = pressao_mais_alta;
    millis_teste_pressao = millis();
  }
    libera_troca = false;
    digitalWrite(reset_inversor, LOW);
    digitalWrite(bomba_dagua, LOW);
    digitalWrite(liga_inversor, HIGH);
    if (CHANGE_VALUE_PRESSAO.onRestart()) {
      if (analog_value < analog_received) {
        analog_value ++;
      }
    }

    analogWrite(zero_a_10v, analog_value);

    if (pressao_mais_alta >= pressao_ideal_teste) {
      digitalWrite(liga_inversor, LOW);
      analog_value = 0;      
      analogWrite(zero_a_10v, analog_value);
      Serial.println("(T. E. realizado com sucesso!!)");
      Serial.println("[media,teste," + String(pressao_mais_alta) + "]");
      delay(2000);
      Serial.println("()");
      libera_teste_pressao = false;
      pressao_mais_alta = 0;
      pressao_mais_alta_anterior = 0;
    }
    /***************FUNÇÃO QUE ENCERRA O TESTE DE ESTANQUEIDADE SE A PRESSAO NÃO SE ESTABILIZAR PELO PERÍODO DETERMINADO***/
    MILLIS = millis();
    //Serial.println((MILLIS - millis_teste_pressao)/1000);
    //Serial.println(tempo_alarme_teste_pressao);
    //if ((MILLIS - millis_teste_pressao > tempo_alarme_teste_pressao)) {
    if ((MILLIS - millis_teste_pressao > 65000)) {
      if (EEPROM.read(70) == 1) {
        digitalWrite(liga_inversor, LOW);
        analog_value = 0;
        analogWrite(zero_a_10v, analog_value);
        if (pressao_mais_alta >= pressao_ideal_teste - 3) {
          digitalWrite(liga_inversor, LOW);
          analog_value = 0;
          analogWrite(zero_a_10v, analog_value);
          Serial.println("(T. E. realizado com sucesso!!)");
          delay(2000);
          Serial.println("(Dentro da margem de tolerância)");
          delay(2000);
          Serial.println("[media,teste," + String(pressao_mais_alta) + "]");
          delay(2000);
          Serial.println("()");
          libera_teste_pressao = false;
          pressao_mais_alta_anterior = 0;
        }
        else {
          digitalWrite(liga_inversor, LOW);
          analog_value = 0;
          analogWrite(zero_a_10v, analog_value);
          Serial.println("(Problema de estanqueidade!!)");
          Serial.println("[media,teste," + String(pressao_mais_alta) + "]");
          delay(2000);
          Serial.println("()");
          libera_teste_pressao = false;
          pressao_mais_alta = 0;
          pressao_mais_alta_anterior = 0;
        }
      }
      else {
        EEPROM.write(41, pressao_mais_alta); // GRAVA O VALOR DA PRESSÃO OBTIDA PARA OS PROXIMOS TESTES
        pressao_ideal_teste = pressao_mais_alta;
        EEPROM.write(70, 1); //ENQUANTO EEPROM 43 = 1, PRESSÃO IDEAL TESTE ESTARÁ SETADA, CASO PRECISE MUDAR, GRAVA EEPROM 43 = 0, E REINICIA O MICRO.
        digitalWrite(liga_inversor, LOW);
        analog_value = 0;
        analogWrite(zero_a_10v, analog_value);
        libera_teste_pressao = false;
        Serial.println("(Pressão máxima obtida: " + String(pressao_mais_alta) + ")");
        delay(2000);
        Serial.println("( )");
        pressao_mais_alta = 0;
        pressao_mais_alta_anterior = 0;
      }

    }
  }
  
 
}
