#define F_CPU 8000000

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>
#include "twislave.h"

//define pins
#define LASER_B OCR0A
#define LED_B OCR0B
#define IR_CLOCK_DUTY_CYCLE OCR1A
#define LED_G OCR1B
#define LED_R OCR2A
#define LED_W OCR2B

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
	unsigned char ch = UDR0;
	if(lastbyte == 'a' && ch == 'b'){
		alive = NO;
	}
	lastbyte = ch;
}

void USART_Transmit( unsigned char data )
{
	/* Wait for empty transmit buffer */
	while ( !( UCSR0A & (1<<UDRE0)) ){}
	/* Put data into buffer, sends the data */
	UDR0 = data;
}

void long_delay(uint16_t ms)
{
	for(; ms>0; ms--) _delay_ms(1);
}

uint32_t millis;
volatile uint8_t counter;

ISR(TIMER0_OVF_vect){
	if(counter++ == 38){
		millis++;
		counter=0;
	}
}

uint8_t laser_r(uint8_t on){
	static uint8_t laser_r_status;
	if(on == 1){
		PORTB |= (1 << PB0);
		laser_r_status = on;
	}else if(on == 0){
		PORTB &= ~(1 << PB0);
		laser_r_status = on;
	}
	return laser_r_status;
}

uint8_t laser_g(uint8_t on){
	static uint8_t laser_g_status;
	if(on == 1){
		PORTD |= (1 << PD7);
		laser_g_status = on;
	}else if(on == 0){
		PORTD &= ~(1 << PD7);
		laser_g_status = on;
	}
	return laser_g_status;
}

int main(void){
	// 12 PB0 LASER_R
	// 11 PD7 LASER_G
	// 10 PD6 LASER_B    OC0A	Timer0	 8 Bit
	//  9 PD5 LED_B      OC0B	Timer0	 8 Bit
	// 13 PB1 IR_CLOCK_- OC1A	Timer1	16 Bit
	// 14 PB2 LED_G      OC1B	Timer1	16 Bit
	// 15 PB3 LED_R      OC2A	Timer2	 8 Bit
	//  1 PD3 LED_W	     OC2B	Timer2	 8 Bit
	// 24 PC1 LDR        ADC1
	// 25 PC2 V_BATT     ADC2
	
	cli();

	//set pins to OUTPUT
	DDRB |= (1 << DDB0) | (1 << DDB1) | (1 << DDB2) | (1 << DDB3);
	DDRD |= (1 << DDD3) | (1 << DDD5) | (1 << DDD6) | (1 << DDD7);
	
	//init Timers for PWM:
	//https://sites.google.com/site/qeewiki/books/avr-guide/pwm-on-the-atmega328
	//WGM* s157: fast pwm without ctc
	//CS*  s158: _BV(CS20) = prescaler 1 (gilt für a und b)
	//PWM_fequency = clock_speed / [Prescaller_value * (1 + TOP_Value) ] = 8000000/(1*(1+210)) = 37.915 kHz
	
	//Timer 0: Mode 3: Fast PWM, TOP: 0xFF, Update of OCRx: Bottom, TOV1 Flag set on: TOP, Prescaler: 1, Set OC0x on Compare Match
	TCCR0A = _BV(COM0B0) | _BV(COM0A0) | _BV(COM0B1) | _BV(COM0A1) | _BV(WGM00) | _BV(WGM01);
    TCCR0B = _BV(CS00);
	TIMSK0 |= (1<<TOIE0); //Overflow Interrupt for count millis
	
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
	LED_R=255;
	LED_G=ICR1;
	LED_B=255;
	LED_W=255;
	LASER_B=255;
	//PORTB |= (1 << PB0); //an
	
	//i2c init
	init_twi_slave(0x30);

	//UART init
	UBRR0H = UBRR_VAL >> 8;
	UBRR0L = UBRR_VAL & 0xFF;
	UCSR0B |= _BV(TXEN0) | _BV(RXEN0) | _BV(RXCIE0); //UART RX, TX und RX-Interrupt einschalten
    UCSR0C = (1<<UCSZ01) | (1<<UCSZ00); //Asynchron 8N1 
	sei();                  // enable Interrupts global
	
	//i2c test
 	while(1){
		txbuffer[0] = rxbuffer[0];
		txbuffer[1] = rxbuffer[1];
		txbuffer[2] = rxbuffer[2];
		laser_r(1);
		_delay_ms(100);
		laser_r(0);

		_delay_ms(100);
	}
	
	
/* 	//output test mode
	#define FADE_DELAY 3
 	while(1){
		laser_r(1);
		for(LED_R=255; LED_R>0; LED_R--){_delay_ms(FADE_DELAY);}
		for(LED_R=0; LED_R<255; LED_R++){_delay_ms(FADE_DELAY);}
		for(LED_G=ICR1; LED_G>0; LED_G--){_delay_ms(FADE_DELAY);}
		for(LED_G=0; LED_G<ICR1; LED_G++){_delay_ms(FADE_DELAY);}
		laser_r(0);
		for(LED_B=255; LED_B>0; LED_B--){_delay_ms(FADE_DELAY);}
		for(LED_B=0; LED_B<255; LED_B++){_delay_ms(FADE_DELAY);}
		for(LED_W=255; LED_W>0; LED_W--){_delay_ms(FADE_DELAY);}
		for(LED_W=0; LED_W<255; LED_W++){_delay_ms(FADE_DELAY);}
	}
 */
	uint32_t time1=0, time2=0;
	while(1){
		// LED_R = 255-1;
		// _delay_ms(500);
		// LED_R = 255-0;
		// LED_G = ICR1-1;
		// _delay_ms(500);
		// LED_G = 255-0;
		// LED_B = 255-1;
		// _delay_ms(500);
		// LED_B = 255-0;
		// LED_W = 255-1;
		// _delay_ms(500);
		// LED_W = 255-0;
		laser_r(1);
		_delay_ms(1000);
		laser_r(0);
		_delay_ms(1000);
	
	
	
	
/*  		if(alive){
			LED_R = 100;
			LED_G = 100;
			LED_B = 100;
			LED_W = 100;
		} else {
			LED_R = 0;
			LED_G = 0;
			LED_B = 0;
			LED_W = 0;
			_delay_ms(50);
			alive = YES;
		}
		if (millis - time1 > 500) {
			USART_Transmit('a');
			USART_Transmit('b');
			time1 = millis;
		}
		if (millis - time2 > 1000) {
			laser_r(!laser_r(2));
			time2 = millis;
		}
 */	}
	return 0;
}
