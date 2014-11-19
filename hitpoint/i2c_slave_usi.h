/*##################################################################################################
	Name	: USI TWI Slave driver
	Version	: 1.2  - stabil running
	autor	: Martin Junghans	jtronics@gmx.de
	page	: www.jtronics.de
	License	: GNU General Public License 

	Created from Atmel source files for Application Note AVR312: Using the USI Module 
	as an I2C slave like a I2C-EEPROM.

	LICENSE:    Copyright (C) 2010 Marin Junghans

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
	
*/
#ifndef _USI_TWI_SLAVE_H_
#define _USI_TWI_SLAVE_H_

//################################################ prototypes
void    usi_i2c_init(uint8_t ownAddress);	// send Slaveadresse

extern void i2c_slave_poll_buffer(unsigned char reg_addr, volatile unsigned char** buffer, volatile unsigned char* buffer_length);
extern void i2c_slave_write_complete(void);
extern void i2c_slave_read_complete(void);
 
//################################################ variablen

#endif  // ifndef _USI_TWI_SLAVE_H_
