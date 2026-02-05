def fibonacci(n):
    if n <= 0:
        return "Incorrect Output"
    data = [0, 1]
    if n > 2:
        for i in range(2, n):
            data.append(data[i-1] + data[i-2])
    print(data)
    return data[n-1]

def main():
    print("Introduzca el número de rondas de fibonacci: ")
    n = input("> ")

    try:
        n = int(n)
        fibonacci(n)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()