//Lasermodule

#define F_CPU 8000000

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>

//---------------------------- Pins and PWM Registers ----------------------------

#define LASER_2 PD7
#define LASER_1 OCR0A
#define LED_FRONT_B OCR0B
#define IR_CLOCK_DUTY_CYCLE OCR1A
#define LED_FRONT_G OCR1B
#define LED_FRONT_R OCR2A
#define LED_FRONT_W OCR2B
#define BUTTON_0 PB7
#define BUTTON_1 PB6
#define BUTTON_2 PD4
#define ONOFF PB0

//----------------------------  ----------------------------

long map(long x, long in_min, long in_max, long out_min, long out_max)
{
  return (x - in_min) * (out_max - out_min + 1) / (in_max - in_min + 1) + out_min;
}

/* uint8_t taster(volatile uint8_t *port, uint8_t pin)
{
	if(!(*port & (1 << pin))){
		//LED_FRONT_R=240;
		return 1;
	}else{
		//LED_FRONT_R=255;
		return 0;
	}
}
 */
uint8_t laser_2(uint8_t on){
	static uint8_t laser_2_status;
	if(on == 1){
		PORTD |= (1 << LASER_2);
		laser_2_status = on;
	}else if(on == 0){
		PORTD &= ~(1 << LASER_2);
		laser_2_status = on;
	}
	return laser_2_status;
}

int main(void){
	// 12 PB0 LASER_R  ---- NICHT MEHR ----
	// 11 PD7 LASER_2								(Laser)
	// 10 PD6 LASER_1		OC0A	Timer0	 8 Bit	(Haptik)
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
	
/* 	//Timer 0: Mode 3: Fast PWM, TOP: 0xFF, Update of OCRx: Bottom, TOV1 Flag set on: TOP, Prescaler: 1, Set OC0x on Compare Match
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
	*/
	//switch off all light
	// LED_FRONT_R=255;
	// LED_FRONT_G=ICR1;
	// LED_FRONT_B=255;
	// LED_FRONT_W=255;
	// LASER_1=255;
	//PORTB |= (1 << PB0); //an
	
	sei(); // enable Interrupts global
		
 	while(1){
		//LED_FRONT_R = 255-1;
		// LED_FRONT_G = ICR1-map(2, 0, 255, 0, ICR1); //0 bis ICR1
		// LED_FRONT_B = 255-1;
		// LED_FRONT_W = 255-1;
		laser_2(1);
		// LASER_1 = 255; //haptik
		
		_delay_ms(255);
		
		//LED_FRONT_R = 255-0;
		// LED_FRONT_G = ICR1-map(0, 0, 255, 0, ICR1); //0 bis ICR1
		// LED_FRONT_B = 255-0;
		// LED_FRONT_W = 255-0;
		laser_2(0);
		// LASER_1 = 0; //haptik
		

		//laser_2(taster(&PINB, BUTTON_0));
		//button_buffer.button_1 = taster(&PINB, BUTTON_1);
		//button_buffer.button_2 = taster(&PIND, BUTTON_2);
	}
}
