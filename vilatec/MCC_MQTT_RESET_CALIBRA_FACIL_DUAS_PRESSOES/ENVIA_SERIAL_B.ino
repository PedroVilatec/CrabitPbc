//##########################-INÍCIO DA LEITURA DO SENSOR DE UMIDADE E TEMPERATURA-##########################
void ENVIA_SERIAL_B() {
  umidade = dht.readHumidity();
  temperatura = dht.readTemperature();
if(debug){
  b = random(46.9, 48.9);
  c = random(45.9, 47.9);
  d = random(0, 100);
  //  Serial.println();
  Serial.print("CALIB_MPX_A: ");
  Serial.println(calibra_pressao1, 4);
  Serial.print("CALIB_MPX_B: ");
  Serial.println(calibra_pressao2, 4);


  Serial.print("S_PRESS 1: ");
  Serial.print(pressao1);
  Serial.print(" - ");
  Serial.print("S_PRESS 2: ");
  Serial.println(pressao2);
  //  Serial.println(" - T_SEP: " + String(EEPROM.readInt(300)));
  //  Serial.println();


  //  Read temperature as Fahrenheit
  //float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  //if (isnan(umidade) || isnan(temperatura) || isnan(f)) {
  //  if (isnan(umidade)) {
  // d = d / 300;
  // b = b + d;
  //    c = c + d;
  //
  //   umidade = (b + c) / 2;
  //  }

  //  if (isnan(temperatura)) {
  //  temperatura =
  //  }
}
}
