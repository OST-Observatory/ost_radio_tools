#include <stdio.h>
#include <stdlib.h>

#include <omp.h>
#include <math.h>
int main(int argc, char *argv[])
{ 
  FILE *f;
  float *temp;
  int samples = atoi(argv[2]);
  FILE *dump;
  float v0;
  float v1;
  temp = malloc(sizeof(float)*samples*2);
  f = fopen(argv[1], "rb");
  fseek(f, 0L, SEEK_END);
  long fsize = ftell(f);
  long size=fsize/sizeof(float)/samples/2;
  rewind(f);
  printf("File size: %d samples: %d\n",fsize,size);
  dump = fopen("data.asc", "w");
    
  for (int s=0;s<size;s++)
    {
    double total=0;
    fread(temp, sizeof(float)*samples*2, 1, f);
    for (int i=0;i<samples;i++)
        {
        v0=temp[i*2 +0];
        v1=temp[i*2 +1];
        total+=sqrt(v0*v0 + v1*v1);
        };
    fprintf(dump, "%d, %f\n", s,total/samples);
    if (s%20==0) 
        {
        printf("\r%.1f done.  ",(float)s/size*100.0);
        fflush(stdout);
        }
    };
  fclose(dump);
  fclose(f);
return 0;
}
