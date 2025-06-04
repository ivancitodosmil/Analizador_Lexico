import csv  # Importamos la librería csv para guardar resultados en archivo CSV

# Definimos las palabras reservadas del lenguaje que nuestro analizador reconocerá
palabras_reservadas = {
    "if", "else", "function", "return", "class",
    "for", "while", "true", "false"
}

# Operadores válidos que se aceptan
operadores = {
    "==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "=", "+", "-", "*", "/", "%", "^", "<", ">"
}

# Conjunto de delimitadores válidos (símbolos de puntuación del lenguaje)
delimitadores = {"{", "}", "(", ")", ";", ","}

# Función para saber si un carácter es letra o guion bajo (válido para identificadores)
def es_letra(c):
    return c.isalpha() or c == "_"

# Función para saber si un carácter es un número
def es_digito(c):
    return c.isdigit()

# Función auxiliar para validar si un token es un número decimal bien formado
def es_decimal_valido(token):
    if token.count('.') != 1:
        return False
    parte_entera, parte_decimal = token.split('.')
    return parte_entera.isdigit() and parte_decimal.isdigit() and parte_decimal != ""

#--------------------------------------------------------------------------------------------
# Determina el estado del autómata para un token determinado
def obtener_estado(token):
    if token in palabras_reservadas:
        return "q0"

    if token in operadores:
        if token == "&&":
            return "q11"
        elif token == "||":
            return "q14"
        elif token in {"<", ">", "="}:
            return "q6"
        elif token in {"==", "!=", "<=", ">="}:
            return "q7"
        elif token in {"+", "-", "*", "/", "^", "%"}:
            return "q1"
        elif token in {"+=", "-="}:
            return "q10"
        else:
            return "q0"

    if token in delimitadores:
        if token in {"(", ")", "{", "}"}:
            return "q13"
        elif token == ",":
            return "q16"
        elif token == ";":
            return "q18"
        else:
            return "q0"

    if es_decimal_valido(token):
        return "q3"  
    elif token.isdigit():
        return "q2"  

    if token.startswith('"') and token.endswith('"'):
        return "q0"

    if es_letra(token[0]):
        if any(c.isdigit() for c in token):
            return "q15"
        else:
            return "q9"

    if token == "$":
        return "q17"

    return "ERROR"

# Clasifica el tipo de token
def analizar_token(token):
    if token in palabras_reservadas:
        return "PALABRA_RESERVADA"
    elif token in operadores:
        return "OPERADOR"
    elif token in delimitadores:
        return "DELIMITADOR"
    elif es_decimal_valido(token) or token.isdigit():
        return "NUMERO"
    elif token.startswith('"') and token.endswith('"'):
        return "CADENA"
    elif es_letra(token[0]):
        return "IDENTIFICADOR"
    else:
        return "ERROR"

# Lista donde guardaremos los resultados para el archivo CSV
resultado_csv = []

# Función principal que analiza una línea de código
def automata_analizador(linea, numero_linea):
    i = 0
    longitud = len(linea)

    while i < longitud:
        # 1. Detectar COMENTARIOS (empezando con $)
        if linea[i] == "$":
            print(f"{numero_linea:<7} {'$':<20} {'COMENTARIO':<20} {'q17'}")
            resultado_csv.append([numero_linea, "$", "COMENTARIO", "q17"])
            break  # ignoramos el resto de la línea si hay un comentario

        # 2. Ignorar ESPACIOS en blanco
        elif linea[i].isspace():
            i += 1
            continue  # pasa al siguiente carácter

        # 3. Detectar CADENAS entre comillas
        elif linea[i] == '"':
            inicio = i
            i += 1
            while i < longitud and linea[i] != '"':
                i += 1
            if i < longitud:
                i += 1  # cerrar cadena correctamente
                token = linea[inicio:i]
                estado = obtener_estado(token)
                print(f"{numero_linea:<7} {token:<20} {'CADENA':<20} {estado}")
                resultado_csv.append([numero_linea, token, "CADENA", estado])
            else:
                print(f"{numero_linea:<7} {'<cadena no cerrada>':<20} {'ERROR':<20} {'---'}")
                resultado_csv.append([numero_linea, "<cadena no cerrada>", "ERROR", "---"])

        # 4. Detectar PALABRAS RESERVADAS o IDENTIFICADORES
        elif es_letra(linea[i]):
            inicio = i
            while i < longitud and (es_letra(linea[i]) or es_digito(linea[i])):
                i += 1
            token = linea[inicio:i]
            tipo = analizar_token(token)
            estado = obtener_estado(token)
            print(f"{numero_linea:<7} {token:<20} {tipo:<20} {estado}")
            resultado_csv.append([numero_linea, token, tipo, estado])

        # 5. Detectar NÚMEROS (enteros o decimales)
        elif es_digito(linea[i]):
            inicio = i
            tiene_punto = False
            while i < longitud and (es_digito(linea[i]) or (linea[i] == "." and not tiene_punto)):
                if linea[i] == ".":
                    tiene_punto = True
                i += 1
            token = linea[inicio:i]
            estado = obtener_estado(token)
            tipo = analizar_token(token)
            print(f"{numero_linea:<7} {token:<20} {tipo:<20} {estado}")
            resultado_csv.append([numero_linea, token, tipo, estado])

        # 6. Detectar DELIMITADORES como ; , ( ) {}
        elif linea[i] in delimitadores:
            estado = obtener_estado(linea[i])
            print(f"{numero_linea:<7} {linea[i]:<20} {'DELIMITADOR':<20} {estado}")
            resultado_csv.append([numero_linea, linea[i], "DELIMITADOR", estado])
            i += 1

        # 7. Detectar OPERADORES o ERRORES
        else:
            token = linea[i:i+2]  # intentamos capturar operadores dobles
            if token in operadores:
                estado = obtener_estado(token)
                print(f"{numero_linea:<7} {token:<20} {'OPERADOR':<20} {estado}")
                resultado_csv.append([numero_linea, token, "OPERADOR", estado])
                i += 2
            else:
                token = linea[i]  # intentamos capturar operadores simples
                if token in operadores:
                    estado = obtener_estado(token)
                    print(f"{numero_linea:<7} {token:<20} {'OPERADOR':<20} {estado}")
                    resultado_csv.append([numero_linea, token, "OPERADOR", estado])
                else:
                    print(f"{numero_linea:<7} {token:<20} {'ERROR':<20} {'---'}")
                    resultado_csv.append([numero_linea, token, "ERROR", "---"])
                i += 1

# Guarda los resultados en archivo CSV usando punto y coma como separador
def guardar_en_csv(nombre_archivo):
    with open(nombre_archivo, mode='w', encoding='utf-8', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv, delimiter=';')
        writer.writerow(["Linea", "Token", "Tipo", "Estado"])
        writer.writerows(resultado_csv)
    print(f"\n✅ Resultado guardado en: {nombre_archivo}")

# Lee un archivo de texto, analiza línea por línea, y guarda el resultado
def analizar_archivo(nombre_archivo):
    try:
        print(f"{'Línea':<7} {'Token':<20} {'Tipo':<20} {'Estado'}")
        print("-" * 60)

        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                automata_analizador(linea.strip(), numero_linea)

        guardar_en_csv("resultado_lexico.csv")

    except FileNotFoundError:
        print("❌ Archivo no encontrado:", nombre_archivo)

# Llamamos a la función principal con un archivo de prueba
analizar_archivo("prueba.txt")
