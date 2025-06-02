void READ_SERIAL() {
  while (Serial.available() > 0) {
    char character = Serial.read();
    Data.concat(character);
    delay(1);
    if ((character == '\n') || (character == '\r')) {
      Data.toUpperCase();

      if (Data.indexOf("LH2S") == 0)
      {
        byte index1 = Data.indexOf(',');
        byte value = Data.substring(index1 + 1, Data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);
        digitalWrite(ligaH2S, value);
        Serial.println(digitalRead(ligaH2S));
        delay(2000);

      }
      if (Data.indexOf("DEBUG") == 0)
      {
        debug = !debug;
      }
      if (Data.indexOf("CSP") > -1 ) {
        calibra_pressao1 = voltage_sensor * 1000;
        calibra_pressao2 = voltage_sensor2 * 1000;
        EEPROM.writeFloat(20, calibra_pressao1);
        EEPROM.writeFloat(30, calibra_pressao2);
      }
      if (Data.indexOf("RESET_INV") == 0)
      {
        byte index1 = Data.indexOf(',');
        unsigned long segundos = Data.substring(index1 + 1, Data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);

        Serial.print("RESET INVERSOR POR ");
        Serial.print(segundos);
        Serial.println(" SEGUNDOS");
        timer_resetInversor.setTimeout(Data.substring(index1 + 1, Data.length() - 1).toInt() * 1000);
        timer_resetInversor.stop();
        timer_resetInversor.restart();
        digitalWrite(reset_inversor, HIGH);
        Serial.println(timer_resetInversor.getTimeout());

      }

      if (Data.indexOf("RESET_12V") == 0)
      {
        byte index1 = Data.indexOf(',');
        unsigned long segundos = Data.substring(index1 + 1, Data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);
        digitalWrite(reset_12v, HIGH);
        Serial.print("RESET 12V POR ");
        Serial.print(segundos);
        Serial.println(" SEGUNDOS");
        timer_reset12v.setTimeout(segundos * 1000);
        timer_reset12v.restart();


      }



      if (Data.indexOf("BOMBA") == 0)
      {
        byte index1 = Data.indexOf(',');
        unsigned long segundos = Data.substring(index1 + 1, Data.length() - 1).toInt();
        //Serial.println(value);
        //Serial.println(value2);
        digitalWrite(bomba_dagua, HIGH);
        Serial.print("LIGA BOMBA ");
        Serial.print(segundos);
        Serial.println(" SEGUNDOS");
        delay_bombaDagua.setTimeout(segundos * 1000);
        delay_bombaDagua.restart();
      }

      if (Data.indexOf("TURBINA") == 0)
      {
        byte index1 = Data.indexOf(',');


        //if (Data.substring(index1 + 1, Data.length() - 1).toInt() < 256);
        int estado = Data.substring(index1 + 1, Data.length() - 1).toInt();
        estado = constrain(estado, 0, 255);
        SET_CURVA_TURBINA = false;
        analog_value = estado;
        analogWrite(zero_a_10v, estado);
        digitalWrite(liga_inversor, HIGH);

      }


      if (Data.substring(0, 4) == "STOP") {
        SET_CURVA_TURBINA = false;
        analog_value = 0;
        digitalWrite(liga_inversor, LOW);
        analogWrite(zero_a_10v, analog_value);
        digitalWrite(bomba_dagua, LOW);
      }

      if (Data.indexOf("SCT") == 0)
      {
        byte index1 = Data.indexOf(',');
        if (Data.substring(index1 + 1, Data.length() - 1).toInt() < 256);
        int value = Data.substring(index1 + 1, Data.length() - 1).toInt();
        value = constrain(value, 0, 255);
        if (value > 0) {
          PRESSAO_SETADA = value;
          digitalWrite(liga_inversor, HIGH);
          SET_CURVA_TURBINA = true;
        }
        else {
          digitalWrite(liga_inversor, LOW);
          analog_value = 0;
          analogWrite(zero_a_10v, analog_value);
          SET_CURVA_TURBINA = false;
        }
      }


      if (Data.substring(0, 4) == "P_IN") {
        if (Data.substring(5, 6) == "1") {
          Serial.println("P_IN LIGADO");
          digitalWrite(peristaltica_out, LOW);
          delay(500);
          digitalWrite(peristaltica_in, HIGH);
        }
        if (Data.substring(5, 6) == "0") {
          Serial.println("P_IN DESLIGADO");

          digitalWrite(peristaltica_in, LOW);
        }
      }


      if (Data.substring(0, 5) == "T_SEP") {
        int total = Data.substring(6, 11).toInt();
        if (total > 0) {
          EEPROM.writeInt(300, total);
        }
        Serial.println(EEPROM.readInt(300));

      }

      if (Data.substring(0, 6) == "EEPROM") {

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

      if (Data.substring(0, 5) == "P_OUT") {
        if (Data.substring(6, 7) == "1") {
          Serial.println("P_OUT LIGADO");
          digitalWrite(peristaltica_in, LOW);
          delay(500);
          digitalWrite(peristaltica_out, HIGH);
        }
        if (Data.substring(6, 7) == "0") {
          Serial.println("P_OUT DESLIGADO");
          digitalWrite(peristaltica_out, LOW);
        }
      }
      Data = "";
    }
  }

}
