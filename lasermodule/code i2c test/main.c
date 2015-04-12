#define F_CPU 8000000

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>
#include <string.h>
#include <util/delay.h>
#include "twislave.h"

//---------------------------- i2c Settings ----------------------------

#define I2C_BUS_ADRESS 0x03

//i2c-register	Funktion		Modul
//0				LED_FRONT_R		LM
//1				LED_FRONT_G		LM
//2				LED_FRONT_B		LM
//3				LED_FRONT_W		LM
//4				LASER_R			LM
//5				LASER_G			LM
//6				LASER_B			LM
//7				Haptik 			LM/TM
//...
//10			Button_0		LM
//11			Button_1		LM
//12			Button_2		LM
//...
//20			Shoot_Enable	LM
//21			Shoot_PlayerID	LM
//22			Shoot_Damage	LM
//23			Shoot_Duration	LM
//24			Shoot_Color_R	LM
//25			Shoot_Color_G	LM
//26			Shoot_Color_B	LM
//...
//30			HIT_Enable		LM/TM
//31			HIT_PlayerID	LM/TM
//32			HIT_DMG			LM/TM
//...
//40			V_BATT 16 bit	LM
//41			V_BATT 16 bit	LM
//42			LDR 16 bit		LM
//43			LDR 16 bit		LM
//...
//50			LED_10MM_R		TM
//51			LED_10MM_G		TM
//52			LED_10MM_B		TM

#define LED_FRONT_REG 0
typedef struct{
	uint8_t r;
	uint8_t g;
	uint8_t b;
	uint8_t w;
} led_front_t;
volatile led_front_t led_front_buffer;

#define LASER_REG 4
typedef struct{
	uint8_t r;
	uint8_t g;
	uint8_t b;
} laser_t;
volatile laser_t laser_buffer;

#define HAPTIK_REG 7
typedef struct{
	uint8_t vibrate;
} haptik_t;
volatile haptik_t haptik_buffer;

#define BUTTON_REG 10
typedef struct{
	uint8_t button_0;
	uint8_t button_1;
	uint8_t button_2;
} button_t;
volatile button_t button_buffer;

#define SHOOT_REG 20
typedef struct{
	uint8_t enable; //Fire once if written > 0
	uint8_t playerid;
	uint8_t damage;
	uint8_t duration; //Laser light duration
	uint8_t laser_r;
	uint8_t laser_g;
	uint8_t laser_b;
} shoot_t;
volatile shoot_t shoot_buffer;

#define HIT_REG 30
typedef struct{
	uint8_t enable; //Hit if enabled
	uint8_t playerid;
	uint8_t damage;
} hit_t;
volatile hit_t hit_buffer;

#define MISC_REG 40
typedef struct{
	uint8_t v_batt_l;
	uint8_t v_batt_r;
	uint8_t ldr_l;
	uint8_t ldr_r;
} misc_t;
volatile misc_t misc_buffer;

volatile uint8_t i2c_last_reg_access = -1;

void i2c_slave_poll_buffer(unsigned char reg_addr, volatile unsigned char** buffer, volatile unsigned char* buffer_length){
	// switch(reg_addr){
		// case LED_FRONT_REG ... LED_FRONT_REG + sizeof(led_front_t) - 1:
			// *buffer        = &((uint8_t *)&led_front_buffer)[reg_addr-LED_FRONT_REG];
			// *buffer_length = (sizeof(led_front_t)-reg_addr);
			// i2c_last_reg_access = LED_FRONT_REG;
			// break;
		// case LASER_REG ... LASER_REG + sizeof(laser_front_t) - 1:
			// *buffer        = &((uint8_t *)&laser_front_buffer)[reg_addr-LASER_REG];
			// *buffer_length = (sizeof(laser_front_t)-reg_addr);
			// i2c_last_reg_access = LASER_REG;
			// break;


	if ((reg_addr >= LED_FRONT_REG) && (reg_addr < (LED_FRONT_REG + sizeof(led_front_t)))){
		*buffer        = &((uint8_t *)&led_front_buffer)[reg_addr-LED_FRONT_REG];
		*buffer_length = sizeof(led_front_t)-(reg_addr-LED_FRONT_REG);
		i2c_last_reg_access = LED_FRONT_REG;
	} else if ((reg_addr >= LASER_REG) && (reg_addr < (LASER_REG + sizeof(laser_t)))){
		*buffer        = &((uint8_t *)&laser_buffer)[reg_addr-LASER_REG];
		*buffer_length = sizeof(laser_t)-(reg_addr-LASER_REG);
		i2c_last_reg_access = LASER_REG;
	} else if ((reg_addr >= BUTTON_REG) && (reg_addr < (BUTTON_REG + sizeof(button_t)))){ //10-12
		*buffer        = &((uint8_t *)&button_buffer)[reg_addr-BUTTON_REG];
		*buffer_length = sizeof(button_t)-(reg_addr-BUTTON_REG);
		i2c_last_reg_access = BUTTON_REG;
	} else if ((reg_addr >= HAPTIK_REG) && (reg_addr < (HAPTIK_REG + sizeof(haptik_t)))){
		*buffer        = &((uint8_t *)&haptik_buffer)[reg_addr-HAPTIK_REG];
		*buffer_length = sizeof(haptik_t)-(reg_addr-HAPTIK_REG);
		i2c_last_reg_access = HAPTIK_REG;
	} else if ((reg_addr >= SHOOT_REG) && (reg_addr < (SHOOT_REG + sizeof(shoot_t)))){
		*buffer        = &((uint8_t *)&shoot_buffer)[reg_addr-SHOOT_REG];
		*buffer_length = sizeof(shoot_t)-(reg_addr-SHOOT_REG);
		i2c_last_reg_access = SHOOT_REG;
	} else if ((reg_addr >= HIT_REG) && (reg_addr < (HIT_REG + sizeof(hit_t)))){
		*buffer        = &((uint8_t *)&hit_buffer)[reg_addr-HIT_REG];
		*buffer_length = sizeof(hit_t)-(reg_addr-HIT_REG);
		i2c_last_reg_access = HIT_REG;
	} else if ((reg_addr >= MISC_REG) && (reg_addr < (MISC_REG + sizeof(misc_t)))){
		*buffer        = &((uint8_t *)&misc_buffer)[reg_addr-MISC_REG];
		*buffer_length = sizeof(misc_t)-(reg_addr-MISC_REG);
		i2c_last_reg_access = MISC_REG;
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

int main(void){
	cli();

	//i2c init
	init_twi_slave(I2C_BUS_ADRESS<<1);
	
	sei(); // enable Interrupts global
 	while(1){		
		_delay_ms(255);
	}
}
