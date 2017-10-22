#include <stdio.h>

int main() {
  int t;
  scanf("%d", &t);
  while(t--) {
    int n;
    scanf("%d", &n);
    int a[n];
    for(int i=0; i<n; ++i)
        scanf("%d", a+i);
    int x;
    scanf("%d", &x);
    int p = -1;
    for(int i=0; i<n; ++i)
      if(a[i] == x) {
         p = i;
         break;
      }

    printf("%d\n", p);
  }

  return 0;
}
