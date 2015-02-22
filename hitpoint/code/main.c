#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>
#include "i2c_slave_usi.h"

//---------------------------- Pins and PWM Registers ----------------------------

#define LED_10MM_R OCR1B
#define LED_10MM_G OCR1A
#define LED_10MM_B OCR0A

//---------------------------- i2c Settings ----------------------------

//i2c-bus adress
//0x00				Broadcast
//0x03				Weapon Lasermodule
//0x04				Weapon Hitmodule
//0x10, 0x11, ...	Weste Hitmodules
#define I2C_BUS_ADRESS 0x04

#define HAPTIK_REG 7
typedef struct{
	uint8_t vibrate;
} haptik_t;
volatile haptik_t haptik_buffer;

#define HIT_REG 30
typedef struct{
	uint8_t enable; //Hit if enabled
	uint8_t playerid;
	uint8_t damage;
} hit_t;
volatile hit_t hit_buffer;

#define LED_10MM_REG 50
typedef struct{
	uint8_t r;
	uint8_t g;
	uint8_t b;
} led_10mm_t;
volatile led_10mm_t led_10mm_buffer;

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

ISR(USART_RX_vect){
	//hit: PlayerID Schaden crc8_checksum
	static uint8_t rx[3];
	rx[0] = rx[1]; //nach links durchschieben
	rx[1] = rx[2];
	rx[2] = UDR;

	if(crc8(rx, 2) == rx[2]){
		hit_buffer.playerid = rx[0];
		hit_buffer.damage = rx[1];
		hit_buffer.enable = 1;
	}
}

volatile uint8_t i2c_last_reg_access = -1;

//master greift auf lm zu, lesen oder schreiben (interrupt). reg_addr=stelle im i2c buffer die angefragt wird. buffer_length=wieviele zeichen angefragt werden dürfen (nur für lib)
void i2c_slave_poll_buffer(uint8_t reg_addr, volatile uint8_t **buffer, volatile uint8_t *buffer_length){
	if ((reg_addr >= HAPTIK_REG) && (reg_addr < (HAPTIK_REG + sizeof(haptik_t)))){
		*buffer        = &((uint8_t *)&haptik_buffer)[reg_addr-HAPTIK_REG];
		*buffer_length = (sizeof(haptik_t)-reg_addr);
		i2c_last_reg_access = HAPTIK_REG;
	} else if ((reg_addr >= HIT_REG) && (reg_addr < (HIT_REG + sizeof(hit_t)))){
		*buffer        = &((uint8_t *)&hit_buffer)[reg_addr-HIT_REG];
		*buffer_length = (sizeof(hit_t)-reg_addr);
		i2c_last_reg_access = HIT_REG;
	} else if ((reg_addr >= LED_10MM_REG) && (reg_addr < (LED_10MM_REG + sizeof(led_10mm_t)))){
		*buffer        = &((uint8_t *)&led_10mm_buffer)[reg_addr-LED_10MM_REG];
		*buffer_length = (sizeof(led_10mm_t)-reg_addr);
		i2c_last_reg_access = LED_10MM_REG;
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

ISR (TIMER0_OVF_vect){
}

int main(void) {
	sei(); // Interrupts global einschalten
	
	usi_i2c_init(I2C_BUS_ADRESS<<1);
	
	//set pins
	DDRB |= _BV(DDB2) | _BV(DDB3) | _BV(DDB4);//LEDs

	//PWM, Phase Correct, 8-bit, no presacler -> 16kHz
	TCCR0A = _BV(WGM00) | _BV(COM0A1);
	TCCR0B = _BV(CS00);
	TCCR1A = _BV(WGM10) | _BV(COM1A1) | _BV(COM1B1);
	TCCR1B = _BV(CS00);
	//TIMSK |= (1<<TOIE0); //overflow interrupt

	LED_10MM_R = 0;
	LED_10MM_G = 0;
	LED_10MM_B = 0;
	
	//UART init
	UBRRH = UBRR_VAL >> 8;
	UBRRL = UBRR_VAL & 0xFF;
	UCSRC = _BV(UCSZ1) | _BV(UCSZ0);  // Asynchron 8N1 
	UCSRB |= _BV(RXEN)| _BV(RXCIE);  // UART RX und RX Interrupt einschalten
	
	uint16_t fade_helper_r, fade_helper_g, fade_helper_b;
	
	while(1){
		_delay_ms(1);
		// fade_helper_r = (uint16_t)led_10mm_buffer.r + ((uint16_t)LED_10MM_R*99);
		// LED_10MM_R = fade_helper_r/100;
		// fade_helper_g = (uint16_t)led_10mm_buffer.g + ((uint16_t)LED_10MM_G*99);
		// LED_10MM_G = fade_helper_g/100;
		// fade_helper_b = (uint16_t)led_10mm_buffer.b + ((uint16_t)LED_10MM_B*99);
		// LED_10MM_B = fade_helper_b/100;
		LED_10MM_R = led_10mm_buffer.r;
		LED_10MM_G = led_10mm_buffer.g;
		LED_10MM_B = led_10mm_buffer.b;
	}
}
