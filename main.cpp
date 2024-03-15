#include <iostream>
#include <fstream>
#include "gml.h"

int main()
{
    // std::ifstream in("Abvt.gml");
    // std::cin.rdbuf(in.rdbuf());

    gml_context_t *ctx = gml_create((void *)"Abvt.gml");
    
    while (gml_parse(ctx, NULL)) {
        std::cout << "output: " << reinterpret_cast<char *>(ctx) << std::endl;
    }
    gml_destroy(ctx);
    return 0;
}