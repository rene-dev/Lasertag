/*#################################################################################################
	Name	: USI TWI Slave driver - I2C/TWI-EEPROM
	Version	: 1.2  - stabil running
	autor	: Martin Junghans	jtronics@gmx.de
	page	: www.jtronics.de
	License	: GNU General Public License 

	Created from Atmel source files for Application Note AVR312: Using the USI Modulea 
	as an I2C slave like a I2C-EEPROM.
//################################################################################################*/

#include <avr/io.h>
#include <avr/interrupt.h>
#include "i2c_slave_usi.h"

//###################### device defines
#if 	defined( __AVR_ATtiny2313__ )
		#define DDR_USI             DDRB
		#define PORT_USI            PORTB
		#define PIN_USI             PINB
		#define PORT_USI_SDA        PB5
		#define PORT_USI_SCL        PB7
		#define PIN_USI_SDA         PINB5
		#define PIN_USI_SCL         PINB7
		#define USI_START_COND_INT  USISIF
		#define USI_START_VECTOR    USI_START_vect
		#define USI_OVERFLOW_VECTOR USI_OVERFLOW_vect

#elif 	defined( __AVR_ATtiny25__ ) | \
		defined( __AVR_ATtiny45__ ) | \
		defined( __AVR_ATtiny85__ )
		#define DDR_USI             DDRB
		#define PORT_USI            PORTB
		#define PIN_USI             PINB
		#define PORT_USI_SDA        PB0
		#define PORT_USI_SCL        PB2
		#define PIN_USI_SDA         PINB0
		#define PIN_USI_SCL         PINB2
		#define USI_START_COND_INT  USICIF
		#define USI_START_VECTOR    USI_START_vect
		#define USI_OVERFLOW_VECTOR USI_OVF_vect

#elif 	defined( __AVR_ATtiny44__ )
		#define DDR_USI             DDRA
		#define PORT_USI            PORTA
		#define PIN_USI             PINA
		#define PORT_USI_SDA        PA6
		#define PORT_USI_SCL        PA4
		#define PIN_USI_SDA         PINA6
		#define PIN_USI_SCL         PINA4
		#define USI_START_COND_INT  USISIF
		#define USI_START_VECTOR    USI_STR_vect
		#define USI_OVERFLOW_VECTOR USI_OVF_vect

#elif 	defined( __AVR_ATtiny26__ )
		#define DDR_USI             DDRB
		#define PORT_USI            PORTB
		#define PIN_USI             PINB
		#define PORT_USI_SDA        PB0
		#define PORT_USI_SCL        PB2
		#define PIN_USI_SDA         PINB0
		#define PIN_USI_SCL         PINB2
		#define USI_START_COND_INT  USISIF
		#define USI_START_VECTOR    USI_STRT_vect
		#define USI_OVERFLOW_VECTOR USI_OVF_vect

#elif 	defined( __AVR_ATtiny261__ ) | \
		defined( __AVR_ATtiny461__ ) | \
		defined( __AVR_ATtiny861__ )
		#define DDR_USI             DDRB
		#define PORT_USI            PORTB
		#define PIN_USI             PINB
		#define PORT_USI_SDA        PB0
		#define PORT_USI_SCL        PB2
		#define PIN_USI_SDA         PINB0
		#define PIN_USI_SCL         PINB2
		#define USI_START_COND_INT  USISIF
		#define USI_START_VECTOR    USI_START_vect
		#define USI_OVERFLOW_VECTOR USI_OVF_vect

#elif 	defined( __AVR_ATmega165__ ) | \
		defined( __AVR_ATmega325__ ) | \
		defined( __AVR_ATmega3250__ ) | \
		defined( __AVR_ATmega645__ ) | \
		defined( __AVR_ATmega6450__ ) | \
		defined( __AVR_ATmega329__ ) | \
		defined( __AVR_ATmega3290__ )
		#define DDR_USI             DDRE
		#define PORT_USI            PORTE
		#define PIN_USI             PINE
		#define PORT_USI_SDA        PE5
		#define PORT_USI_SCL        PE4
		#define PIN_USI_SDA         PINE5
		#define PIN_USI_SCL         PINE4
		#define USI_START_COND_INT  USISIF
		#define USI_START_VECTOR    USI_START_vect
		#define USI_OVERFLOW_VECTOR USI_OVERFLOW_vect

#elif 	defined( __AVR_ATmega169__ )
		#define DDR_USI             DDRE
		#define PORT_USI            PORTE
		#define PIN_USI             PINE
		#define PORT_USI_SDA        PE5
		#define PORT_USI_SCL        PE4
		#define PIN_USI_SDA         PINE5
		#define PIN_USI_SCL         PINE4
		#define USI_START_COND_INT  USISIF
		#define USI_START_VECTOR    USI_START_vect
		#define USI_OVERFLOW_VECTOR USI_OVERFLOW_vect
		
#else
		#error "no USI-Slave definition for MCU available"
 
#endif

//###################### functions implemented as macros
#define SET_USI_TO_SEND_ACK( ) 	{ USIDR = 0; \
								DDR_USI |= ( 1 << PORT_USI_SDA ); \
								USISR = ( 0 << USI_START_COND_INT ) | \
								( 1 << USIOIF ) | ( 1 << USIPF ) | \
								( 1 << USIDC )| \
								( 0x0E << USICNT0 );}

								// prepare ACK 
								// set SDA as output 
								// clear all interrupt flags, except Start Cond 
								// set USI counter to shift 1 bit
								
#define SET_USI_TO_SEND_NACK( ) { USIDR = 0; \
								DDR_USI &= (unsigned char)~( 1 << PORT_USI_SDA ); \
								USISR = ( 0 << USI_START_COND_INT ) | \
								( 1 << USIOIF ) | ( 1 << USIPF ) | \
								( 1 << USIDC )| \
								( 0x0E << USICNT0 );}

								// prepare ACK 
								// set SDA as output 
								// clear all interrupt flags, except Start Cond 
								// set USI counter to shift 1 bit

#define SET_USI_TO_READ_ACK( ) 	{ USIDR = 0; \
								DDR_USI &= ~( 1 << PORT_USI_SDA ); \
								USISR = ( 0 << USI_START_COND_INT ) | \
								( 1 << USIOIF) | \
								( 1 << USIPF ) | \
								( 1 << USIDC ) | \
								( 0x0E << USICNT0 );}


								// set SDA as input 
								// prepare ACK 
								// clear all interrupt flags, except Start Cond 
								// set USI counter to shift 1 bit 

#define SET_USI_TO_TWI_START_CONDITION_MODE( ) { \
								USICR = ( 1 << USISIE ) | ( 0 << USIOIE ) | \
								( 1 << USIWM1 ) | ( 0 << USIWM0 ) | \
								( 1 << USICS1 ) | ( 0 << USICS0 ) | ( 0 << USICLK ) | \
								( 0 << USITC ); \
								USISR = ( 0 << USI_START_COND_INT ) | ( 1 << USIOIF ) | ( 1 << USIPF ) | \
								( 1 << USIDC ) | ( 0x0 << USICNT0 ); }

								// enable Start Condition Interrupt, disable Overflow Interrupt 
								// set USI in Two-wire mode, no USI Counter overflow hold 
								// Shift Register Clock Source = External, positive edge 
								// 4-Bit Counter Source = external, both edges 
								// no toggle clock-port pin 
								// clear all interrupt flags, except Start Cond 

#define SET_USI_TO_SEND_DATA( ) { DDR_USI |=  ( 1 << PORT_USI_SDA ); \
								USISR = ( 0 << USI_START_COND_INT ) | ( 1 << USIOIF ) | ( 1 << USIPF ) | \
								( 1 << USIDC) | \
								( 0x0 << USICNT0 ); \
								}
								// set SDA as output 
								// clear all interrupt flags, except Start Cond 
								// set USI to shift out 8 bits 

#define SET_USI_TO_READ_DATA( ) { DDR_USI &= ~( 1 << PORT_USI_SDA ); \
								USISR =	( 0 << USI_START_COND_INT ) | ( 1 << USIOIF ) | \
								( 1 << USIPF ) | ( 1 << USIDC ) | \
								( 0x0 << USICNT0 ); \
								}

								// set SDA as input 
								// clear all interrupt flags, except Start Cond 
								// set USI to shift out 8 bits 

#define cbi(ADDRESS,BIT) 	((ADDRESS) &= ~(1<<(BIT)))	// clear Bit

//###################### typedef's
typedef enum
	{
	USI_SLAVE_CHECK_ADDRESS                = 0x00,
	USI_SLAVE_SEND_DATA                    = 0x01,
	USI_SLAVE_REQUEST_REPLY_FROM_SEND_DATA = 0x02,
	USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA   = 0x03,
	USI_SLAVE_REQUEST_DATA                 = 0x04,
	USI_SLAVE_GET_DATA_AND_SEND_ACK        = 0x05
	} overflowState_t;

//###################### local variables
 volatile uint8_t         	slaveAddress;
 volatile overflowState_t 	overflowState;

 volatile unsigned char* current_buffer = 0;
 volatile unsigned char  current_length = 0;
 volatile unsigned char  buffer_adr; 					// "Adressregister" für den Buffer

 
//################################################################################################## initialise USI for TWI slave mode
void usi_i2c_init(  uint8_t ownAddress)
{
  slaveAddress = ownAddress;

  // In Two Wire mode (USIWM1, USIWM0 = 1X), the slave USI will pull SCL
  // low when a start condition is detected or a counter overflow (only
  // for USIWM1, USIWM0 = 11).  This inserts a wait state.  SCL is released
  // by the ISRs (USI_START_vect and USI_OVERFLOW_vect).
  DDR_USI |= ( 1 << PORT_USI_SCL ) | ( 1 << PORT_USI_SDA );	  // Set SCL and SDA as output
  PORT_USI |= ( 1 << PORT_USI_SCL );  // set SCL high
  PORT_USI |= ( 1 << PORT_USI_SDA );  // set SDA high
  DDR_USI &= ~( 1 << PORT_USI_SDA );  // Set SDA as input
  USICR =
       ( 1 << USISIE ) |       					// enable Start Condition Interrupt
       ( 0 << USIOIE ) |       					// disable Overflow Interrupt
       ( 1 << USIWM1 ) | ( 0 << USIWM0 ) |     // set USI in Two-wire mode, no USI Counter overflow hold
       ( 1 << USICS1 ) | ( 0 << USICS0 ) | ( 0 << USICLK ) |       // Shift Register Clock Source = external, positive edge 4-Bit Counter Source = external, both edges
       ( 0 << USITC );       					// no toggle clock-port pin
  USISR = ( 1 << USI_START_COND_INT ) | ( 1 << USIOIF ) | ( 1 << USIPF ) | ( 1 << USIDC );  // clear all interrupt flags and reset overflow counter
}

//################################################################################################## USI Start Condition ISR
ISR( USI_START_VECTOR )
{
	overflowState = USI_SLAVE_CHECK_ADDRESS;			// set default starting conditions for new TWI package
	DDR_USI &= ~( 1 << PORT_USI_SDA );					// set SDA as input

	// wait for SCL to go low to ensure the Start Condition has completed (the
	// start detector will hold SCL low ) - if a Stop Condition arises then leave
	// the interrupt to prevent waiting forever - don't use USISR to test for Stop
	// Condition as in Application Note AVR312 because the Stop Condition Flag is
	// going to be set from the last TWI sequence
	
	while (	( PIN_USI & ( 1 << PIN_USI_SCL ) ) &&	!( ( PIN_USI & ( 1 << PIN_USI_SDA ) ) ));// SCL his high and SDA is low

	if ( !( PIN_USI & ( 1 << PIN_USI_SDA ) ) )
		{	// a Stop Condition did not occur
		USICR =
		( 1 << USISIE ) |								// keep Start Condition Interrupt enabled to detect RESTART
		( 1 << USIOIE ) |								// enable Overflow Interrupt
		( 1 << USIWM1 ) | ( 1 << USIWM0 ) |			// set USI in Two-wire mode, hold SCL low on USI Counter overflow
		( 1 << USICS1 ) | ( 0 << USICS0 ) | ( 0 << USICLK ) |	// 4-Bit Counter Source = external, both edges; Clock Source = External, positive edge	
		( 0 << USITC );									// no toggle clock-port pin

		}
	else
		{	// a Stop Condition did occur
		USICR =
		( 1 << USISIE ) |								// enable Start Condition Interrupt
		( 0 << USIOIE ) |								// disable Overflow Interrupt
		( 1 << USIWM1 ) | ( 0 << USIWM0 ) |			// set USI in Two-wire mode, no USI Counter overflow hold
		( 1 << USICS1 ) | ( 0 << USICS0 ) | ( 0 << USICLK ) |		// 4-Bit Counter Source = external, both edges; Clock Source = external, positive edge
		( 0 << USITC );									// no toggle clock-port pin
		} 

	USISR =
	( 1 << USI_START_COND_INT ) | ( 1 << USIOIF ) |	// clear interrupt flags - resetting the Start Condition Flag will release SCL
	( 1 << USIPF ) |( 1 << USIDC ) |
	( 0x0 << USICNT0);									// set USI to sample 8 bits (count 16 external SCL pin toggles)
}

//################################################################################################## ISR( USI_OVERFLOW_VECTOR )
ISR( USI_OVERFLOW_VECTOR )	//Handles all the communication. Only disabled when waiting for a new Start Condition.
{
	uint8_t data=0;
	switch ( overflowState )
		{
//###### Address mode: check address and send ACK (and next USI_SLAVE_SEND_DATA) if OK, else reset USI
		case USI_SLAVE_CHECK_ADDRESS:
			if (USIDR == 0 || (USIDR & ~1) == slaveAddress) 		
				{
				if (  USIDR & 0x01 )
					{
					overflowState = USI_SLAVE_SEND_DATA;		// Master Write Data Mode - Slave transmit
					}
				else
					{
					overflowState = USI_SLAVE_REQUEST_DATA;		// Master Read Data Mode - Slave receive
					current_buffer=0; //Buffer undefiniert
					current_length=0;
					} // end if
				SET_USI_TO_SEND_ACK();
				}
			else
				{
				SET_USI_TO_TWI_START_CONDITION_MODE();
				}
			break;


//###### Master Write Data Mode - Slave transmit:
		// check reply and goto USI_SLAVE_SEND_DATA if OK, 
		// else reset USI
		case USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA:
			if ( USIDR )
				{
				SET_USI_TO_TWI_START_CONDITION_MODE();	// if NACK, the master does not want more data
				return;
				}
	
		// from here we just drop straight into USI_SLAVE_SEND_DATA if the master sent an ACK
		case USI_SLAVE_SEND_DATA:
			if (current_buffer == 0) { 				//zuvor keine Leseadresse angegeben!
				USIDR = 0;
			} else {
				USIDR = current_buffer[buffer_adr];	//Datenbyte senden 
				buffer_adr++; 						//bufferadresse für nächstes Byte weiterzählen
			}
			overflowState = USI_SLAVE_REQUEST_REPLY_FROM_SEND_DATA;
			SET_USI_TO_SEND_DATA( );
			
			if (current_buffer != 0 && buffer_adr == current_length){
				i2c_slave_write_complete();
			}
			break;

		// set USI to sample reply from master
		// next USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA
		case USI_SLAVE_REQUEST_REPLY_FROM_SEND_DATA:
			overflowState = USI_SLAVE_CHECK_REPLY_FROM_SEND_DATA;
			SET_USI_TO_READ_ACK( );
			break;




//###### Master Read Data Mode - Slave receive:

		// set USI to sample data from master,
		// next USI_SLAVE_GET_DATA_AND_SEND_ACK
		case USI_SLAVE_REQUEST_DATA:
			overflowState = USI_SLAVE_GET_DATA_AND_SEND_ACK;
			SET_USI_TO_READ_DATA( );
			break;

		// copy data from USIDR and send ACK
		// next USI_SLAVE_REQUEST_DATA
		case USI_SLAVE_GET_DATA_AND_SEND_ACK:
			data = USIDR; 							//Empfangene Daten auslesen
			if (current_buffer == 0){ 				//erster Zugriff, Bufferposition setzen
				i2c_slave_poll_buffer(data, &current_buffer, &current_length);
				buffer_adr = 0;
			} else {								//weiterer Zugriff, Daten empfangen
				current_buffer[buffer_adr] = data;	//Daten in Buffer schreiben
				buffer_adr++; 						//Buffer-Adresse weiterzählen für nächsten Schreibzugriff
			}
			overflowState = USI_SLAVE_REQUEST_DATA;	// next USI_SLAVE_REQUEST_DATA
			
			if (current_length == buffer_adr){
				//Answer last byte with NACK.
				SET_USI_TO_SEND_NACK( );
				i2c_slave_write_complete();
			} else {
				SET_USI_TO_SEND_ACK( );
			}
			break;


		}// end switch
}// end ISR( USI_OVERFLOW_VECTOR )
