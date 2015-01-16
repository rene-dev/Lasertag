#define F_CPU 8000000

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>

//define pins
#define IR_CLOCK_DUTY_CYCLE OCR1A
#define LED_G OCR1B

//UART http://www.mikrocontroller.net/articles/AVR-GCC-Tutorial/Der_UART
#define BAUD 1200UL      // Baudrate

// Berechnungen
#define UBRR_VAL ((F_CPU+BAUD*8)/(BAUD*16)-1)   // clever runden
#define BAUD_REAL (F_CPU/(16*(UBRR_VAL+1)))     // Reale Baudrate
#define BAUD_ERROR ((BAUD_REAL*1000)/BAUD) // Fehler in Promille, 1000 = kein Fehler.

#if ((BAUD_ERROR<990) || (BAUD_ERROR>1010))
  #error Systematischer Fehler der Baudrate grösser 1% und damit zu hoch! 
#endif

void USART_Transmit( unsigned char data )
{
	/* Wait for empty transmit buffer */
	while ( !( UCSR0A & (1<<UDRE0)) ){}
	/* Put data into buffer, sends the data */
	UDR0 = data;
}

int main(void){
	cli();

	//set pins
	DDRB |= (1 << DDB0) | (1 << DDB1) | (1 << DDB2) | (1 << DDB3); //OUTPUT
	DDRD |= (1 << DDD3) | (1 << DDD5) | (1 << DDD6) | (1 << DDD7); //OUTPUT

	//Timer 1: Mode 14: Fast PWM, inverting mode, Top: ICR1, Update of OCR1x: Bottom, TOV1 Flag set on: TOP, Prescaler: 1
	TCCR1A = _BV(COM1B0) | _BV(COM1A0) | _BV(COM1B1) | _BV(COM1A1) | _BV(WGM11);
	TCCR1B = _BV(CS10) | _BV(WGM12) | _BV(WGM13);
	
	//IR carrier frequency to 37.915 kHz:
	ICR1 = 210;
	//IR carrier frequency duty cycle to 50%:
	IR_CLOCK_DUTY_CYCLE = ICR1-ICR1/2;
	
	//switch off all light
	LED_G=ICR1;
	
	//UART init
	UBRR0H = UBRR_VAL >> 8;
	UBRR0L = UBRR_VAL & 0xFF;
	UCSR0C = (1<<UCSZ01) | (1<<UCSZ00); //Asynchron 8N1 
	UCSR0B = _BV(TXEN0) | _BV(RXEN0); //UART RX, TX einschalten
	
	sei();                  // enable Interrupts global
	
 	while(1){
		USART_Transmit('a'); //IR_TX: PlayerID
		USART_Transmit('b'); //IR_TX: Schaden
		_delay_ms(40);
	}
}
