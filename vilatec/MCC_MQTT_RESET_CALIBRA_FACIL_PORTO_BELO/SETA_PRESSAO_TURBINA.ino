void _SET_CURVA_TURBINA_() {
  if (CHANGE_VALUE_PRESSAO.onRestart()) {

    // Calcula a diferença de pressão em valor absoluto
    int diferenca = abs(pressao_absoluta - PRESSAO_SETADA);

    // Calcula o tempo de incremento usando a função inversamente proporcional
    if (diferenca != 0) {
      int tempo = 10000 / diferenca;
      if (tempo > 2000) tempo = 2000;
      // Define o tempo de incremento do timer usando a função setTimeout()
      CHANGE_VALUE_PRESSAO.setTimeout(tempo);
      if (debug) Serial.println((String) "TEMPO " + tempo);
    }

    if (round(pressao_absoluta) < PRESSAO_SETADA) {
      if (analog_value < 255) {
        analog_value++;
        digitalWrite(liga_inversor, HIGH);
        analogWrite(zero_a_10v, analog_value);
      }
    } else if (round(pressao_absoluta) > PRESSAO_SETADA){
      if (analog_value > 0) {
        analog_value--;
        digitalWrite(liga_inversor, HIGH);
        analogWrite(zero_a_10v, analog_value);
      }
    }
  }
}
