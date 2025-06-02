
void CALCULA_PRESSAO() {
  leitura_sensor_h2s = leitura_sensor_h2s / total_leituras;
  leitura_sensor_pressao = leitura_sensor_pressao / total_leituras;
  leitura_sensor_pressao2 = leitura_sensor_pressao2 / total_leituras;
  double voltage_vcc = 5.0;
  voltage_sensor_h2s = leitura_sensor_h2s * (voltage_vcc / 1023.0);
  voltage_sensor = leitura_sensor_pressao * (voltage_vcc / 1024.0);
  voltage_sensor2 = leitura_sensor_pressao2 * (voltage_vcc / 1024.0);

  pressao1 = (leitura_sensor_pressao * ADC_mV - calibra_pressao1) / sensitivity;
  pressao2 = (leitura_sensor_pressao2 * ADC_mV - calibra_pressao2) / sensitivity;

  if (desativa_sensor_pressao_1) pressao1 = 0.0;
  if (desativa_sensor_pressao_2) pressao1 = 0.0;

  leitura_sensor_h2s = 0;
  leitura_sensor_pressao = 0;
  leitura_sensor_pressao2 = 0;



  if (isnan(pressao1) && !isnan(pressao2)) {
    //pressao1 = pressao2;
    pressao_absoluta = pressao2;
    debug = true;
  } else if (isnan(pressao2) && !isnan(pressao1)) {
    //pressao1 = pressao2;
    pressao_absoluta = pressao1;
    debug = true;
  } else {
    //pressao1 = pressao2;
    // int pressao_instantanea = (pressao1 + pressao2) / 2;
    pressao_absoluta = (pressao1 + pressao2) / 2;
    // pressureController.updatePressure(pressao_instantanea);
    
//     if(millis()/1000 > WINDOW_SIZE + 2) pressao_absoluta = pressureController.getSmoothPressure();//dalay para somatizar as médias de pressão no início do sistema
// else{
//   pressao_absoluta = pressao_instantanea;
// }
    

    //###  SE A DIFERENÇA DE LEITURA DOS SENSORES FOR MAIOR QUE 50 O VALOR É SETADO PARA 999 ##########################

    if (pressao1 - pressao2 > 50) {
      pressao_absoluta = 9999;
    }
    if (pressao2 - pressao1 > 50) {
      pressao_absoluta = 9999;
    }
  }
  // if (pressao_absoluta < 2) {
  //   pressao_absoluta = 0;
  // }
}


// Convert normal decimal numbers to binary coded decimal
// Convert normal decimal numbers to binary coded decimal
byte decToBcd(byte val) {
  return ((val / 10 * 16) + (val % 10));
}

boolean aprovaString(String x) {
  for (byte i = 0; i < x.length(); i++) {
    if (!isdigit(x.charAt(i))) {
      return 0;
    }
  }
  return 1;
}
