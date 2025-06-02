
#define SERIAL_RX_BUFFER_SIZE 128
#define SERIAL_TX_BUFFER_SIZE 128

#include <EEPROMex.h>

#define pino_sct  4
#define VERSAO "V1.1"

/************************Hardware Related Macros***********************************/

#define         MQ_PIN                       (A2)     //define which analog input channel you are going to use
#define         RL_VALUE                     (10)    //define the load resistance on the board, in kilo ohms
#define         RO_CLEAN_AIR_FACTOR          (3.6)  //RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
//which is derived from the chart in datasheet

/***********************Software Related Macros************************************/
#define         CALIBARAION_SAMPLE_TIMES     (50)    //define how many samples you are going to take in the calibration phase
#define         CALIBRATION_SAMPLE_INTERVAL  (500)   //define the time interal(in milisecond) between each samples in the
//cablibration phase
#define         READ_SAMPLE_INTERVAL         (50)    //define how many samples you are going to take in normal operation
#define         READ_SAMPLE_TIMES            (5)     //define the time interal(in milisecond) between each samples in
//normal operation

/**********************Application Related Macros***********************************/
#define         GAS_H2S                      (0)

/*****************************Globals***********************************************/
float           H2SCurve[3]  =  {1.6, -0.87, -0.6};   //two points are taken from the curve in datasheet.
//with these two points, a line is formed which is "approximately equivalent"
//to the original curve.
//data format:{ x, y, slope}; point1: (lg200, 0.47), point2: (lg10000, -0.92)

float           Ro           =  10;                  //Ro is initialized to 10 kilo ohms
double pressao1 = 0;
double pressao2 = 0;
double pressao_anterior = 0.;
float calibra_pressao1;
float calibra_pressao2;
double pressao_absoluta;
double voltage_sensor_h2s = 0;
double leitura_sensor_h2s = 0;
double leitura_sensor_pressao = 0.0;
double leitura_sensor_pressao2 = 0.0;
double voltage_sensor = 0.0;
double voltage_sensor2 = 0.0;
bool pressao_seguranca = false;
String comando_serial = "";
const float ADC_mV = 4.8828125;       // convesion multiplier from Arduino ADC value to voltage in mV
//const float SensorOffset = 200.0;     // in mV taken from datasheet
const float sensitivity = 4.413;      // in mV/mmH2O taken from datasheet
const double mmh2O_cmH2O = 10;         // divide by this figure to convert mmH2O to cmH2O
const float mmh2O_kpa = 0.00981;      // convesion multiplier from mmH2O to kPa

#include <RBD_Timer.h>
/*****************************VARIÁVEIS DO TESTE DE PRESSÃO***************************/
RBD::Timer delay_teste;
unsigned long duracao_teste_pressao;//TEMPO DE DURAÇÃO DO TESTE DE PRESSÃO
unsigned int pressao_mais_alta = 0;
unsigned int pressao_mais_alta_anterior = 0;
unsigned int pressao_ideal_teste;
unsigned int tempo_alarme_teste_pressao;
unsigned long millis_teste_pressao;
unsigned long MILLIS = 0;

/******************************* VARIÁVEIS DA TROCA GASOSA *****************************/
RBD::Timer delay_troca;
RBD::Timer delay_read_sensors;
RBD::Timer delay_liga_turbina;
RBD::Timer envio_serial;
byte hora_troca;
byte minutos_troca;


/*************************** VARIÁVEIS PARA CONTAGEM REGRESSIVA ************************/
RBD::Timer delay_regressiva;
int intervalo_delay_regressiva = 1000;
unsigned int contagem_regressiva;
byte decrementa;

/*************************VARIÁVEIS PARA LIGA/DESLIGA BOMBA DÁGUA*********************/
RBD::Timer delay_bombaDagua;
//unsigned int time_delay_bombaDagua = 30000; //apenas no primeiro loop após libera_troca e pressao ideal atingida
int contagem_bombaDagua;
bool desativa_sensor_pressao_1 = false;
bool desativa_sensor_pressao_2 = false;
byte analog_value = 0; // ajusta o valor da porta 0 a 255 para 0 a 10v no hardware
byte analog_received = 0;
unsigned int total_de_sepultados;
#include <RBD_Button.h>
#include "DHT.h"

#define DHTPIN A1
#define DHTTYPE DHT21   // DHT 22  (AM2302)
DHT dht(DHTPIN, DHTTYPE);
float umidade;
float temperatura;
float b;
float c;
float d;
/******************* ATRIBUICAO DE PINOS I/O *******************/
#define ligaH2S 2
#define feedbackH2S 17
#define entrada4 12
#define botao_painel 9
RBD::Button button(botao_painel);//botão painel
unsigned long millisButton = 0;
// #define pressostato 11
#define ret_inversor_ok 10
#define bomba_dagua 8
#define reset_inversor 7
#define reset_12v 6 //  AI2 NO INVERSOR
#define liga_inversor 4     //AI1 NO INVERSOR
#define zero_a_10v 5
#define peristaltica_in 13 // Ligando peristaltica_in ou peristaltica_out liga também o sensor de h2s
#define peristaltica_out 14
#define DS3231_I2C_ADDRESS 104

byte tMSB, tLSB;
float temp3231;
String Data = "";
bool debug = false;
//###################################    #####################################
boolean passa;
bool calibrar1 = false;
bool calibrar2 = false;

// PORTA 01 = ATV INVERSOR; PORTA 02 = NAO CONECTADO; PORTA 03 VALVULA SOLENOIDE; PORTA 04 BOMBA D´AGUA;

int total_leituras = 1;
bool SET_CURVA_TURBINA = false;

RBD::Timer CHANGE_VALUE_PRESSAO;
RBD::Timer timer_reset12v;
RBD::Timer timer_resetInversor;
RBD::Timer timer_protecao;
RBD::Timer timer_temp_humidade;

int PRESSAO_SETADA = 0;

#include "alivioPress.h"

PressureController pressureController;