#define UNICODE

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>
#include <stdio.h>
#include <assert.h>
#include <stdbool.h>

#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "Ws2_32.lib")



// 64bit PRNG from https://burtleburtle.net/bob/rand/smallprng.html
typedef DWORD64 u8;
typedef struct ranctx { u8 a; u8 b; u8 c; u8 d; } ranctx;

#define rot(x,k) (((x)<<(k))|((x)>>(64-(k))))
__forceinline u8 ranval( ranctx *x ) {
    u8 e = x->a - rot(x->b, 7);
    x->a = x->b ^ rot(x->c, 13);
    x->b = x->c + rot(x->d, 37);
    x->c = x->d + e;
    x->d = e + x->a;
    return x->d;
}

void raninit( ranctx *x, u8 seed ) {
    u8 i;
    x->a = 0xf1ea5eed, x->b = x->c = x->d = seed;
    for (i=0; i<20; ++i) {
        (void)ranval(x);
    }
}

#define PORT "27015"

bool init_wsock(){
    WSADATA wsaData;
    return !WSAStartup(MAKEWORD(2,2), &wsaData);
}

SOCKET getsock(){
    struct addrinfo *result = NULL, hints = {0};
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags = AI_PASSIVE;

    SOCKET lsock = INVALID_SOCKET;

    if(getaddrinfo(NULL, PORT, &hints, &result)) goto ret;

    lsock = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if(lsock==INVALID_SOCKET) goto ret;

    if(bind(lsock,result->ai_addr,(int)result->ai_addrlen) == SOCKET_ERROR){closesocket(lsock); lsock=INVALID_SOCKET; goto ret;}
    if(listen(lsock,SOMAXCONN) == SOCKET_ERROR) {closesocket(lsock); lsock=INVALID_SOCKET;}
ret:
    if(result) freeaddrinfo(result);
    return lsock;
}

void gameloop(SOCKET csock);

void accept_dispatch(SOCKET lsock){
    SOCKET csock = INVALID_SOCKET;
    struct sockaddr_in addr={0};
    socklen_t socklen = sizeof(addr);
    while((csock=accept(lsock,(struct sockaddr*)&addr,&socklen))!=INVALID_SOCKET){
        int recv_to = 2500;
        setsockopt(csock,SOL_SOCKET,SO_RCVTIMEO,(const char *)&recv_to,sizeof(recv_to));
        if(!CreateThread(0, 0, (LPTHREAD_START_ROUTINE)&gameloop,(void*)csock, 0, 0)) break;
    }
}

typedef enum {
    NOTE,
    TELEPORT,
    SWORD,
    SCRIBE
} itm_typ;

typedef struct item{
    char* title;
    itm_typ type;
    void *data;
} item;

typedef struct room{
    char title[24];
    char desc[256];
    item* items[10];
    struct room* exits[4];
} room;

// Global game data, initialized in main thread. 

item starting_leaflet = {"A Crumbled Leaflet (inside the mailbox)",NOTE,"WELCOME TO ROKZ! Brave adventurer, your objective is to find the orc and to kill it by any means necessary."};

room whouse = {"WEST OF HOUSE","You are standing in an open field west of a white house, with a boarded front door. There is a mailbox with a note inside here.",
              {&starting_leaflet,0},{0}};

room nhouse = {"NORTH OF HOUSE","You are facing the north side of a white house. There is no door here and all windows are boarded up. There a short path here, you can see a large looming cave at a distance.",{0},{0}};

room center = {"AT CAVE ENTRANCE","You are in front of a dark looming cave. You can hear low growls of a large beast from inside. You also see the path through which you came here.",{0},{0}};

room shouse = {"SOUTH OF HOUSE","You are facing the south side of a white house. There is a window left open here and it seems like you can just about squeeze through the opening. There is also a grave marked with a wodden cross a little farther away from the house.",{0},{0}};

room ihouse = {"INSIDE THE HOUSE","You see a large living room with a cozy fireplace. There are two boarded up doors to what you assume are kitchen and the upper floor. There is a note here and a giant sword mounted by the fireplace.",{0},{0}};

room icave = {"INSIDE THE CAVE","Total darkness, you can see a small red glow coming from what appears to a large red blood diamond. Before you get a chance to observe it up close, you hear a monstrous roar in front of you.",{0},{0}};

room winner = {"INSIDE WINNERS ROOM","Congrats, you have beaten this short demo. You can record your victory message using the scribe or use the blue diamond to try the game out again.", {0}, {0}};


item marked_grave = {"A Wodden Cross",TELEPORT,&center};
item blood_diamond = {"A Red Diamond",TELEPORT,&winner};
item blue_diamond = {"A Blue Diamond",TELEPORT,&whouse};

item sword = {"A Normal Sword",SWORD,0};
item scribe = {"The Rat Scribe",SCRIBE,0};

char opt_str[]  =  "You currently see the following items in the room:";
char exit_str[] =  "You currently see the following exits:";
char no_opt[]   =  "There are no items in the room.";
char no_exit[]  =  "You cannot see any exits from the room.";


void send_resp(SOCKET sock, char* msg, int len){
    int bsent = send(sock,msg,len,0);
    if(bsent == SOCKET_ERROR) ExitThread(1);
    while(bsent!=len){
       int tmp = send(sock,&msg[bsent],len-bsent,0);
       if(tmp == SOCKET_ERROR) ExitThread(1);
       bsent += tmp;
    }
}

void send_resps(SOCKET sock, ...){
    va_list ap;
    va_start(ap,sock);
    char *msg = va_arg(ap,char*);
    char ibuf[1024] = {0};
    int iblen = 0;
    while(msg){
        if((iblen + strlen(msg))>1000) ExitThread(1);
        memcpy(&ibuf[iblen+4],msg,strlen(msg));
        iblen += (int)strlen(msg);
        msg = va_arg(ap,char*);
    }
    memcpy(ibuf,&iblen,sizeof(iblen));
    send_resp(sock,ibuf,iblen+4);
}

void send_raw(SOCKET sock, BYTE* arr, DWORD len){
    if(len>1000) ExitThread(1);
    char ibuf[1024] = {0};
    memcpy(&ibuf[4],arr,len); 
    memcpy(ibuf,&len,sizeof(len));
    send_resp(sock,ibuf,len+4);
}


void get_shrt(char* inp, char* out){
    int sz = (int)strlen(inp);
    out[0] = inp[0];
    int sht_idx = 1;

    for(int i=1; (sht_idx<3) && (i<sz); i++){
        if(inp[i] == ' ') out[sht_idx++] = inp[i+1];
    }
}

   



void gameloop(SOCKET csock){
#define SC(msg) send_resp((csock),(msg))
#define SCA(...) send_resps((csock), __VA_ARGS__, 0)

    room *curr_room = &whouse;

    // Username should at least 6 characters and should be printable
    // If any condition fails, break connection and exit thread
    char uname[12] = {0};
    SCA("\nEnter Username: ");
    printf("uname: %x\n",sizeof(uname)-1);
    if(recv(csock,uname,sizeof(uname)-1,0)<6) goto thread_exit;

    for(int i=0; uname[i]; i++){
        if((uname[i]<0x21) || (uname[i]>0x7E)) goto thread_exit;
    }

    // Anti-Debug: If debugger found, then exit
    // Should be easy to find and patch out
    BYTE b = *(BYTE*)0x7ffe02d4;
    if((b & 0x01) || (b & 0x02)) goto thread_exit;

    // Password should be atleast 8 bytes (if we are to use it as seed)
    // Also reject all null bytes (zero) as password
    u8 upass = 0;
    SCA("\nEnter Password: ");
    
    printf("upass: %x\n",sizeof(upass));
    if(recv(csock,(char*)&upass,sizeof(upass),0)!=sizeof(upass)) goto thread_exit;
    if(upass==0) goto thread_exit;

    u8 storedpass = 0;
    DWORD sp_sz = sizeof(storedpass);
    if(ERROR_SUCCESS==RegGetValueA(HKEY_CURRENT_USER,uname,"password",RRF_RT_REG_QWORD,0,&storedpass,&sp_sz)){
          if(memcmp(&storedpass,&upass,sp_sz)) goto thread_exit; 
    }else{
        // User not registered
        HKEY ukey = NULL;
        if(ERROR_SUCCESS != RegCreateKeyExA(HKEY_CURRENT_USER,uname,0,0,REG_OPTION_NON_VOLATILE,KEY_ALL_ACCESS,0,&ukey,0)) goto thread_exit;
        if(ERROR_SUCCESS != RegSetValueExA(ukey,"password",0,REG_QWORD,(BYTE*)&upass,sizeof(upass))) goto thread_exit;
        if(ERROR_SUCCESS != RegCloseKey(ukey)) goto thread_exit;
    }
    
    bool has_sword = false;
    
    // To ensure that a player doesn't hog the connection forever, we
    // kick a player after 16 inputs. 16 should be enough to get the flag.
    int num_inputs = 0;

    while(1){
        SCA(curr_room->title, "\n\n", curr_room->desc, "\n\n");
        
        // Entering the cave without the sword will result in instant death.
        // If user has sword, he wins but loses the sword.
        if(curr_room == &icave){
                if(!has_sword){
                        SCA("You are crushed by the weight of something humongous. You are dead. Better luck next time.\n\n");
                        break;
                }else{
                        SCA("You thrust your sword forward and pierce the heart of whatever monstrosity is in front of you.\n\n");
                        has_sword = false;
                }
        }

        if(curr_room->items[0]) {
            SCA(opt_str,"\n");
            for(int i=0; (i<10)&&(curr_room->items[i]); i++){
                item * it = curr_room->items[i];
                SCA("\t[*] ", it->title, "\n");
            }
        }else SCA(no_opt);

        if(curr_room->exits[0]){
            SCA(exit_str, "\n");
            for(int i=0; (i<4) && (curr_room->exits[i]); i++){
                room *exit = curr_room->exits[i];
                SCA("\t[*] ", exit->title, "\n");
            }
        }else SCA(no_exit);

        SCA("\n>");
        char inp[256] = {0};
        
        
        printf("inp: %x\n",sizeof(inp)-1);
        int rlen = recv(csock,inp,sizeof(inp)-1,0);
        if(rlen<=0) goto thread_exit;
        if(rlen>8) goto thread_exit;
        if(++num_inputs > 16) goto thread_exit;

        // Matches with strings and returns an int
        char* acts[] = {"mov ","read ","take "};
        int match = -1;

        for(int i=0; i<(sizeof(acts)/sizeof(acts[1])); i++){
            int alen = (int)strlen(acts[i]);
            if(rlen > alen){
                if(!memcmp(acts[i], inp, alen)) {
                    match = i;
                    break;
                }
            }
        }

        if(match<0) goto thread_exit; //break connection on no inp match
        if((!match) && (rlen!=7)) goto thread_exit;
        if((match) && (rlen!=8)) goto thread_exit;

        switch(match){
            case(0):{
                for(int i=0; (i<4) && (curr_room->exits[i]); i++){
                    char sht[4] = {0};
                    room* exit = curr_room->exits[i];
                    get_shrt(exit->title, sht);
                    if(!memcmp(&inp[4], sht, 3)){
                        curr_room = exit;
                        break;
                    }
                }
                break;
            };

            case(1):{
                for(int i=0;(i<10) && (curr_room->items[i]); i++){
                    item *it = curr_room->items[i];
                    if(it->type != NOTE) continue;
                    char sht[4] = {0}; // Move this out of switch?
                    get_shrt(it->title, sht);
                    if(!memcmp(&inp[5], sht, 3)){
                        SCA("\nIt reads:\n", it->data, "\n");
                        break;
                    }
                }

                break;
            }

           case(2):{
                for(int i=0;(i<10) && (curr_room->items[i]); i++){
                    item *it = curr_room->items[i];
                    if(it->type == NOTE) continue;
                    char sht[4] = {0}; // Move this out of switch?
                    get_shrt(it->title, sht);
                    if(!memcmp(&inp[5], sht, 3)){
                        if((it == &sword)){
                                SCA("\nYou grab the giant sword from the matlepiece and put it away in your backpack.\n");
                                has_sword = true;
                                break;
                        }else if((it == &scribe)){
                                SCA("\nThe rat squeaks in your hands and you somehow are able to make sense of it, it asks you to tell it the message so that it can be recorded.\n");
                                HKEY ukey = NULL;
                                if(ERROR_SUCCESS != RegCreateKeyExA(HKEY_CURRENT_USER,uname,0,0,REG_OPTION_NON_VOLATILE,KEY_ALL_ACCESS,0,&ukey,0)) goto thread_exit;
                                
                                BYTE prev_msg[256] = {0};
                                DWORD prev_sz = sizeof(prev_msg)-1;
                                if(ERROR_SUCCESS==RegGetValueA(ukey,0,"pmsg",RRF_RT_REG_BINARY,0,prev_msg,&prev_sz)){
                                        SCA("\nThe rat says that you had already recorded a message.\n");
                                        u8 seed_part = (upass>>32);
                                        u8 seed = (seed_part<<32) | seed_part;
                                        ranctx prs = {0};
                                        raninit(&prs,seed);

                                        for(int j=0; j<(prev_sz/sizeof(seed)); j++){
                                                u8 nval = ranval(&prs);
                                                BYTE* tptr = (BYTE*)&nval;
                                                for(int k=0; k<sizeof(seed); k++){
                                                        DWORD oi = (j*8)+k;
                                                        prev_msg[oi] = prev_msg[oi] ^ tptr[k];
                                                }
                                        }
                                        send_raw(csock,prev_msg,prev_sz);
                                }
  
                                SCA("\nPlease enter your message: ");
                                BYTE pmsg[256] = {0};
                                
                                printf("pmsg: %x\n",sizeof(pmsg)-1);
                                int pmsg_len = recv(csock,(char*)pmsg,sizeof(pmsg)-1,0);
                                // If we don't even have enough data for one round, reject input
                                if(pmsg_len<8) goto thread_exit;

                                // Note is the fact that if the message length is not 
                                // divisible by 8, the last few bytes are left unencrypted.
                                u8 seed_part = (upass>>32);
                                u8 seed = (seed_part<<32) | seed_part;
                                ranctx prs = {0};
                                raninit(&prs, seed);

                                for(int j=0; j<(pmsg_len/sizeof(seed)); j++){
                                        u8 nval = ranval(&prs);
                                        BYTE* tptr = (BYTE*)&nval;
                                        for(int k=0; k<sizeof(seed); k++){
                                                DWORD oi = (j*8)+k;
                                                pmsg[oi] = pmsg[oi] ^ tptr[k];
                                        }
                                }
                                
                                if(ERROR_SUCCESS != RegSetValueExA(ukey,"pmsg",0,REG_BINARY,pmsg,pmsg_len)) goto thread_exit;
                                if(ERROR_SUCCESS != RegCloseKey(ukey)) goto thread_exit;
                                break;

                        }else if(it == &blue_diamond){
                                SecureZeroMemory(uname,sizeof(uname));
                                SCA("\nEnter new name: ");
                                if(recv(csock,uname,sizeof(uname)-1,0)<6) goto thread_exit;                       
                                // We won't verify whether the new user exists or not.
                        }
                        SCA("\nAs you move your arm forward to touch it, it teleports you away to someplace else!\n");
                        curr_room = it->data;
                        break;
                    }
                }
               break;
           }
        }
    }


thread_exit:
    //Exited gameloop, shutdown connection
    shutdown(csock,SD_BOTH);
    closesocket(csock);
    //Thread Exit
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow){
//int main(){

    shouse.items[0] = &marked_grave;
    icave.items[0] = &blood_diamond;
    winner.items[0] = &blue_diamond;
    winner.items[1] = &scribe;
    ihouse.items[0] = &sword;


    whouse.exits[0] = &nhouse;
    whouse.exits[1] = &shouse;

    nhouse.exits[0] = &whouse;
    nhouse.exits[1] = &center;

    shouse.exits[0] = &whouse;
    shouse.exits[1] = &ihouse;

    ihouse.exits[0] = &shouse;

    center.exits[0] = &nhouse;
    center.exits[1] = &icave;

    icave.exits[0] = &center;

    if(!init_wsock()) return -1;
    SOCKET lsock = getsock();
    if(lsock == INVALID_SOCKET) return -1;
    accept_dispatch(lsock);
    return -1;
}
