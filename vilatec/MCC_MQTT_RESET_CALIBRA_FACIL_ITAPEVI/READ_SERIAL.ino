void READ_SERIAL() {
  while (Serial.available() > 0) {
    char character = Serial.read();
    Data.concat(character);
    delay(1);
    if ((character == '\n') || (character == '\r')) {
      Data.toUpperCase();
      processaString(Data);
      Data = "";
    }
  }
}

void processaString(String data){
      if (data.indexOf("LH2S") == 0) {
        byte index1 = data.indexOf(',');
        byte value = data.substring(index1 + 1, data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);
        digitalWrite(ligaH2S, value);
        Serial.println(digitalRead(ligaH2S));
        delay(2000);
      }
      if (data.indexOf("DEBUG") == 0) {
        debug = !debug;
      }
      if (data.indexOf("DESP1") == 0) {
        desativa_sensor_pressao_1 = true;
        Serial.println("DESP1");
      }
      if (data.indexOf("ATVP1") == 0) {
        desativa_sensor_pressao_1 = false;
        Serial.println("ATVP1");
      }
      if (data.indexOf("ATVP2") == 0) {
        desativa_sensor_pressao_2 = false;
        Serial.println("ATVP2");
      }
      if (data.indexOf("DESP2") == 0) {
        desativa_sensor_pressao_2 = true;
        Serial.println("DESP2");
      }
      if (data.indexOf("CSP") > -1) {
        calibra_pressao1 = voltage_sensor * 1000;
        calibra_pressao2 = voltage_sensor2 * 1000;
        EEPROM.writeFloat(20, calibra_pressao1);
        EEPROM.writeFloat(30, calibra_pressao2);
      }
      if (data.indexOf("RESET_INV") == 0) {
        byte index1 = data.indexOf(',');
        unsigned long segundos = data.substring(index1 + 1, data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);

        Serial.print("RESET INVERSOR POR ");
        Serial.print(segundos);
        Serial.println(" SEGUNDOS");
        timer_resetInversor.setTimeout(data.substring(index1 + 1, data.length() - 1).toInt() * 1000);
        timer_resetInversor.stop();
        timer_resetInversor.restart();
        digitalWrite(reset_inversor, HIGH);
        Serial.println(timer_resetInversor.getTimeout());
      }

      if (data.indexOf("RESET_12V") == 0) {
        byte index1 = data.indexOf(',');
        unsigned long segundos = data.substring(index1 + 1, data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);
        digitalWrite(reset_12v, HIGH);
        Serial.print("RESET 12V POR ");
        Serial.print(segundos);
        Serial.println(" SEGUNDOS");
        timer_reset12v.setTimeout(segundos * 1000);
        timer_reset12v.restart();
      }



      if (data.indexOf("BOMBA") == 0) {
        byte index1 = data.indexOf(',');
        unsigned long segundos = data.substring(index1 + 1, data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);
        digitalWrite(bomba_dagua, HIGH);
        Serial.print("LIGA BOMBA ");
        Serial.print(segundos);
        Serial.println(" SEGUNDOS");
        delay_bombaDagua.setTimeout(segundos * 1000);
        delay_bombaDagua.restart();
      }

      if (data.indexOf("TURBINA") == 0) {
        if (pressao_seguranca){
          Serial.println("PRESSAO DE SEGURANÇA ATIVADO");
          return;
        }        
        if (calibrar1 || calibrar2) {
          Serial.println("CALIBRAR SENSORES DE PRESSÃO");
          return;
        }
        byte index1 = data.indexOf(',');


        //if (data.substring(index1 + 1, data.length() - 1).toInt() < 256);
        int estado = data.substring(index1 + 1, data.length() - 1).toInt();
        estado = constrain(estado, 0, 255);
        SET_CURVA_TURBINA = false;
        analog_value = estado;
        analogWrite(zero_a_10v, estado);
        digitalWrite(liga_inversor, HIGH);
      }


      if (data.substring(0, 4) == "STOP") {
        SET_CURVA_TURBINA = false;
        analog_value = 0;
        pressao_seguranca = false;
        digitalWrite(liga_inversor, LOW);
        analogWrite(zero_a_10v, analog_value);
        digitalWrite(bomba_dagua, LOW);
        timer_protecao.stop();
      }

      if (data.indexOf("SCT") == 0) {
        if (pressao_seguranca){
          return;
        }
        if (calibrar1 || calibrar2) {
          Serial.println("CALIBRAR SENSORES DE PRESSÃO");
          return;
        }
        byte index1 = data.indexOf(',');
        int value = data.substring(index1 + 1, data.length() - 1).toInt();
        value = constrain(value, 0, 255);
        if (value > 0) {
          PRESSAO_SETADA = value;
          digitalWrite(liga_inversor, HIGH);

          if (SET_CURVA_TURBINA == false) {
            analog_value = 200;
            int x = map(PRESSAO_SETADA + 50, 0, 1024, 0, 255);
            analog_value = constrain(x, 0, 255);
            pressao_anterior = pressao_absoluta;
          }
          SET_CURVA_TURBINA = true;
          pressao_seguranca = false;
          timer_protecao.setTimeout(10000);
          if (! timer_protecao.isActive())timer_protecao.restart();
        } else {
          digitalWrite(liga_inversor, LOW);
          analog_value = 0;
          analogWrite(zero_a_10v, analog_value);
          SET_CURVA_TURBINA = false;
        }
      }


      if (data.substring(0, 4) == "P_IN") {
        if (data.substring(5, 6) == "1") {
          Serial.println("P_IN LIGADO");
          digitalWrite(peristaltica_out, LOW);
          delay(500);
          digitalWrite(peristaltica_in, HIGH);
        }
        if (data.substring(5, 6) == "0") {
          Serial.println("P_IN DESLIGADO");

          digitalWrite(peristaltica_in, LOW);
        }
      }


      if (data.substring(0, 5) == "T_SEP") {
        int total = data.substring(6, 11).toInt();
        if (total > 0) {
          EEPROM.writeInt(300, total);
        }
        Serial.println(EEPROM.readInt(300));
      }

      if (data.substring(0, 6) == "EEPROM") {

        Serial.println();
        Serial.print(EEPROM.readByte(0));
        Serial.print("\t");
        Serial.print(EEPROM.readByte(10));
        Serial.print("\t");
        Serial.print(EEPROM.readFloat(20));
        Serial.print("\t");
        Serial.print(EEPROM.readFloat(30));
        Serial.print("\t");
        Serial.print(EEPROM.readByte(40));
        Serial.print("\t");
        Serial.print(EEPROM.readInt(50));
        Serial.print("\t");
        Serial.print(EEPROM.readInt(60));
        Serial.print("\t");
        Serial.print(EEPROM.readByte(70));
        Serial.print("\t");
        Serial.print(EEPROM.readInt(80));
        Serial.print("\t");
        Serial.print(EEPROM.readInt(90));
        Serial.print("\t");
        Serial.print(EEPROM.readInt(100));
        Serial.print("\t");
        Serial.println(EEPROM.readInt(110));

        Serial.println();
      }

      if (data.substring(0, 5) == "P_OUT") {
        if (data.substring(6, 7) == "1") {
          Serial.println("P_OUT LIGADO");
          digitalWrite(peristaltica_in, LOW);
          delay(500);
          digitalWrite(peristaltica_out, HIGH);
        }
        if (data.substring(6, 7) == "0") {
          Serial.println("P_OUT DESLIGADO");
          digitalWrite(peristaltica_out, LOW);
        }
      }
    }

