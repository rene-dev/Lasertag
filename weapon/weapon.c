#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main(int argc, char *argv[]){
        int file,i;
        int addr = 0x10;
        char buf[10] = {0x00,0xff,0xff,0xff};
        if(argc >= 3){
                for(i = 1;i<=3;i++){
                        buf[i] = atoi(argv[i]);
                }
        }
        char *filename = "/dev/i2c-1";
        if ((file = open(filename, O_RDWR)) < 0) {
                /* ERROR HANDLING: you can check errno to see what went wrong */
                perror("Failed to open the i2c bus");
                exit(1);
        }
        if (ioctl(file, I2C_SLAVE, addr) < 0) {
                printf("Failed to acquire bus access and/or talk to slave.\n");
                /* ERROR HANDLING; you can check errno to see what went wrong */
                exit(1);
        }
        if (write(file,buf,4) != 4) {
                /* ERROR HANDLING: i2c transaction failed */
                printf("Failed to write to the i2c bus.\n");
                printf(strerror(errno));
                printf("\n\n");
        }
}