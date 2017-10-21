#include <stdio.h>

int main() {
  int t;
  scanf("%d", &t);

  while(t--) {
    int a,b,c;
    scanf("%d %d %d", &a, &b, &c);
    printf("%d\n", a+b+c);
  }

  return 0;
}
