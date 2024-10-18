#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#ifdef COUNT
    #define NO_SHOP COUNT
#else
    #define NO_SHOP 0x0
#endif

void initialize(){
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

void getInp(char * buf, unsigned int size) {
    int n = read(0, buf, size);
    if (n <= 0) {
        perror("Read Error");
        exit(1);
    }
    buf[n-1] = '\0';
}

unsigned int getInt() {
    char buf[32];
    getInp(buf, 31);
    return atoi(buf);
}

int main() {
    initialize();
    printf("Welcome to the fruit market\nWhich shop do you want to enter: ");
    
    unsigned int shop = getInt();
    
    if (shop < NO_SHOP) {

        char storeroom_path[256];
        snprintf(storeroom_path, sizeof(storeroom_path), "storeroom-%u", shop);
        if (chdir(storeroom_path) != 0) {
            fprintf(stderr, "Failed to change directory to storeroom: %s\n", strerror(errno));
            exit(1);
        }
        

        char shop_path[256];
        snprintf(shop_path, sizeof(shop_path), "../shop-%u", shop);
        char *args[] = {shop_path, NULL};
        execv(shop_path, args);
        
        fprintf(stderr, "Failed to execute shop: %s\n", strerror(errno));
        exit(1);
    } else {
        fprintf(stderr, "Invalid shop number. Please choose a number between 0 and %d\n", NO_SHOP);
    }
    
    return 0;
}
