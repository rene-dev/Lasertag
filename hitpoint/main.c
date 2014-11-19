#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>
#include "pwm.h"

#define NO 0
#define YES 1

//UART http://www.mikrocontroller.net/articles/AVR-GCC-Tutorial/Der_UART
#define BAUD 1200UL      // Baudrate

// Berechnungen
#define UBRR_VAL ((F_CPU+BAUD*8)/(BAUD*16)-1)   // clever runden
#define BAUD_REAL (F_CPU/(16*(UBRR_VAL+1)))     // Reale Baudrate
#define BAUD_ERROR ((BAUD_REAL*1000)/BAUD) // Fehler in Promille, 1000 = kein Fehler.
 
#if ((BAUD_ERROR<990) || (BAUD_ERROR>1010))
  #error Systematischer Fehler der Baudrate grösser 1% und damit zu hoch! 
#endif

volatile uint8_t alive = YES;

ISR(USART_RX_vect){
	static unsigned char lastbyte = 0;
	unsigned char ch = UDR;
	if(lastbyte == 'a' && ch == 'b'){
		alive = NO;
	}
	lastbyte = ch;
}

void long_delay(uint16_t ms)
{
	for(; ms>0; ms--) _delay_ms(1);
}

int main(void) {
	int i = 0;
	uint8_t pwm[8];
	pwm_init();
	sei();                  // Interrupts global einschalten
	
	//UART init
	UBRRH = UBRR_VAL >> 8;
	UBRRL = UBRR_VAL & 0xFF;
	UCSRC = (1<<UCSZ1)|(1<<UCSZ0);  // Asynchron 8N1 
	UCSRB |= (1<<RXEN)|(1<<RXCIE);  // UART RX und RX Interrupt einschalten
	
	while(1){
		if(alive){
			pwm[LED1R] = 30;
			pwm[LED1G] = 31;
			pwm[LED1B] = 32;
			pwm[LED2R] = 33;
			pwm[LED2G] = 34;
			pwm[LED2B] = 35;
			memcpy(pwm_setting, pwm, 8);
			pwm_update();
		}else{
			pwm[LED1R] = pwm[LED2R] = 0;
			pwm[LED1G] = pwm[LED2G] = 0;
			pwm[LED1B] = pwm[LED2B] = 0;
			memcpy(pwm_setting, pwm, 8);
			pwm_update();
			long_delay(50);
			alive = YES;
		}
	}
	return 0;
}

