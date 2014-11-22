#include <stdint.h>
//LED pin nummern an port B

#define PWM_CHANNELS  7                // Anzahl der PWM-Kanäle

#define LED1R 6
#define LED1G 4
#define LED1B 3
#define LED2R 2
#define LED2G 1
#define LED2B 0

extern uint8_t  pwm_setting[];

void pwm_init(void);
void pwm_update(void);
