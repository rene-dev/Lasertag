#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>
#include "i2c_slave_usi.h"

#define NO 0
#define YES 1

#define RED OCR1B
#define GREEN OCR1A
#define BLUE OCR0A

//UART http://www.mikrocontroller.net/articles/AVR-GCC-Tutorial/Der_UART
#define BAUD 1200UL      // Baudrate

// Berechnungen
#define UBRR_VAL ((F_CPU+BAUD*8)/(BAUD*16)-1)   // clever runden
#define BAUD_REAL (F_CPU/(16*(UBRR_VAL+1)))     // Reale Baudrate
#define BAUD_ERROR ((BAUD_REAL*1000)/BAUD) // Fehler in Promille, 1000 = kein Fehler.
 
#if ((BAUD_ERROR<990) || (BAUD_ERROR>1010))
  #error Systematischer Fehler der Baudrate grösser 1% und damit zu hoch! 
#endif

#define BIT_SET(port, mask, value) {if (value) {port |= (mask);} else {port &= ~(mask);}}

//i2c adresses
#define REG_LED_COLOR 0x00
#define REG_LAST_HIT  0x10

volatile uint8_t alive = YES;
volatile uint8_t color_buffer[3];
volatile uint16_t color[3];
volatile uint8_t last_hit = 0;
volatile uint8_t i2c_last_reg_access = -1;

ISR(USART_RX_vect){
	static unsigned char lastbyte = 0;
	unsigned char ch = UDR;
	if(lastbyte == 'a' && ch == 'b'){
		alive = NO;
		last_hit = 42;
	}
	lastbyte = ch;
}

void long_delay(uint16_t ms)
{
	for(; ms>0; ms--) _delay_ms(1);
}

//master greift auf lm zu, lesen oder schreiben (interrupt). reg_addr=stelle im i2c buffer die angefragt wird. buffer_length=wieviele zeichen angefragt werden dürfen (nur für lib)
void i2c_slave_poll_buffer(uint8_t reg_addr, volatile uint8_t **buffer, volatile uint8_t *buffer_length){
	if ((reg_addr >= REG_LED_COLOR) && (reg_addr < (REG_LED_COLOR + 3))){
		*buffer        = &color_buffer[reg_addr];
		*buffer_length = (3-(reg_addr-REG_LED_COLOR));
		i2c_last_reg_access = REG_LED_COLOR;
	} else if (reg_addr == REG_LAST_HIT){
		*buffer        = &last_hit; //buffer-pointer wird auf last_hit umgebogen
		*buffer_length = 1; //aus last_hit darf 1 byte gelesen werden
		i2c_last_reg_access = REG_LAST_HIT; //modul merkt sich was zuletzt angefordert wurde um nach abruf den buffer zu leeren
	} else {
// 		*buffer = i2c_buffer;
// 		*buffer_length = 16;
		*buffer_length = 0;
		*buffer = 0;
	}
}
void i2c_slave_write_complete(void){
	
}
void i2c_slave_read_complete(void){
	if (i2c_last_reg_access == REG_LAST_HIT) last_hit = 0;
}

ISR (TIMER0_OVF_vect){
}

int main(void) {
	usi_i2c_init(0x20);
	sei();                  // Interrupts global einschalten
	
	DDRB |= _BV(DDB2) | _BV(DDB3) | _BV(DDB4);//LEDs

	//PWM, Phase Correct, 8-bit, no presacler -> 16kHz
	TCCR0A = _BV(WGM00) | _BV(COM0A1);
	TCCR0B = _BV(CS00);
	TCCR1A = _BV(WGM10) | _BV(COM1A1) | _BV(COM1B1);
	TCCR1B = _BV(CS00);
	//TIMSK |= (1<<TOIE0);	

	RED = 0;
	GREEN = 0;
	BLUE = 0;
	//UART init
	UBRRH = UBRR_VAL >> 8;
	UBRRL = UBRR_VAL & 0xFF;
	UCSRC = _BV(UCSZ1) | _BV(UCSZ0);  // Asynchron 8N1 
	UCSRB |= _BV(RXEN)| _BV(RXCIE);  // UART RX und RX Interrupt einschalten
	
	while(1){
		long_delay(1);
		if(alive){
			color[0] = (uint16_t)color_buffer[0] + ((uint16_t)RED*99); //color_buffer=zielwert vom i2c
			RED = color[0]/100;
			color[1] = (uint16_t)color_buffer[1] + ((uint16_t)GREEN*99);
			GREEN = color[1]/100;
			color[2] = (uint16_t)color_buffer[2] + ((uint16_t)BLUE*99);
			BLUE = color[2]/100;
		} else {
			color[0] = 0;
			color[1] = 0;
			color[2] = 0;
			long_delay(50);
			alive = YES;
		}
	}
	return 0;
}
