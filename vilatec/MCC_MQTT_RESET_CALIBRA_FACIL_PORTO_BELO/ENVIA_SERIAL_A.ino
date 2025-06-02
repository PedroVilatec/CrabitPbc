void ENVIA_SERIAL_A() {
String status_inversor = "";
double x = map(analog_value, 0, 255 , 0, 66);

  if (digitalRead(ret_inversor_ok) == LOW) {
    status_inversor = "INV_OK";
  }
  else {
    status_inversor = "INV_FAIL";
  }
  String status_h2s = "";
  if (digitalRead(ligaH2S) == HIGH) {
    if (digitalRead(feedbackH2S) == LOW) {
      status_h2s = "H2S_Ok "+String(voltage_sensor_h2s);
    }
    else {
      status_h2s = "H2S_Err "+String(voltage_sensor_h2s);
    }
  }
  else {
    status_h2s = "H2S Off";
  }
  String status_reset_inv = "";
    if (digitalRead(reset_inversor) == LOW) {
    status_reset_inv = "RST_INV:ON";
  }
  else {
    status_reset_inv = "RST_INV:OFF";
  }
  String status_reset_12v = "12v:";
  if (digitalRead(reset_12v) == LOW) {
    status_reset_12v += "ON";
  }
  else {
    status_reset_12v += "OFF";
  }
  String status_bomba = "BOMBA:";
  if (digitalRead(bomba_dagua) == LOW) {
    status_bomba += "OFF";
  }
  else {
    status_bomba += "ON";
  }
  String an_value =(String) "AnVal:"+ analog_value;
  //(TEMPERATURA,UMIDADE, PRESSAO ,FREQUENCIA, RET_INV_OK,RET_PRESSOSTATO, DATA, CONTAGEM TEMPO TESTE)
  comando_serial = (String)"<"+temperatura+","+umidade+","+round(pressao_absoluta)+","+x+","+status_inversor+","+
  status_h2s+","+status_reset_inv+","+status_reset_12v+","+status_bomba+","+an_value+">";

  Serial.println(comando_serial);


}
