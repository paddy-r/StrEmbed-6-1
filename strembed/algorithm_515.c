/**
 * HR 11/02/21
 * Algorithm 515 (Buckles_77, DOI: https://doi.org/10.1145/355732.355739)
 * For indexing combinations -> lexicographic ordering for ranking/unranking
 *
 * via Stack Overflow user nlucaroni here:
 * https://stackoverflow.com/questions/561/how-to-use-combinations-of-sets-as-test-data#794
 *
 * [combination c n p x]
 * get the [x]th lexicographically ordered set of [p] elements in [n]
 * output is in [c], and should be sizeof(int)*[p] */
void combination(int* c,int n,int p, int x){
    int i,r,k = 0;
    for(i=0;i<p-1;i++){
        c[i] = (i != 0) ? c[i-1] : 0;
        do {
            c[i]++;
            r = choose(n-c[i],p-(i+1));
            k = k + r;
        } while(k < x);
        k = k - r;
    }
    c[p-1] = c[p-2] + x - k;
}