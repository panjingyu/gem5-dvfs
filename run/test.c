int main()
{
    // init variables
    int i, j;
    double x, y, z;
    #define MAX 10
    double a[MAX];

    int k = i / j;
    for (int iter = 0; iter < MAX; ++iter)
    {
        // main loop
        i += j;
        j -= i;
        x *= y;
        if (x)
        {
            y /= x * z;    
        }
        else
        {
            x = y + 0.002 * z;
        }
        aa:
        if (iter > 0)
        {
            a[iter] *= x + y;
        }
        else
        {
            a[iter] = x - y;
        }
    }
    
    return 0;
}