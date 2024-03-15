all:
	gcc gml.c -O2 -Wall -Werror -c -o gml.o
	g++ main.cpp -O2 -Wall -Werror -c -o main.o
	g++ main.o gml.o -O2 -Wall -Werror -o main
	./main