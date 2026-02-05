max=10000

# Compilacion de objetos
for (( i=0; i <= $max; ++i ))
do
    ollama pull llama3.1
    ollama pull deepseek-r1
done