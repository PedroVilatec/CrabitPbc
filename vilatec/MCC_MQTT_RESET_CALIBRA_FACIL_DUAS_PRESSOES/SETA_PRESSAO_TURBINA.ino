void _SET_CURVA_TURBINA_() {
  if (CHANGE_VALUE_PRESSAO.onRestart()) {
 
    if (pressao_absoluta > PRESSAO_SETADA){
      CHANGE_VALUE_PRESSAO.setTimeout(100);
      
    }
    else if (PRESSAO_SETADA > pressao_absoluta && PRESSAO_SETADA - pressao_absoluta > 50
            ) {
      CHANGE_VALUE_PRESSAO.setTimeout(300);
 
    }
    else if (PRESSAO_SETADA > pressao_absoluta && PRESSAO_SETADA - pressao_absoluta > 20 ||
        PRESSAO_SETADA < pressao_absoluta &&  pressao_absoluta - PRESSAO_SETADA > 20
       ) {
            
      CHANGE_VALUE_PRESSAO.setTimeout(500);
 
    }
    else {
      
      //CHANGE_VALUE_PRESSAO.setTimeout(3000);
//Serial.println("3000");
    }


    if (pressao_absoluta < PRESSAO_SETADA) {
      if (analog_value < 255) {
        analog_value ++;
        digitalWrite(liga_inversor, HIGH);
        analogWrite(zero_a_10v, analog_value);

      }
    }
    else {
      if (analog_value > 0) {
        analog_value --;
        digitalWrite(liga_inversor, HIGH);
        analogWrite(zero_a_10v, analog_value);

      }
    }
  }
}
