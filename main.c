#include <avr/io.h>
#include <util/delay.h>

#define V01

#ifdef V01
#define LED1R PB6
#define LED1G PB4
#define LED1B PB3
#define LED2R PB2
#define LED2G PB1
#define LED2B PB0

#define LED1R_PORT PORTB
#define LED1G_PORT PORTB
#define LED1B_PORT PORTB
#define LED2R_PORT PORTB
#define LED2G_PORT PORTB
#define LED2B_PORT PORTB

#define LED1R_DDR DDRB
#define LED1G_DDR DDRB
#define LED1B_DDR DDRB
#define LED2R_DDR DDRB
#define LED2G_DDR DDRB
#define LED2B_DDR DDRB
#endif

void long_delay(uint16_t ms)
{
    for(; ms>0; ms--) _delay_ms(1);
}

int main(void) {
	LED1R_DDR |= (1 << LED1R);
	LED1G_DDR |= (1 << LED1G);
	LED1B_DDR |= (1 << LED1B);
	LED2R_DDR |= (1 << LED2R);
	LED2G_DDR |= (1 << LED2G);
	LED2B_DDR |= (1 << LED2B);
	
	LED1R_PORT &= ~(1 << LED1R);
	LED1G_PORT &= ~(1 << LED1G);
	LED1B_PORT &= ~(1 << LED1B);
	LED2R_PORT &= ~(1 << LED2R);
	LED2G_PORT &= ~(1 << LED2G);
	LED2B_PORT &= ~(1 << LED2B);
	
	//DDRB = 0x5f;
    LED1R_PORT ^= ( 1 << LED1R );
	LED1G_PORT ^= ( 1 << LED1G );
	LED1B_PORT ^= ( 1 << LED1B );
    while( 1 )
    {                
        LED1R_PORT ^= ( 1 << LED1R );
		LED1G_PORT ^= ( 1 << LED1G );
		LED1B_PORT ^= ( 1 << LED1B );
		LED2R_PORT ^= ( 1 << LED2R );
		LED2G_PORT ^= ( 1 << LED2G );
		LED2B_PORT ^= ( 1 << LED2B );
        long_delay(500);
    }
	
	while(1){}
	return 0;
}

