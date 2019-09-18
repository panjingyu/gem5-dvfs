int main()
{
    // init variables
    int i, j;
    double x, y;

    for (int iter = 0; iter < 10; ++iter)
    {
        // main loop
        i += j;
        j -= i;
        x *= y;
        if (x)
        {
            y /= x;    
        }
        else
        {
            x = y + 0.001;
        }
    }
    
    return 0;
}