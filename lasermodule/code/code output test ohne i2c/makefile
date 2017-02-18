MCU = atmega328
#FREQ=8000000
TRG = main
SRC = $(TRG).c twislave.c

CFLAGS	= -g -Os -Wall -Wstrict-prototypes -mcall-prologues -mmcu=$(MCU) -DMCU=$(MCU) -std=c99
#-DF_CPU=$(FREQ)
LDFLAGS = -mmcu=$(MCU)

CC	= avr-gcc
RM	= rm -f
RN	= mv
CP	= cp
OBJCOPY	= avr-objcopy
SIZE	= avr-size
INCDIR = .
FORMAT = ihex	
OBJ	= $(SRC:.c=.o)

all: $(TRG).elf $(TRG).bin $(TRG).hex $(TRG).eep $(TRG).ok
%.o : %.c 
	$(CC) -c $(CFLAGS) -I$(INCDIR) $< -o $@

%.s : %.c
	$(CC) -S $(CFLAGS) -I$(INCDIR) $< -o $@


%.elf: $(OBJ)
	$(CC) $(OBJ) $(LIB) $(LDFLAGS) -o $@
	
%.bin: %.elf
	$(OBJCOPY) -O binary -R .eeprom $< $@

%.hex: %.elf
	$(OBJCOPY) -O $(FORMAT) -R .eeprom $< $@

%.eep: %.elf
	$(OBJCOPY) -j .eeprom --set-section-flags=.eeprom="alloc,load" --change-section-lma .eeprom=0 -O $(FORMAT) $< $@

$(TRG).o : $(TRG).c

%ok:
	$(SIZE) -C --mcu=$(MCU) $(TRG).elf

clean:
	$(RM) $(OBJ)
	$(RM) $(SRC:.c=.s)
	$(RM) $(SRC:.c=.lst)
	$(RM) $(TRG).map
	$(RM) $(TRG).elf
	$(RM) $(TRG).cof
	$(RM) $(TRG).obj
	$(RM) $(TRG).a90
	$(RM) $(TRG).sym
	$(RM) $(TRG).eep
	$(RM) $(TRG).hex
	$(RM) $(TRG).bin
	
size88:
	$(SIZE) -C --mcu=atmega88 $(TRG).elf
size328:
	$(SIZE) -C --mcu=atmega328 $(TRG).elf
load88: $(TRG).hex
	avrdude -c usbasp -p m88 -U flash:w:main.hex
load328: $(TRG).hex
	avrdude -c usbasp -p m328 -U flash:w:main.hex
fuses88:
	avrdude -c usbasp -p m88 -B 150 -U lfuse:w:0xe2:m -U hfuse:w:0xd9:m -U efuse:w:0x07:m
fuses328:
	avrdude -c usbasp -p m328 -B 150 -U lfuse:w:0xe2:m -U hfuse:w:0xd9:m -U efuse:w:0x07:m
