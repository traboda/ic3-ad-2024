#include <dirent.h>
#include <errno.h>
#include <openssl/evp.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

/* ---------------------------------------- Auth ----------------------------*/

#define f1(x)                             \
  do {                                    \
    uint64_t h0 = x & 0xffffffff;         \
    uint64_t h1 = x & 0xffffffff00000000; \
    x = (h1 >> 32) + (h0 << 32);          \
  } while (0)

#define f2(x)               \
  do {                      \
    uint64_t h0 = x & 0xff; \
    x = x >> 8;             \
    x += h0 << 56;          \
  } while (0)

#define f3(x)                 \
  do {                        \
    uint64_t h0 = x & 0xffff; \
    x = x >> 16;              \
    x += h0 << 48;            \
  } while (0)

#define f4(x)                \
  do {                       \
    uint64_t n = x & 0xffff; \
    x = x ^ (n << 16);       \
    x = x ^ (n << 32);       \
    x = x ^ (n << 48);       \
  } while (0)

#define f5(x)              \
  do {                     \
    uint64_t n = x & 0xff; \
    x = x ^ (n << 8);      \
    x = x ^ (n << 16);     \
    x = x ^ (n << 24);     \
    x = x ^ (n << 32);     \
    x = x ^ (n << 40);     \
    x = x ^ (n << 48);     \
    x = x ^ (n << 56);     \
  } while (0)

#define f6(x)                                                                \
  do {                                                                       \
    uint64_t y = 0xff;                                                       \
    uint64_t n0 = x & y;                                                     \
    uint64_t n1 = x & (y << 8);                                              \
    uint64_t n2 = x & (y << 16);                                             \
    uint64_t n3 = x & (y << 24);                                             \
    uint64_t n4 = x & (y << 32);                                             \
    uint64_t n5 = x & (y << 40);                                             \
    uint64_t n6 = x & (y << 48);                                             \
    uint64_t n7 = x & (y << 56);                                             \
    x = n1 + (n5 << 8) + (n6 << 16) + (n3 << 24) + (n4 << 32) + (n0 << 40) + \
        (n2 << 48) + (n7 << 56);                                             \
  } while (0)

#define f7(x) (x = x ^ 0xdeadbeef)

#define f8(x)                             \
  do {                                    \
    uint64_t h0 = x & 0xffff;             \
    uint64_t h1 = x & 0xffff000000000000; \
    x = x ^ (h0 << 48);                   \
    x = x ^ (h1 >> 48);                   \
  } while (0)

__attribute__((always_inline)) uint64_t inline pad(uint64_t x) {
#ifdef FUNC1
  f1(x);
#endif
#ifdef FUNC2
  f2(x);
#endif
#ifdef FUNC3
  f3(x);
#endif
#ifdef FUNC4
  f4(x);
#endif
#ifdef FUNC5
  f5(x);
#endif
#ifdef FUNC6
  f6(x);
#endif
#ifdef FUNC7
  f7(x);
#endif
#ifdef FUNC8
  f8(x);
#endif
  return x;
}

#ifdef SHARED
uint64_t func1(uint64_t x) {
  f1(x);
  return x;
}

uint64_t func2(uint64_t x) {
  f2(x);
  return x;
}

uint64_t func3(uint64_t x) {
  f3(x);
  return x;
}

uint64_t func4(uint64_t x) {
  f4(x);
  return x;
}

uint64_t func5(uint64_t x) {
  f5(x);
  return x;
}

uint64_t func6(uint64_t x) {
  f6(x);
  return x;
}

uint64_t func7(uint64_t x) {
  f7(x);
  return x;
}

uint64_t func8(uint64_t x) {
  f8(x);
  return x;
}
#else

/* ---------------------------------------------------------------------- */

uint64_t auth(uint64_t x) {
  x = pad(x);
  x = pad(x);
  x = pad(x);
  x = pad(x);
  return x;
}

#define SHA256_DIGEST_LENGTH 32
#define TAG_LENGTH 10

#ifdef CANARY
#define CANARY_VAL CANARY
#else
#define CANARY_VAL 0xDEADBEEFDEADBEEF
#endif

#ifdef SIZE
#define BUF_SIZE SIZE
#else
#define BUF_SIZE 0x100
#endif

#define MAX_FRUIT_SIZE 0x500
#define RED "\x1B[31m%s\x1B[0m"
#define YELLOW "\x1B[33m%s\x1B[0m"
#define BLUE "\x1B[34m%s\x1B[0m"
#define GREEN "\x1B[32m%s\x1B[0m"

void pexit(char *arg) {
  fprintf(stderr, "%s: %s\n", arg, strerror(errno));
  exit(0);
}

void *Malloc(size_t size) {
  void *ptr = malloc(size);
  memset(ptr, 0, size);
  if (!ptr) {
    pexit("Malloc error");
  }
  return ptr;
}

FILE *Fopen(const char *filename, const char *mode) {
  FILE *fp;

  if ((fp = fopen(filename, mode)) == NULL) pexit("Fopen error");

  return fp;
}
void Fclose(FILE *fp) {
  if (fclose(fp) != 0) pexit("Fclose error");
}
size_t Fread(void *ptr, size_t size, size_t nmemb, FILE *stream) {
  size_t n;

  if (((n = fread(ptr, size, nmemb, stream)) < nmemb) && ferror(stream))
    pexit("Fread error");
  return n;
}

void Fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream) {
  if (fwrite(ptr, size, nmemb, stream) < nmemb) pexit("Fwrite error");
}

DIR *Opendir(void *ptr) {
  DIR *fp;
  if ((fp = opendir(ptr)) == NULL) pexit("Opendir error");
  return fp;
}

void getInp(char *buf, unsigned int size) {
  int n = read(0, buf, size);
  if (n <= 0) {
    perror("Read Error");
  }
  buf[n - 1] = '\0';
  return;
}

void Unlink(char *filename) {
  int n = unlink(filename);
  if (n < 0) {
    pexit("Unlink Error");
  }
  return;
}

unsigned int getInt() {
  char buf[32] = {0};
  getInp(buf, 31);
  return atoi(buf);
}

void verifySignature() {
  printf("Enter the number : ");
  long long int signarute = (long long int)auth(getInt());
  printf("%016llx\n", signarute);
  return;
}

void viewWarehouse() {
  struct dirent *de;
  DIR *dr = Opendir(".");
  printf("Available baskets: \n");
  while ((de = readdir(dr)) != NULL) {
    if (strcmp(de->d_name, ".") != 0 && strcmp(de->d_name, "..")) {
      printf("%s\n", de->d_name);
    }
  }
  closedir(dr);
  return;
}

void printBanana() {
  static const char string[] =
      "\n//\n"
      "V  \n"
      " \\  \\_\n"
      "  \\,'.`-.\n"
      "   |\\ `. `.\n"
      "   ( \\  `. `-.                        _,.-:\n"
      "    \\ \\   `.  `-._             __..--' ,-';/\n"
      "     \\ `.   `-.   `-..___..---'   _.--' ,'/\n"
      "      `. `.    `-._        __..--'    ,' /\n"
      "        `. `-_     ``--..''       _.-' ,'\n"
      "          `-_ `-.___        __,--'   ,'\n"
      "             `-.__  `----'''   __.-'\n"
      "                  `--..____..--'\n";
  printf("\x1B[33m%s\x1B[0m%s", string, "The name of Fruit is : ");
  return;
}

void printApple() {
  static const char string[] =
      "\n        __\n"
      "        \\/.--,\n"
      "        //_.'\n"
      "   .-''-/''-.\n"
      "  /       __ \\\n"
      " /        \\\\ \\\n"
      " |         || |\n"
      " \\            /\n"
      " \\  \\         /\n"
      "  \\  '-      /\n"
      "   '-.__.__.' \n";
  printf("\x1B[31m%s\x1B[0m%s", string, "The name of Fruit is : ");
  return;
}

void printCherry() {
  static const char string[] =
      "\n   __.--~~.,-.__\n"
      "   `~-._.-(`-.__`-.\n"
      "           \\    `~~`\n"
      "      .--./ \\\n"
      "     /#   \\  \\.--.\n"
      "     \\    /  /#   \\\n"
      "      '--'   \\    /\n"
      "              '--'\n";
  printf("\x1B[31m%s\x1B[0m%s", string, "The name of Fruit is : ");
  return;
}

void printWatermelon() {
  static const char string[] =
      "\n            ______\n"
      "        .-'' ____ ''-.\n"
      "       /.-=''    ''=-.\\\n"
      "       |-===wwwwww===-|\n"
      "       \'-=,,____,,=-'/\n"
      "        '-..______..-'\n";
  printf("\x1B[34m%s\x1B[0m%s", string, "The name of Fruit is : ");
  return;
}

void printGrape() {
  static const char string[] =
      "\n         __\n"
      "     __ {_/ \n"
      "     \\_}\\ _\n"
      "        _\(_)_\n"
      "       (_)_)(_)_\n"
      "      (_)(_)_)(_)\n"
      "       (_)(_))_)\n"
      "        (_(_(_)\n"
      "         (_)_)\n"
      "          (_)\n";
  printf("\x1B[34m%s\x1B[0m%s", string, "The name of Fruit is : ");
  return;
}

uint64_t canary = CANARY_VAL;

typedef struct {
  char *name;
  size_t name_size;
  size_t type;
  void (*ptr)();
} __attribute__((randomize_layout)) Fruit;

typedef struct {
  Fruit *fruits[10];
  size_t f_count;
  char tag[BUF_SIZE];
  uint64_t canary;
  void (*ptr)();
} __attribute__((no_randomize_layout)) Basket;

Basket basket;

void emptyBasket() {
  static const char string[] =
      "\n        ___...----------....___\n"
      "    .-''                       ''-.\n"
      "    |-._                      _.-'|\n"
      "    |   `''---...........---''`   |\n"
      "    |                             |\n"
      "    |                             |\n"
      "    |                             |\n"
      "    |                             |\n"
      "    |                             |\n"
      "    \\                             /\n"
      "     \\                           /\n"
      "      \\                         /\n"
      "       \\                       /\n"
      "        `-.__             __.-'\n"
      "             ''---...---''  \n";
  printf(GREEN, string);
}

void initBasket() {
  bzero(&basket.fruits, sizeof(basket.fruits));
  bzero(&basket.tag, BUF_SIZE);
  basket.f_count = 0;
  basket.canary = canary;
  basket.ptr = &emptyBasket;
}

bool isBasket() {
  if (!basket.ptr) {
    printf("No basket available!!");
    return false;
  }
  return true;
}

void initialize() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
}

unsigned int menu() {
  static const char string[] =
      "\n          Fruit Shop          \n"
      "+-----------------------------+\n"
      "| 1. Create Basket            |\n"
      "| 2. View Basket              |\n"
      "| 3. Add Fruit                |\n"
      "| 4. Remove Fruit             |\n"
      "| 5. Store Basket             |\n"
      "| 6. Restore Basket           |\n"
      "| 7. Remove Basket            |\n"
      "| 8. Leave Shop               |\n"
      "+-----------------------------+\n"
      "Your Choice >> ";
  printf(string);
  return getInt();
}

void createBasket() {
  initBasket();
  printf("Enter the name of basket : ");
  getInp(basket.tag, BUF_SIZE + 24);
  return;
}

void viewBasket() {
  if (!isBasket()) return;

  if (!basket.f_count) {
    if (basket.canary == canary) basket.ptr();
    return;
  }
  for (int i = 0; i < 10; i++) {
    Fruit *fruit = basket.fruits[i];
    if (fruit) {
      if (fruit->type > 0 && fruit->type < 6) {
        char *name = fruit->name;
        char buf[MAX_FRUIT_SIZE];
        fruit->ptr();
        memcpy(buf, fruit->name, fruit->name_size);
        printf(name);
      } else {
        printf("Overwrite detected\n");
        exit(0);
      }
    }
  }
  return;
}

void printFruits() {
  printf(
      "%s\n\x1B[33m%s\x1B[0m\x1B[31m%s\x1B[0m\x1B[31m%s\x1B[0m\x1B[32m%"
      "s\x1B[0m\x1B[34m%s\x1B[0m%s",
      "Which fruit to add", "1.Banana\n", "2.Apple\n", "3.Cherry\n",
      "4.Water Melon\n", "5.Grapes\n", ">> ");
  return;
}

void addPrintFunc(Fruit *fruit) {
  switch (fruit->type) {
    case 1:
      fruit->ptr = &printBanana;
      break;
    case 2:
      fruit->ptr = &printApple;
      break;
    case 3:
      fruit->ptr = &printCherry;
      break;
    case 4:
      fruit->ptr = &printWatermelon;
      break;
    case 5:
      fruit->ptr = &printGrape;
      break;
    default:
      printf("Invalid fruit type \n");
      exit(0);
  }
}

void addFruit() {
  if (!isBasket()) return;

  int idx;
  for (idx = 0; idx < 10; idx++) {
    if (!basket.fruits[idx]) break;
  }

  if (idx > 9) {
    printf("Not more than 10 fruits\n");
    return;
  }

  printFruits();

  unsigned int type = getInt();
  if (type > 5 || type <= 0) {
    printf("No such fruit\n");
    return;
  }

  printf("Enter size of tag : ");
  unsigned int size = getInt() + 1;
  if (size < MAX_FRUIT_SIZE) {
    char *ptr = (char *)Malloc(size);
    printf("Enter tag of Fruit : ");
    getInp(ptr, size);
    basket.fruits[idx] = (Fruit *)Malloc(sizeof(Fruit));
    Fruit *fruit = basket.fruits[idx];
    fruit->type = type;
    fruit->name = ptr;
    fruit->name_size = size;
    addPrintFunc(fruit);
    basket.f_count++;
    printf("Fruit added : %d\n", idx);
  }
}

void removeFruit() {
  if (!isBasket()) return;

  printf("Enter the fruit id : ");
  size_t idx = getInt();
  if (!basket.fruits[idx] || idx > 9) {
    printf("No such fruit\n");
    return;
  }
  if (basket.fruits[idx]->type == 0) {
    printf("Double free detected\n");
    exit(0);
  }
  free(basket.fruits[idx]->name);
  free(basket.fruits[idx]);
  basket.fruits[idx]->type = 0;
  basket.f_count--;
  for (size_t i = idx; i < basket.f_count; i++) {
    basket.fruits[i] = basket.fruits[i + 1];
  }

  printf("Success\n");
  return;
}

char *getBasketTag(char *buf, size_t size) {
  EVP_MD_CTX *mdctx;
  const EVP_MD *md;
  unsigned char hash[SHA256_DIGEST_LENGTH];
  unsigned int hash_len;

  mdctx = EVP_MD_CTX_new();
  md = EVP_sha256();

  EVP_DigestInit_ex(mdctx, md, NULL);
  EVP_DigestUpdate(mdctx, buf, size);
  EVP_DigestFinal_ex(mdctx, hash, &hash_len);

  EVP_MD_CTX_free(mdctx);

  // We know the hash length is always 32 for SHA256
  char *out = Malloc(SHA256_DIGEST_LENGTH * 2 + 1);
  for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
    snprintf(&out[i * 2], 3, "%02x", hash[i]);
  }
  out[SHA256_DIGEST_LENGTH * 2] = '\0';

  return out;
}

void saveBasket() {
  if (!isBasket()) return;

  FILE *fd;
  char *tag = getBasketTag(basket.tag, BUF_SIZE);

  // Use only the first 5 bytes of basket.tag for the filename
  size_t filename_size =
      strlen(tag) + TAG_LENGTH + 2;  // 1 for '-' and 1 for '\0'
  char *filename = Malloc(filename_size);
  snprintf(filename, filename_size, "%s-%.*s", tag, TAG_LENGTH, basket.tag);

  fd = Fopen(filename, "w+");
  Fwrite(&basket.f_count, sizeof(size_t), 1, fd);
  Fwrite(basket.tag, BUF_SIZE, 1, fd);

  for (size_t i = 0; i < basket.f_count; i++) {
    Fruit *fruit = basket.fruits[i];
    Fwrite(&fruit->name_size, sizeof(size_t), 1, fd);
    Fwrite(&fruit->type, sizeof(size_t), 1, fd);
    Fwrite(fruit->name, fruit->name_size, 1, fd);
  }

  Fclose(fd);
  printf("Basket tag : %s\n", filename);

  free(tag);
  free(filename);
  return;
}

void checkTag(char *tag) {
  unsigned int length = 0;
  for (size_t i = 0; i < strlen(tag); i++) {
    if ((tag[i] >= '0' && tag[i] <= '9') || (tag[i] >= 'a' && tag[i] <= 'z') ||
        tag[i] == '-') {
      length++;
    }
  }
  if (length != strlen(tag)) {
    printf("Invalid character detected in tag\n");
    exit(0);
  }
  return;
}

void restoreBasket() {
  char tag[SHA256_DIGEST_LENGTH * 2 + TAG_LENGTH + 2] = {0};
  printf("Basket tag : ");
  getInp(tag, sizeof(tag));

  checkTag(tag);

  FILE *fd = Fopen(tag, "r");
  if (basket.ptr) {
    for (size_t i = 0; i < basket.f_count; i++) {
      Fruit *fruit = basket.fruits[i];
      free(fruit->name);
      free(fruit);
      fruit = NULL;
    }
  }
  initBasket();

  Fread(&basket.f_count, sizeof(size_t), 1, fd);
  if (basket.f_count > 9) {
    printf("Too much fruits!!\n");
    basket.f_count = 0;
    return;
  }

  Fread(basket.tag, BUF_SIZE, 1, fd);

  for (size_t i = 0; i < basket.f_count; i++) {
    Fruit *fruit = Malloc(sizeof(Fruit));
    Fread(&fruit->name_size, sizeof(size_t), 1, fd);
    Fread(&fruit->type, sizeof(size_t), 1, fd);
    addPrintFunc(fruit);
    fruit->name = Malloc(fruit->name_size);
    Fread(fruit->name, fruit->name_size, 1, fd);
    basket.fruits[i] = fruit;
  }

  Fclose(fd);
  return;
}

void removeBasket() {
  initBasket();
  char tag[SHA256_DIGEST_LENGTH * 2 + TAG_LENGTH + 2] = {0};
  printf("Basket tag : ");
  getInp(tag, sizeof(tag));
  checkTag(tag);
  // Unlink(tag);
  return;
}

int main() {
  initialize();
  while (1) {
    unsigned int option = menu();
    if (option == 0x31337) {
      printf("You are not leet enough\n");
      exit(0);
    }
    switch (option) {
      case 1:
        createBasket();
        break;
      case 2:
        viewBasket();
        break;
      case 3:
        addFruit();
        break;
      case 4:
        removeFruit();
        break;
      case 5:
        saveBasket();
        break;
      case 6:
        restoreBasket();
        break;
      case 7:
        removeBasket();
        break;
      case 8:
        exit(0);
      case 0x1337:
        verifySignature();
        break;
      case 0x31337:
        viewWarehouse();
        break;
      default:
        exit(0);
    }
  }
}

#endif
