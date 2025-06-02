void _SET_CURVA_TURBINA_() {
  if (SET_CURVA_TURBINA == true) {
    if (CHANGE_VALUE_PRESSAO.onRestart()) {
      // Calcula a diferença de pressão em valor absoluto
      int diferenca = abs(pressao_absoluta - PRESSAO_SETADA);

      // Calcula o tempo de incremento usando a função inversamente proporcional
      if (diferenca != 0) {
        int tempo = 10000 / diferenca;
        if (tempo > 4000) tempo = 4000;
        // Define o tempo de incremento do timer usando a função setTimeout()
        CHANGE_VALUE_PRESSAO.setTimeout(tempo);
        // if (debug) Serial.println((String) "TEMPO " + tempo);
      }

      if (round(pressao_absoluta) < PRESSAO_SETADA) {
        if (analog_value < 255) {
          if(!pressao_seguranca) analog_value++;
          // digitalWrite(liga_inversor, HIGH);
          // analogWrite(zero_a_10v, analog_value);
        }

      } else if (abs(pressao_absoluta) > PRESSAO_SETADA) {
        if (analog_value > 0) {
          if(!pressao_seguranca) analog_value--;
        }
      }
    }

    if (pressao_absoluta < 5. && analog_value >= 65 && timer_protecao.isExpired()) {
      analog_value = 65;
      pressao_seguranca = true;
    }

    if (pressao_absoluta == 9999) {
      analog_value = 65;
      pressao_seguranca = true;
    }
    digitalWrite(liga_inversor, HIGH);
    analogWrite(zero_a_10v, analog_value);
  }
}
