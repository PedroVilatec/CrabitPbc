void setup() {
  //   emon1.voltage(5, VOLT_CAL, 1.7); //PASSA PARA A FUNÇÃO OS PARÂMETROS (PINO ANALÓGIO / VALOR DE CALIBRAÇÃO / MUDANÇA DE FASE)
  //Pino, calibracao - Cur Const= Ratio/BurdenR. 1800/62 = 29.
  //  emon1.current(pino_sct, 30);
  dht.begin();
  Serial.begin(9600);
  pinMode(9, INPUT);
  pinMode(10, INPUT);
  pinMode(11, INPUT);
  pinMode(12, INPUT);
  pinMode(feedbackH2S, INPUT);
  pinMode(ret_inversor_ok, INPUT);
  pinMode(ligaH2S, OUTPUT);
  pinMode(bomba_dagua, OUTPUT);
  pinMode(peristaltica_in, OUTPUT);
  pinMode(peristaltica_out, OUTPUT);
  pinMode(reset_inversor, OUTPUT);
  pinMode(liga_inversor, OUTPUT);
  pinMode(reset_12v, OUTPUT);
  digitalWrite(bomba_dagua, LOW);
  digitalWrite(peristaltica_in, LOW);
  digitalWrite(peristaltica_out, LOW);
  digitalWrite(reset_inversor, LOW);
  digitalWrite(liga_inversor, LOW);
  digitalWrite(reset_12v, LOW);
  digitalWrite(ligaH2S, LOW);
  analog_value = 0;
  analogWrite(zero_a_10v, analog_value);
  calibra_pressao1 = EEPROM.readFloat(20);
  calibra_pressao2 = EEPROM.readFloat(30);
  delay_read_sensors.setTimeout(1);
  delay_liga_turbina.setTimeout(5000);
  hora_troca = EEPROM.readInt(100);
  minutos_troca = EEPROM.readInt(110);
  
  /********************************* SETUP CONTAGEM REGRESSIVA *******************************/
  delay_regressiva.setTimeout(intervalo_delay_regressiva);
  delay_bombaDagua.setTimeout(3000);
  timer_reset12v.setTimeout(3000);
  timer_resetInversor.setTimeout(40000);
  CHANGE_VALUE_PRESSAO.setTimeout(300);
  timer_protecao.setTimeout(10000);
  timer_temp_humidade.setTimeout(2000);
  envio_serial.setTimeout(500);
  if (button.onPressed()) {
  }
  if (button.onReleased()) {
  }
}
