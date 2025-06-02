void loop() {
  if (delay_bombaDagua.onRestart()) {
    digitalWrite(bomba_dagua, LOW);
  }
  if (timer_reset12v.onRestart()) {
    digitalWrite(reset_12v, LOW);
  }
  if (timer_resetInversor.onRestart()) {
    digitalWrite(reset_inversor, LOW);
  }

  //   Serial.print("H2S:");
  // Serial.print(MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_H2S) );
  //  Serial.println( "ppm" );
  //##########################-INÍCIO DA LEITURA DOS SENSORES DE PRESSÃO-##########################
  if (SET_CURVA_TURBINA == true) {
    _SET_CURVA_TURBINA_();
  }
  READ_SERIAL();


  if (button.onPressed()) {
    millisButton = millis();
    Serial.println("LIGA_TELA");
  }

  if (button.onReleased()) {
    if (millis() - millisButton > 3000) {
      Serial.println("TESTE_PRESSAO");
    } else {
      Serial.println("TROCA_GASOSA");
    }
  }

  if (envio_serial.onRestart()) {  //chama função a cada 500 milissegundos
    ENVIA_SERIAL_A();
  }
  if (delay_read_sensors.onRestart()) {  //chama função a cada 5 milissegundos
    leitura_sensor_h2s += analogRead(A3);
    leitura_sensor_pressao += analogRead(A6);
    leitura_sensor_pressao2 += analogRead(A7);
    total_leituras++;
    if (total_leituras >= 100) {  // CHAMADA A CADA 500 MILISSEGUNDOS

      CALCULA_PRESSAO();

      total_leituras = 1;
    }
    delay_humid_e_temp++;
    if (delay_humid_e_temp > 599) {
      ENVIA_SERIAL_B();
      delay_humid_e_temp = 0;
    }
  }
}
