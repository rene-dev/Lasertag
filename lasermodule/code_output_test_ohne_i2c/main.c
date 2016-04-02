//Lasermodule code_output_test_ohne_i2c

#define F_CPU 8000000

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>
#include "twislave.h"

//---------------------------- Pins and PWM Registers ----------------------------

#define LASER PD7 //laser 2
#define HAPTIK OCR0A //laser 1
#define LED_FRONT_B OCR0B
#define IR_CLOCK_DUTY_CYCLE OCR1A
#define LED_FRONT_G OCR1B
#define LED_FRONT_R OCR2A
#define LED_FRONT_W OCR2B
#define BUTTON_1 PB7
#define BUTTON_2 PB6
#define BUTTON_3 PD4
#define ONOFF PB0

//---------------------------- i2c Settings ----------------------------

#define I2C_BUS_ADRESS 0x03 //Weapon Lasermodule

#define LED_FRONT_REG 0
typedef struct{
	uint8_t r;
	uint8_t g;
	uint8_t b;
	uint8_t w;
} led_front_t;
static volatile led_front_t led_front_buffer;

#define LASER_REG 4
typedef struct{
	uint8_t laser; //laser 2
} laser_t;
static volatile laser_t laser_buffer;

#define HAPTIK_REG 7
typedef struct{
	uint8_t vibrate; //laser 1
} haptik_t;
static volatile haptik_t haptik_buffer;

#define BUTTON_REG 10
typedef struct{
	uint8_t button_1;
	uint8_t button_2;
	uint8_t button_3;
} button_t;
static volatile button_t button_buffer;

#define SHOOT_REG 20
typedef struct{
	uint8_t enable; //20, Fire once if written > 0
	uint8_t playerid; //21
	uint8_t damage; //22
	uint8_t laser; //23
	uint8_t laser_duration; //24, Laser light duration
	uint8_t vibrate_power; //25
	uint8_t vibrate_duration; //26
	uint8_t muzzle_flash_r; //27
	uint8_t muzzle_flash_g; //28
	uint8_t muzzle_flash_b; //29
	uint8_t muzzle_flash_w; //30
	uint8_t muzzle_flash_duration; //31
} shoot_t;
static volatile shoot_t shoot_buffer;

#define HIT_REG 40
typedef struct{
	uint8_t enable; //Hit if enabled
	uint8_t playerid;
	uint8_t damage;
} hit_t;
static volatile hit_t hit_buffer;

#define MISC_REG 50
typedef struct{
	uint8_t v_bat_l;
	uint8_t v_bat_r;
	uint8_t ldr_l;
	uint8_t ldr_r;
} misc_t;
static volatile misc_t misc_buffer;

//logarithmic pwm fading: http://www.mikrocontroller.net/articles/LED-Fading
//const uint8_t pwmtable64[64] PROGMEM = 
const uint8_t pwmtable64[64] = 
{
    1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 21, 22, 24, 26, 28, 30, 33, 35, 38, 41, 45, 48, 52, 56, 61, 65, 71, 76, 82, 89, 96, 103, 111, 120, 129, 140, 151, 162, 175, 189, 203, 219, 237, 255
};

//---------------------------- UART init ----------------------------

//UART http://www.mikrocontroller.net/articles/AVR-GCC-Tutorial/Der_UART
#define BAUD 1200UL      // Baudrate

// Berechnungen
#define UBRR_VAL ((F_CPU+BAUD*8)/(BAUD*16)-1)   // clever runden
#define BAUD_REAL (F_CPU/(16*(UBRR_VAL+1)))     // Reale Baudrate
#define BAUD_ERROR ((BAUD_REAL*1000)/BAUD) // Fehler in Promille, 1000 = kein Fehler.

#if ((BAUD_ERROR<990) || (BAUD_ERROR>1010))
  #error Systematischer Fehler der Baudrate grösser 1% und damit zu hoch! 
#endif

//----------------------------  ----------------------------

uint8_t crc8(const void *vptr, int len){
	const uint8_t *data = vptr;
	unsigned crc = 0;
	int i, j;
	for (j = len; j; j--, data++) {
		crc ^= (*data << 8);
		for(i = 8; i; i--) {
			if (crc & 0x8000)
			crc ^= (0x1070 << 3);
			crc <<= 1;
		}
	}
	return (uint8_t)(crc >> 8);
}

uint32_t map32(uint32_t x, uint32_t in_min, uint32_t in_max, uint32_t out_min, uint32_t out_max)
{
  return (x - in_min) * (out_max - out_min + 1) / (in_max - in_min + 1) + out_min;
}

uint16_t map16(uint16_t x, uint16_t in_min, uint16_t in_max, uint16_t out_min, uint16_t out_max)
{
  return (x - in_min) * (out_max - out_min + 1) / (in_max - in_min + 1) + out_min;
}

uint8_t map8(uint8_t x, uint8_t in_min, uint8_t in_max, uint8_t out_min, uint8_t out_max)
{
  return (x - in_min) * (out_max - out_min + 1) / (in_max - in_min + 1) + out_min;
}

uint8_t taster(volatile uint8_t *port, uint8_t pin)
{
	if(!(*port & (1 << pin))){
		//LED_FRONT_R=240;
		return 1;
	}else{
		//LED_FRONT_R=255;
		return 0;
	}
}

ISR(USART_RX_vect){
	//hit: PlayerID Schaden crc8_checksum
	static uint8_t rx[3];
	rx[0] = rx[1]; //nach links durchschieben
	rx[1] = rx[2];
	rx[2] = UDR0;

	if(crc8(rx, 2) == rx[2]){
		hit_buffer.playerid = rx[0];
		hit_buffer.damage = rx[1];
		hit_buffer.enable = 1;
	}
}

void USART_Transmit( unsigned char data )
{
	/* Wait for empty transmit buffer */
	while ( !( UCSR0A & (1<<UDRE0)) ){}
	/* Put data into buffer, sends the data */
	UDR0 = data;
}

ISR(TIMER0_OVF_vect){
	// if(counter++ == 38){
		// millis++;
		// counter=0;
	// }
}

uint8_t laser(uint8_t on){
	static uint8_t laser_status;
	if(on == 1){
		PORTD |= (1 << LASER);
		laser_status = on;
	}else if(on == 0){
		PORTD &= ~(1 << LASER);
		laser_status = on;
	}
	return laser_status;
}
	
volatile uint8_t i2c_last_reg_access = -1;

void i2c_slave_poll_buffer(unsigned char reg_addr, volatile unsigned char** buffer, volatile unsigned char* buffer_length){
	// switch(reg_addr){
		// case LED_FRONT_REG ... LED_FRONT_REG + sizeof(led_front_t) - 1:
			// *buffer        = &((uint8_t *)&led_front_buffer)[reg_addr-LED_FRONT_REG];
			// *buffer_length = (sizeof(led_front_t)-reg_addr);
			// i2c_last_reg_access = LED_FRONT_REG;
			// break;
		// case LASER_REG ... LASER_REG + sizeof(laser_front_t) - 1:
			// *buffer        = &((uint8_t *)&laser_front_buffer)[reg_addr-LASER_REG];
			// *buffer_length = (sizeof(laser_front_t)-reg_addr);
			// i2c_last_reg_access = LASER_REG;
			// break;

	if ((reg_addr >= LED_FRONT_REG) && (reg_addr < (LED_FRONT_REG + sizeof(led_front_t)))){
		*buffer        = &((uint8_t *)&led_front_buffer)[reg_addr-LED_FRONT_REG];
		*buffer_length = sizeof(led_front_t)-(reg_addr-LED_FRONT_REG);
		i2c_last_reg_access = LED_FRONT_REG;
	} else if ((reg_addr >= BUTTON_REG) && (reg_addr < (BUTTON_REG + sizeof(button_t)))){ //10-12
		*buffer        = &((uint8_t *)&button_buffer)[reg_addr-BUTTON_REG];
		*buffer_length = sizeof(button_t)-(reg_addr-BUTTON_REG);
		i2c_last_reg_access = BUTTON_REG;
	} else if ((reg_addr >= LASER_REG) && (reg_addr < (LASER_REG + sizeof(laser_t)))){
		*buffer        = &((uint8_t *)&laser_buffer)[reg_addr-LASER_REG];
		*buffer_length = sizeof(laser_t)-(reg_addr-LASER_REG);
		i2c_last_reg_access = LASER_REG;
	} else if ((reg_addr >= HAPTIK_REG) && (reg_addr < (HAPTIK_REG + sizeof(haptik_t)))){
		*buffer        = &((uint8_t *)&haptik_buffer)[reg_addr-HAPTIK_REG];
		*buffer_length = sizeof(haptik_t)-(reg_addr-HAPTIK_REG);
		i2c_last_reg_access = HAPTIK_REG;
	} else if ((reg_addr >= SHOOT_REG) && (reg_addr < (SHOOT_REG + sizeof(shoot_t)))){
		*buffer        = &((uint8_t *)&shoot_buffer)[reg_addr-SHOOT_REG];
		*buffer_length = sizeof(shoot_t)-(reg_addr-SHOOT_REG);
		i2c_last_reg_access = SHOOT_REG;
	} else if ((reg_addr >= HIT_REG) && (reg_addr < (HIT_REG + sizeof(hit_t)))){
		*buffer        = &((uint8_t *)&hit_buffer)[reg_addr-HIT_REG];
		*buffer_length = sizeof(hit_t)-(reg_addr-HIT_REG);
		i2c_last_reg_access = HIT_REG;
	} else if ((reg_addr >= MISC_REG) && (reg_addr < (MISC_REG + sizeof(misc_t)))){
		*buffer        = &((uint8_t *)&misc_buffer)[reg_addr-MISC_REG];
		*buffer_length = sizeof(misc_t)-(reg_addr-MISC_REG);
		i2c_last_reg_access = MISC_REG;
	} else {
		*buffer_length = 0;
		*buffer = 0;
	}
}

void i2c_slave_write_complete(void){
}

void i2c_slave_read_complete(void){
	if (i2c_last_reg_access == HIT_REG) hit_buffer.enable = 0;
}

int main(void){
	// 12 PB0 LASER_R  ---- NICHT MEHR ----
	// 11 PD7 LASER								(Laser)
	// 10 PD6 HAPTIK		OC0A	Timer0	 8 Bit	(Haptik)
	//  9 PD5 LED_FRONT_B	OC0B	Timer0	 8 Bit
	// 13 PB1 IR_CLOCK_-	OC1A	Timer1	16 Bit
	// 14 PB2 LED_FRONT_G	OC1B	Timer1	16 Bit
	// 15 PB3 LED_FRONT_R	OC2A	Timer2	 8 Bit
	//  1 PD3 LED_FRONT_W	OC2B	Timer2	 8 Bit
	// 24 PC1 LDR			ADC1
	// 25 PC2 V_BATT		ADC2
	//  2 PD4 BUTTON_3
	//  7 PB6 BUTTON_2
	//  8 PB7 BUTTON_1
	// 12 PB0 ONOFF

	cli();

	//set pins
	DDRB |= (1 << DDB1) | (1 << DDB2) | (1 << DDB3); //OUTPUT
	DDRD |= (1 << DDD3) | (1 << DDD5) | (1 << DDD6) | (1 << DDD7); //OUTPUT
	DDRB &= ~(1 << PB6) & ~(1 << PB7); //INPUT
	PORTB |= (1 << PB6) | (1 << PB7); //input pullup
	DDRD &= ~(1 << PD4); //INPUT
	PORTD |= (1 << PD4); //input pullup
	
	//ausschalten
	//DDRB |= (1 << DDB0); //OUTPUT
	//PORTB &= ~(1 << DDB0); //LOW

	//init Timers for PWM:
	//https://sites.google.com/site/qeewiki/books/avr-guide/pwm-on-the-atmega328
	//WGM* s157: fast pwm without ctc
	//CS*  s158: _BV(CS20) = prescaler 1 (gilt für a und b)
	//PWM_fequency = clock_speed / [Prescaller_value * (1 + TOP_Value) ] = 8000000/(1*(1+210)) = 37.915 kHz
	
	//Timer 0: Mode 3: Fast PWM, TOP: 0xFF, Update of OCRx: Bottom, TOV1 Flag set on: TOP, Prescaler: 1, Set OC0x on Compare Match
	TCCR0A = _BV(COM0B0) | _BV(COM0A0) | _BV(COM0B1) | _BV(COM0A1) | _BV(WGM00) | _BV(WGM01);
	TCCR0B = _BV(CS00);
	//TIMSK0 |= (1<<TOIE0); //Overflow Interrupt for count millis
	
	//Timer 2: Mode 3: Fast PWM, TOP: 0xFF, Update of OCRx: Bottom, TOV1 Flag set on: TOP, Prescaler: 1, Set OC2x on Compare Match
	TCCR2A = _BV(COM2B0) | _BV(COM2A0) | _BV(COM2B1) | _BV(COM2A1) | _BV(WGM20) | _BV(WGM21);
	TCCR2B = _BV(CS20);
	
	//Timer 1: Mode 14: Fast PWM, inverting mode, Top: ICR1, Update of OCR1x: Bottom, TOV1 Flag set on: TOP, Prescaler: 1
	//https://docs.google.com/spreadsheets/d/1HadMDsU0MGo1LXUr1gKNFrfe4wX_Bq9kbVIwOvD3chk
	TCCR1A = _BV(COM1B0) | _BV(COM1A0) | _BV(COM1B1) | _BV(COM1A1) | _BV(WGM11);
	TCCR1B = _BV(CS10) | _BV(WGM12) | _BV(WGM13);

	//IR carrier frequency to 37.915 kHz:
	ICR1 = 210;
	//IR carrier frequency duty cycle to 50%:
	IR_CLOCK_DUTY_CYCLE = ICR1-ICR1/2;
	
	//switch off all light
	LED_FRONT_R=255;
	LED_FRONT_G=ICR1;
	LED_FRONT_B=255;
	LED_FRONT_W=255;
	HAPTIK=255; //haptik
	//PORTB |= (1 << PB0); //an
	
	//i2c init
	init_twi_slave(I2C_BUS_ADRESS<<1);

	//UART init
	UBRR0H = UBRR_VAL >> 8;
	UBRR0L = UBRR_VAL & 0xFF;
	UCSR0B |= _BV(TXEN0) | _BV(RXEN0) | _BV(RXCIE0); //UART RX, TX und RX-Interrupt einschalten
	UCSR0C = (1<<UCSZ01) | (1<<UCSZ00); //Asynchron 8N1 
	
	sei(); // enable Interrupts global
	
	uint32_t laser_duration_counter=0;
	uint32_t vibrate_duration_counter=0;
	uint32_t muzzle_flash_duration_counter=0;
	uint32_t muzzle_flash_duration_counter_max=0; //fürs ausfaden
	uint16_t ir_delay=0;
	uint8_t ir_count=255;
	
			// return links*256 + rechts
	uint16_t battt = 12345;
	misc_buffer.v_bat_l = battt>>8;
	misc_buffer.v_bat_r = battt;
	
 	while(1){
/*  		// ---------------- blinken + buttons (gedrueckt halten) + ir shoot ----------------
		LED_FRONT_R = 255-1-taster(&PINB, BUTTON_1)*100;
		LED_FRONT_G = ICR1-map8(2, 0, 255, 0, ICR1); //0 bis ICR1
		LED_FRONT_B = 255-1-taster(&PINB, BUTTON_2)*100;
		LED_FRONT_W = 255-1-taster(&PIND, BUTTON_3)*100;
		laser(1); //laser
		HAPTIK = 255-50; //haptik

		_delay_ms(255);
		_delay_ms(255);
		_delay_ms(255);
		
		LED_FRONT_R = 255-0;
		LED_FRONT_G = ICR1-map8(0, 0, 255, 0, ICR1); //0 bis ICR1
		LED_FRONT_B = 255-0;
		LED_FRONT_W = 255-0;
		laser(0); //laser
		HAPTIK = 255-0; //haptik
		
		_delay_ms(255);
		_delay_ms(255);
		_delay_ms(255);
		
		shoot_buffer.playerid = 42;
		shoot_buffer.damage = 123;
		shoot_buffer.enable = 1;
		uint8_t array[] = {shoot_buffer.playerid, shoot_buffer.damage};
		USART_Transmit(shoot_buffer.playerid); //IR_TX: PlayerID
		USART_Transmit(shoot_buffer.damage); //IR_TX: Schaden
		USART_Transmit(crc8(array, 2)); //IR_TX: crc8 checksum
 */
		
 		// ---------------- pew ----------------
		uint8_t brightness = 80;
		if(taster(&PINB, BUTTON_1)){
			if(taster(&PINB, BUTTON_2) && !taster(&PIND, BUTTON_3)){
				LED_FRONT_R = 255-brightness;
				LED_FRONT_G = ICR1-map8(0, 0, 255, 0, ICR1);
				LED_FRONT_B = 255-0;
				LED_FRONT_W = 255-0;
				_delay_ms(20);
				laser(1);
			}else if(!taster(&PINB, BUTTON_2) && taster(&PIND, BUTTON_3)){
				LED_FRONT_R = 255-0;
				LED_FRONT_G = ICR1-map8(brightness, 0, 255, 0, ICR1);
				LED_FRONT_B = 255-0;
				LED_FRONT_W = 255-0;
				_delay_ms(20);
				laser(1);
			}else if(taster(&PINB, BUTTON_2) && taster(&PIND, BUTTON_3)){
				LED_FRONT_R = 255-brightness;
				LED_FRONT_G = ICR1-map8(brightness, 0, 255, 0, ICR1);
				LED_FRONT_B = 255-brightness;
				LED_FRONT_W = 255-brightness;
				_delay_ms(20);
				laser(1);
			}else{
				LED_FRONT_R = 255-0;
				LED_FRONT_G = ICR1-map8(0, 0, 255, 0, ICR1);
				LED_FRONT_B = 255-brightness;
				LED_FRONT_W = 255-0;
				_delay_ms(20);
				laser(1);
			}
			
			
			_delay_ms(30);
			LED_FRONT_R = 255-0;
			LED_FRONT_G = ICR1-map8(0, 0, 255, 0, ICR1);
			LED_FRONT_B = 255-0;
			LED_FRONT_W = 255-0;
			
			_delay_ms(200);
			laser(0);
			_delay_ms(255);
		}
					
		
		
/* 		// ---- buttons ----
		laser_buffer.laser = taster(&PINB, BUTTON_1);
		led_front_buffer.r = taster(&PINB, BUTTON_2)*255;
		led_front_buffer.b = taster(&PIND, BUTTON_3)*255;
 */
	}
}
