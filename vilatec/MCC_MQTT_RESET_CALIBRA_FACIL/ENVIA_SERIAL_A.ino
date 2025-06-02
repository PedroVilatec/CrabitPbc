void ENVIA_SERIAL_A() {
  String status_inversor = "";
  double x = map(analog_value, 0, 255, 0, 66);

  if (digitalRead(ret_inversor_ok) == LOW) {
    status_inversor = "INV_OK";
  } else {
    status_inversor = "INV_FAIL";
  }
  String status_h2s = "";
  if (digitalRead(ligaH2S) == HIGH) {
    if (digitalRead(feedbackH2S) == LOW) {
      status_h2s = "H2S_Ok " + String(voltage_sensor_h2s);
    } else {
      status_h2s = "H2S_Err " + String(voltage_sensor_h2s);
    }
  } else {
    status_h2s = "H2S Off";
  }
  String status_reset_inv = "";
  if (digitalRead(reset_inversor) == LOW) {
    status_reset_inv = "RST_INV:ON";
  } else {
    status_reset_inv = "RST_INV:OFF";
  }
  String status_reset_12v = "12v:";
  if (digitalRead(reset_12v) == LOW) {
    status_reset_12v += "ON";
  } else {
    status_reset_12v += "OFF";
  }
  String status_bomba = "BOMBA:";
  if (digitalRead(bomba_dagua) == LOW) {
    status_bomba += "OFF";
  } else {
    status_bomba += "ON";
  }
  String an_value = (String) "AnVal:" + analog_value;
  //(TEMPERATURA,UMIDADE, PRESSAO ,FREQUENCIA, RET_INV_OK,RET_PRESSOSTATO, DATA, CONTAGEM TEMPO TESTE)
  comando_serial = "<";
    comando_serial.concat(String(temperatura));
    comando_serial.concat(", " + String(umidade));
    comando_serial.concat(", " + String(pressao_absoluta));
    comando_serial.concat(", " + String(x));
    comando_serial.concat(", " + String(status_inversor));
    comando_serial.concat(", " + String(status_h2s));
    comando_serial.concat(", " + String(status_reset_inv));
    comando_serial.concat(", " + String(status_reset_12v));
    comando_serial.concat(", " + String(status_bomba));
    comando_serial.concat(", " + String(an_value));
  if (pressao_seguranca && SET_CURVA_TURBINA) {
    comando_serial.concat(", PSEG");
  }
  if (calibra_pressao1 < 100. || calibra_pressao1 > 300.) {
    comando_serial.concat(", CSP1 " + String(calibra_pressao1));
    calibrar1 = true;
  }
  else{
    calibrar1 = false;
  }
  if (calibra_pressao2 < 100. || calibra_pressao2 > 300.) {
    comando_serial.concat(", SCP2 " + String(calibra_pressao1));
    calibrar2 = true;
  }
  else{
    calibrar2 = false;
  }
  comando_serial.concat(", "+ String(VERSAO));
  comando_serial.concat(">");
  Serial.println(comando_serial);
}
