#include <stdlib.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <util/delay.h>

#include "twislave.h"

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#define SLAVE_ADRESSE 0x50

int main(void)
{
	cli();
	init_twi_slave(SLAVE_ADRESSE);
	sei();

	while(1)
    {
		txbuffer[0]++;
		_delay_ms(50);
	}
}