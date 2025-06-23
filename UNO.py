import random
from datetime import datetime
import os
import time
import copy
import pandas as pd
from colorama import Fore, Style, init
init(autoreset=True)

# Auxiliares -------------------------------------------------------------------

def encabezados():
    colores = ["NE", "AZ", "VE", "RO", "AM"]
    tipos_nombres = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'S', 'R', '+2', 'C']

    return colores, tipos_nombres

# ------------------------------------------------------------------------------

def Crear_Mazo():
    colores, tipos = encabezados()
    tipos.remove('C')
    mazo = []
    for color in colores:
        x = []
        if color == 'NE':
            for i in range(12):
                x.append(color + '#' + 'C')

        else:
            for tipo in tipos:
                for i in range(1 if tipo == "0" else 2):
                    x.append(color + '#' + tipo)
            
        
        mazo.append(x)
        
    return mazo

# ------------------------------------------------------------------------------

def Crear_jugadores(Num_jugadores):
    jugadores = [{'nombre':'CPU', 'mano':[], 'estadisticas':[]}]
    for i in range(1, Num_jugadores+1):
        while True:
            nombre = str(input(f"Ingresa el nombre del jugador {i}: "))
            if len(nombre) != 0:
                break
            else:
              print(f"Debes de ingresar un nombre para jugador {i}")
        jugadores.append({'nombre': nombre, 'mano':[], 'estadisticas':[]})

    return jugadores

# ------------------------------------------------------------------------------

def Repartir_cartas(jugadores, mazo):
    for jugador in jugadores:
        mano = []
        for i in range(7):
            sector = random.choice(mazo)
            carta = random.choice(sector)
            mano.append(carta)
            index = mazo.index(sector)
            mazo[index].remove(carta)

        jugador['mano'] = mano

    return mazo

# ------------------------------------------------------------------------------

def revolver_mazo(mazo):
    baraja = []
    for sector in mazo:
        baraja.extend(sector)
    random.shuffle(baraja)
    print("El mazo ha sido revuelto")
    print(baraja)
    return baraja

# ------------------------------------------------------------------------------

def separar_carta(carta):
    carta_separada = carta.split("#")
    color = carta_separada[0]
    tipo = carta_separada[1]    
    return color, tipo

def diccionario_carta(carta):
    carta_separada = carta.split("#")
    carta_diccionario = {
        'carta': carta,
        'color': carta_separada[0],
        'valor': carta_separada[1]
    }   
    return carta_diccionario

# ------------------------------------------------------------------------------

def mostrarCarta(carta):
    carta = diccionario_carta(carta)
    
    color = carta['color']
    valor = str(carta['valor'])
    if color == "RO":
        return Fore.RED + color + " " + valor 
    elif color == "AZ":
        return Fore.BLUE + color + " " + valor 
    elif color == "VE":
        return Fore.GREEN + color + " " + valor 
    elif color == "AM":
        return Fore.YELLOW + color + " " + valor 
    else:
        return color + " " + valor

# ------------------------------------------------------------------------------

def mostrarMano(jugador, numeradas=False):
    i=1
    for carta in jugador['mano']:
        print((str(i)+' ' if numeradas else '') + mostrarCarta(carta))
        i+=1

#------------------------------------------------------------------------------

def cumple_reglas(cartaEscogida, cartaEnJuego):
    if not isinstance(cartaEscogida, dict):
        cartaEscogida = diccionario_carta(cartaEscogida)
    if not isinstance(cartaEnJuego, dict):
        cartaEnJuego = diccionario_carta(cartaEnJuego)
    if cartaEscogida['color'] == 'NE':
        return True
    else:
        return (cartaEnJuego['color'] == cartaEscogida['color'] or
                cartaEnJuego['valor'] == cartaEscogida['valor'])
# ------------------------------------------------------------------------------

def escoger_color_comodin():
    colores, tipos = encabezados()
    colorEscogido = ""
    repetir = True
    while repetir:
        i = 1
        for color in colores[1:]:
            if color == "RO":
                print(Fore.RED + str(i) + " " + color)
            elif color == "AZ":
                print(Fore.BLUE + str(i) + " " + color)
            elif color == "VE":
                print(Fore.GREEN + str(i) + " " + color)
            elif color == "AM":
                print(Fore.YELLOW + str(i) + " " + color)
            else:
                print(str(i) + " " + color)
            i += 1
        colorEscogido = input('Escoge un color: ')
        if colorEscogido.isnumeric() and int(colorEscogido) > 0 and int(colorEscogido) <= len(colores) - 1:
            repetir = False
    return colores[int(colorEscogido)]

# ------------------------------------------------------------------------------

def robar(jugador, cantidad, mazo):
    for _ in range(cantidad):
        if len(mazo) > 0:
            jugador['mano'].append(mazo[0])
            mazo = mazo[1:]
        else:
            print("No hay más cartas para robar.")
            break
    return mazo

# ------------------------------------------------------------------------------

def escoger_carta(jugador, cartaEnJuego, mazo, monton):
    repetir = True
    carta_jugada = None
    ya_robaste = False
    while repetir:
        mostrarMano(jugador, True)
        print('\r\n\rCarta en la mesa: ', mostrarCarta(monton[-1]))
        if not ya_robaste:
            IdcartaEscogida = input('Selecciona una carta (R para robar): ').capitalize()
        else:
            IdcartaEscogida = input('Selecciona una carta o P para pasar: ').capitalize()
        if IdcartaEscogida == 'R' and not ya_robaste:
            if len(mazo) > 0:
                mazo = robar(jugador, 1, mazo)
                ya_robaste = True
            else:
                print('No hay cartas para robar. Puedes pasar el turno (P).')
                ya_robaste = True
        elif IdcartaEscogida == 'P' and ya_robaste:
            repetir = False
            carta_jugada = None
        elif IdcartaEscogida.isnumeric() and int(IdcartaEscogida) > 0 and int(IdcartaEscogida) <= len(jugador['mano']):
            cartaEscogida = jugador['mano'][int(IdcartaEscogida) - 1]
            cartaEscogida_dict = diccionario_carta(cartaEscogida)
            if cumple_reglas(cartaEscogida_dict, cartaEnJuego):
                jugador['mano'].remove(cartaEscogida)
                if cartaEscogida_dict['color'] == 'NE':
                    # Elegir color para el comodín
                    color_escogido = escoger_color_comodin()
                    carta_jugada = cartaEscogida_dict.copy()
                    carta_jugada['color'] = color_escogido
                    carta_jugada['carta'] = color_escogido + "#C"
                else:
                    carta_jugada = cartaEscogida_dict
                repetir = False
                if len(jugador['mano']) == 1:
                    print(f"{jugador['nombre']} dice: ¡UNO!")
            else:
                print('No se puede jugar esa carta')
        else:
            print('Opción inválida')
    return carta_jugada, mazo
# ------------------------------------------------------------------------------

def jugarCarta(jugador, cartaEnJuego, baraja, monton, jugadores, jugador_actual, sentido):
    mano = [diccionario_carta(c) for c in jugador['mano']]
    siguiente_idx = (jugador_actual + sentido) % len(jugadores)
    siguiente_jugador = jugadores[siguiente_idx]
    cartas_siguiente = len(siguiente_jugador['mano'])
    color_mesa = diccionario_carta(cartaEnJuego)['color']
    valor_mesa = diccionario_carta(cartaEnJuego)['valor']

    print(f"Cartas del siguiente jugador ({siguiente_jugador['nombre']}): {cartas_siguiente}")
    print(f"Mano del CPU: {jugador['mano']} cartas")
    

    # 1. Si el siguiente jugador tiene menos de 4 cartas, juega cualquier carta válida (+2, salto, reversa, comodín, color/tipo)
    if cartas_siguiente < 4:
        for tipo in ['+2', 'S', 'R']:
            for i, carta in enumerate(mano):
                if carta['valor'] == tipo and cumple_reglas(carta['carta'], cartaEnJuego):
                    jugador['mano'].pop(i)
                    return carta, baraja

    # 2. ¿Tengo comodín? (prioridad antes de buscar otras jugadas)
    for i, carta in enumerate(mano):
        if carta['color'] == 'NE':
            # Elegir color más frecuente
            colores = {}
            for c in mano:
                if c['color'] != 'NE':
                    colores[c['color']] = colores.get(c['color'], 0) + 1
            color = max(colores, key=colores.get) if colores else 'AZ'
            carta_jugada = carta.copy()
            carta_jugada['color'] = color
            carta_jugada['carta'] = color + "#C"
            # Elimina el comodín original de la mano
            jugador['mano'].remove(carta['carta'])
            print(f"CPU escoge el color {color} para el comodín.")
            return carta_jugada, baraja

    # 3. ¿Tengo carta válida cualquiera?
    for i, carta in enumerate(mano):
        if cumple_reglas(carta['carta'], cartaEnJuego):
            jugador['mano'].pop(i)
            return carta, baraja

    # 4. ¿Tengo carta +2, salto o reversa del mismo color?
    for tipo in ['+2', 'S', 'R']:
        for i, carta in enumerate(mano):
            if carta['valor'] == tipo and carta['color'] == color_mesa:
                jugador['mano'].pop(i)
                return carta, baraja

    # 5. ¿Tengo carta del mismo color?
    cartas_color = [c for c in mano if c['color'] == color_mesa and cumple_reglas(c['carta'], cartaEnJuego)]
    if cartas_color:
        estadisticas = jugador.get('estadisticas', None)
        if estadisticas and len(estadisticas) > 3:
            conteo_tipo = estadisticas[3]
            carta_elegida = min(cartas_color, key=lambda c: conteo_tipo[int(c['valor'])] if c['valor'].isdigit() else 99)
        else:
            carta_elegida = cartas_color[0]
        jugador['mano'].remove(carta_elegida['carta'])
        return carta_elegida, baraja

    # 6. ¿Tengo carta del mismo número/tipo?
    cartas_tipo = [c for c in mano if c['valor'] == valor_mesa and cumple_reglas(c['carta'], cartaEnJuego)]
    if cartas_tipo:
        jugador['mano'].remove(cartas_tipo[0]['carta'])
        return cartas_tipo[0], baraja

    # 7. ¿Tengo comodín? (por si no se jugó antes)
    comodines = [c for c in jugador['mano'] if c.endswith('#C')]
    if comodines:
        carta_jugada = diccionario_carta(comodines[0])
        colores = {}
        for c in jugador['mano']:
            color_carta, tipo_carta = separar_carta(c)
            if color_carta != 'NE':
                colores[color_carta] = colores.get(color_carta, 0) + 1
        color = max(colores, key=colores.get) if colores else 'AZ'
        carta_jugada['color'] = color
        carta_jugada['carta'] = color + "#C"
        jugador['mano'].remove(comodines[0])
        print(f"CPU escoge el color {color} para el comodín.")
        return carta_jugada, baraja

    # 8. Robo carta
    if len(baraja) > 0:
        nueva_carta = baraja[0]
        baraja = baraja[1:]
        jugador['mano'].append(nueva_carta)
        if cumple_reglas(nueva_carta, cartaEnJuego):
            jugador['mano'].remove(nueva_carta)
            return diccionario_carta(nueva_carta), baraja
        return None, baraja
    else:
        print('No hay cartas para robar')
        return None, baraja

# ------------------------------------------------------------------------------

def ajustar_mazo_CPU(jugadores):
    colores, tipos_nombres = encabezados()

    Conteo_Color_Cartas = [12, 25, 25, 25, 25]
    Conteo_Tipo_Cartas = [4, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 12]
    Total_cartas = 112

    cpu = jugadores[0]
    Mano_CPU = cpu['mano']

    for carta in Mano_CPU:
        color, tipo = separar_carta(carta)
        Total_cartas -= 1

        if color in colores:
            index_color = colores.index(color)
            Conteo_Color_Cartas[index_color] -= 1

        if tipo in tipos_nombres:
            index_tipo = tipos_nombres.index(tipo)
            Conteo_Tipo_Cartas[index_tipo] -= 1
        else:
            try:
                index_tipo = int(tipo)
                Conteo_Tipo_Cartas[index_tipo] -= 1
            except ValueError:
                pass

    return Conteo_Color_Cartas, Conteo_Tipo_Cartas, Total_cartas

# ------------------------------------------------------------------------------

def conteo_inicial(jugadores):
    Conteo_color, Conteo_tipo, Cartas_totales = ajustar_mazo_CPU(jugadores)

    for jugador in jugadores:
        if jugador['nombre'] == 'CPU':
            jugador['estadisticas'] = [Conteo_color, Conteo_tipo, Cartas_totales]
        else:
            jugador['estadisticas'] = [Conteo_color, Cartas_totales, [], 
                                           Conteo_tipo, Cartas_totales, []]
    return jugadores

# ------------------------------------------------------------------------------

def estadisticas_completas(jugadores):
    for jugador in jugadores[1:]:
        player = jugador['estadisticas']
        conteos_color = player[0]
        totales_color = player[1]
        estadisticas_color = player[2]
        conteos_tipo = player[3]
        totales_tipo = player[4]
        estadisticas_tipo = player[5]

        for i in conteos_color:
            estadistica = round((i / totales_color * 100), 2)
            estadisticas_color.append(estadistica)
        for i in conteos_tipo:
            estadistica = round((i / totales_tipo * 100), 2)
            estadisticas_tipo.append(estadistica)

    return jugadores


# ------------------------------------------------------------------------------

def definir_orden_dejuego(jugadores):
    print("Tiraremos un dado para definir el orden. El más alto empieza.\n")

    tiros = []
    cpu_tiro = random.randint(1, 6)
    tiros.append((jugadores[0]['nombre'], cpu_tiro))
    print(f"Tiro del CPU: {cpu_tiro}\n")

    for jugador in jugadores[1:]:
        input(f"{jugador['nombre']}, presiona [ENTER] para tirar tu dado.")
        tiro = random.randint(1, 6)
        tiros.append((jugador['nombre'], tiro))
        print(f"Tiro de {jugador['nombre']}: {tiro}\n")

    tiros.sort(key=lambda x: x[1], reverse=True)

    print("Orden de juego:")
    for i, (nombre, tiro) in enumerate(tiros, 1):
        print(f"{i}. {nombre} (Tiro: {tiro})")

    jugadores_ordenados = []
    for nombre, _ in tiros:
        for jugador in jugadores:
            if jugador['nombre'] == nombre:
                jugadores_ordenados.append(jugador)
                break

    return jugadores_ordenados




# Funcion Carta REVERSA --------------------------------------------------------

def efecto_reversa(sentido, jugadores):
    sentido *= -1
    print("¡Sentido de juego invertido!")
    return sentido

# Funcion Carta BLOQUEO
def efecto_bloqueo(jugador_actual, sentido, jugadores):
    print("¡El siguiente jugador pierde su turno!")
    return (jugador_actual + sentido) % len(jugadores)

# ------------------------------------------------------------------------------

def mostrar_estadistica(jugador, df_historial=None, turno=1, carta_jugada=None):
    columnas_color, columnas_tipo = encabezados()
    stats = jugador['estadisticas']
    nombre = jugador['nombre']

    fila = {
        'Juego': 11,
        'Turno': turno,
        'Jugador': nombre,
        'Carta jugada': carta_jugada if carta_jugada is not None else ''
    }

    if nombre == 'CPU':
        conteo_color = stats[0]
        conteo_tipo = stats[1]
        total = stats[2]

        fila['Total Color'] = total
        for i, color in enumerate(columnas_color):
            fila[color] = conteo_color[i]

        fila['Total Tipo'] = total
        for i, tipo in enumerate(columnas_tipo):
            fila[tipo] = conteo_tipo[i]

    else:
        conteo_color = stats[0]
        total_color = stats[1]
        porcentaje_color = stats[2]
        conteo_tipo = stats[3]
        total_tipo = stats[4]
        porcentaje_tipo = stats[5]

        fila['Total Color'] = total_color
        for i, color in enumerate(columnas_color):
            fila[color] = conteo_color[i]

        fila['Total Tipo'] = total_tipo
        for i, tipo in enumerate(columnas_tipo):
            fila[tipo] = conteo_tipo[i]

    # Agregar la fila al historial
    df_historial = pd.concat([df_historial, pd.DataFrame([fila])], ignore_index=True) if df_historial is not None else pd.DataFrame([fila])

    return df_historial



# ------------------------------------------------------------------------------

def actualizar_estadisticas_CPU_tras_jugada(carta_jugada, jugador):
    colores, tipos_nombres = encabezados()
    
    if isinstance(carta_jugada, dict):
        color = carta_jugada['color']
        tipo = carta_jugada['valor']
    else:
        color, tipo = separar_carta(carta_jugada)

    conteo_color = jugador['estadisticas'][0]
    conteo_tipo = jugador['estadisticas'][1]
    total = jugador['estadisticas'][2]

    # Actualizar conteo por color
    if color in colores:
        idx_color = colores.index(color)
        conteo_color[idx_color] = max(0, conteo_color[idx_color] - 1)

    # Actualizar conteo por tipo
    if tipo in tipos_nombres:
        idx_tipo = tipos_nombres.index(tipo)
        conteo_tipo[idx_tipo] = max(0, conteo_tipo[idx_tipo] - 1)

    # Actualizar total
    jugador['estadisticas'][2] = max(0, total - 1)

    return jugador

# ------------------------------------------------------------------------------
def actualizar_estadisticas_jugador(jugador, carta_jugada, carta_en_mesa, robo=False):
    colores, tipos_nombres = encabezados()
    stats = jugador['estadisticas']

    conteo_color = stats[0]
    total_color = stats[1]
    conteo_tipo = stats[3]
    total_tipo = stats[4]

    color_mesa, tipo_mesa = separar_carta(carta_en_mesa if isinstance(carta_en_mesa, str) else carta_en_mesa['carta'])

    if robo:
        for color in ["NE", color_mesa]:
            if color in colores:
                idx = colores.index(color)
                total_color -= conteo_color[idx]
                total_color = max(total_color, 0)
                conteo_color[idx] = 0

        for tipo in ["C", tipo_mesa]:
            if tipo in tipos_nombres:
                idx = tipos_nombres.index(tipo)
                total_tipo -= conteo_tipo[idx]
                total_tipo = max(total_tipo, 0)
                conteo_tipo[idx] = 0

    else:
        if isinstance(carta_jugada, str):
            color_jugada, tipo_jugada = separar_carta(carta_jugada)
        else:
            color_jugada = carta_jugada['color']
            tipo_jugada = carta_jugada['valor']

        idx_color_jugada = colores.index(color_jugada) if color_jugada in colores else None
        idx_tipo_jugada = tipos_nombres.index(tipo_jugada) if tipo_jugada in tipos_nombres else None
        idx_color_mesa = colores.index(color_mesa) if color_mesa in colores else None
        idx_tipo_mesa = tipos_nombres.index(tipo_mesa) if tipo_mesa in tipos_nombres else None

        if color_jugada == 'NE':
            if idx_color_mesa is not None:
                total_color -= conteo_color[idx_color_mesa]
                total_color = max(total_color, 0)
                conteo_color[idx_color_mesa] = 0
            if idx_tipo_mesa is not None:
                total_tipo -= conteo_tipo[idx_tipo_mesa]
                total_tipo = max(total_tipo, 0)
                conteo_tipo[idx_tipo_mesa] = 0

        elif color_jugada == color_mesa and tipo_jugada == tipo_mesa:
            if idx_color_jugada is not None and conteo_color[idx_color_jugada] > 0:
                conteo_color[idx_color_jugada] -= 1
                total_color -= 1
                total_color = max(total_color, 0)
            if idx_tipo_jugada is not None and conteo_tipo[idx_tipo_jugada] > 0:
                conteo_tipo[idx_tipo_jugada] -= 1
                total_tipo -= 1
                total_tipo = max(total_tipo, 0)

        elif color_jugada == color_mesa:
            if idx_color_jugada is not None and conteo_color[idx_color_jugada] > 0:
                conteo_color[idx_color_jugada] -= 1
                total_color -= 1
                total_color = max(total_color, 0)
            if idx_tipo_jugada is not None and conteo_tipo[idx_tipo_jugada] > 0:
                conteo_tipo[idx_tipo_jugada] -= 1
                total_tipo -= 1
                total_tipo = max(total_tipo, 0)

        elif tipo_jugada == tipo_mesa:
            if idx_color_mesa is not None:
                total_color -= conteo_color[idx_color_mesa]
                total_color = max(total_color, 0)
                conteo_color[idx_color_mesa] = 0
            if idx_tipo_jugada is not None and conteo_tipo[idx_tipo_jugada] > 0:
                conteo_tipo[idx_tipo_jugada] -= 1
                total_tipo -= 1
                total_tipo = max(total_tipo, 0)

    jugador['estadisticas'][0] = conteo_color
    jugador['estadisticas'][1] = total_color
    jugador['estadisticas'][3] = conteo_tipo
    jugador['estadisticas'][4] = total_tipo
    jugador['estadisticas'][2] = []
    jugador['estadisticas'][5] = []

    for i in conteo_color:
        jugador['estadisticas'][2].append(round((i / total_color * 100), 2) if total_color > 0 else 0.0)
    for i in conteo_tipo:
        jugador['estadisticas'][5].append(round((i / total_tipo * 100), 2) if total_tipo > 0 else 0.0)

    return jugador

def afectar_estadisticas_otros_jugadores_por_CPU(jugadores, carta_cpu):
    colores, tipos = encabezados()
    color, tipo = separar_carta(carta_cpu if isinstance(carta_cpu, str) else carta_cpu['carta'])

    for jugador in jugadores:
        if jugador['nombre'] == 'CPU':
            continue  # Saltar al CPU
        conteo_color = jugador['estadisticas'][0]
        total_color = jugador['estadisticas'][1]
        conteo_tipo = jugador['estadisticas'][3]
        total_tipo = jugador['estadisticas'][4]

        if color in colores:
            idx = colores.index(color)
            if conteo_color[idx] > 0:
                conteo_color[idx] -= 1
                total_color = max(total_color - 1, 0)

        if tipo in tipos:
            idx = tipos.index(tipo)
            if conteo_tipo[idx] > 0:
                conteo_tipo[idx] -= 1
                total_tipo = max(total_tipo - 1, 0)

        jugador['estadisticas'][0] = conteo_color
        jugador['estadisticas'][1] = total_color
        jugador['estadisticas'][3] = conteo_tipo
        jugador['estadisticas'][4] = total_tipo

        jugador['estadisticas'][2] = [round((i / total_color * 100), 2) if total_color > 0 else 0.0 for i in conteo_color]
        jugador['estadisticas'][5] = [round((i / total_tipo * 100), 2) if total_tipo > 0 else 0.0 for i in conteo_tipo]

def afectar_estadisticas_otros_jugadores_por_jugador(jugadores, jugador_que_jugo, carta_jugada):
    colores, tipos = encabezados()
    color, tipo = separar_carta(carta_jugada if isinstance(carta_jugada, str) else carta_jugada['carta'])

    for jugador in jugadores:
        if jugador == jugador_que_jugo or jugador['nombre'] == 'CPU':
            continue

        conteo_color = jugador['estadisticas'][0]
        total_color = jugador['estadisticas'][1]
        conteo_tipo = jugador['estadisticas'][3]
        total_tipo = jugador['estadisticas'][4]

        if color in colores:
            idx = colores.index(color)
            if conteo_color[idx] > 0:
                conteo_color[idx] -= 1
                total_color = max(total_color - 1, 0)

        if tipo in tipos:
            idx = tipos.index(tipo)
            if conteo_tipo[idx] > 0:
                conteo_tipo[idx] -= 1
                total_tipo = max(total_tipo - 1, 0)

        jugador['estadisticas'][0] = conteo_color
        jugador['estadisticas'][1] = total_color
        jugador['estadisticas'][3] = conteo_tipo
        jugador['estadisticas'][4] = total_tipo

        jugador['estadisticas'][2] = [round((i / total_color * 100), 2) if total_color > 0 else 0.0 for i in conteo_color]
        jugador['estadisticas'][5] = [round((i / total_tipo * 100), 2) if total_tipo > 0 else 0.0 for i in conteo_tipo]

def afectar_estadisticas_CPU_por_jugada(jugadores, carta_jugada):
    colores, tipos = encabezados()
    color, tipo = separar_carta(carta_jugada if isinstance(carta_jugada, str) else carta_jugada['carta'])

    cpu = jugadores[0]
    conteo_color = cpu['estadisticas'][0]   # lista de conteos por color
    conteo_tipo = cpu['estadisticas'][1]   # lista de conteos por tipo
    total_cartas = cpu['estadisticas'][2]  # total de cartas

    if not isinstance(total_cartas, int):
        print("Error: total_cartas no es un entero. Verifica la estructura de estadísticas del CPU.")
        return

    if color in colores:
        idx = colores.index(color)
        if conteo_color[idx] > 0:
            conteo_color[idx] -= 1
            total_cartas = max(total_cartas - 1, 0)

    if tipo in tipos:
        idx = tipos.index(tipo)
        if conteo_tipo[idx] > 0:
            conteo_tipo[idx] -= 1
            total_cartas = max(total_cartas - 1, 0)

    cpu['estadisticas'][0] = conteo_color
    cpu['estadisticas'][1] = conteo_tipo
    cpu['estadisticas'][2] = total_cartas



# Iniciar el juego ------------------------------------------------------------

def Iniciar_juego():
    monton = []
    baraja = Crear_Mazo()
    colores, tipos_nombres = encabezados()
    jugadores = Crear_jugadores(2)
    Repartir_cartas(jugadores, baraja)
    baraja = revolver_mazo(baraja)
    jugadores = definir_orden_dejuego(estadisticas_completas(conteo_inicial(jugadores)))
    
    df_historial = pd.DataFrame()
    turno = 1

    
    monton.append(baraja[0])
    baraja.remove(monton[0])

    primer_carta = diccionario_carta(monton[0])
    if primer_carta['valor'] in ['+2', 'R', 'S']:
        print(f"La primera carta es especial ({primer_carta['valor']}). No surte efecto, solo cuenta el color.")
    if primer_carta['valor'] == 'C':
        color_aleatorio = random.choice(colores[1:])
        print(f"La primera carta es un COMODIN. Se asigna el color {color_aleatorio}.")
        monton[0] = color_aleatorio + "#C"
    
    sentido = 1
    jugador_actual = 0
    continuar = True

    while continuar:
        if len(baraja) <= 0:
            continuar = False
            break

        jugador = jugadores[jugador_actual]
        print('\n' + Style.BRIGHT + Fore.YELLOW + '--------------------------------')
        print('\n' + Style.BRIGHT + Fore.WHITE + 'Turno de ' + jugador['nombre'] + '\n')

        if jugador['nombre'] == 'CPU':
            cartaEscogida, baraja = jugarCarta(jugador, monton[-1], baraja, monton, jugadores, jugador_actual, sentido)
        else:
            cartaEscogida, baraja = escoger_carta(jugador, monton[-1], baraja, monton)

        if cartaEscogida:
            if jugador['nombre'] == 'CPU':
                actualizar_estadisticas_CPU_tras_jugada(cartaEscogida, jugador)
                afectar_estadisticas_otros_jugadores_por_CPU(jugadores, cartaEscogida)
            else:
                actualizar_estadisticas_jugador(jugador, cartaEscogida, monton[-1])
                afectar_estadisticas_otros_jugadores_por_jugador(jugadores, jugador, cartaEscogida)
                afectar_estadisticas_CPU_por_jugada(jugadores, cartaEscogida)
        else:
            if jugador['nombre'] != 'CPU':
                actualizar_estadisticas_jugador(jugador, None, monton[-1], robo=True)

        if cartaEscogida:
            if isinstance(cartaEscogida, dict):
                if cartaEscogida['valor'] == 'C' and cartaEscogida['color'] == 'NE':
                    color_aleatorio = random.choice(['AZ', 'VE', 'RO', 'AM'])
                    cartaEscogida['color'] = color_aleatorio
                    cartaEscogida['carta'] = color_aleatorio + "#C"
                monton.append(cartaEscogida['carta'])
            else:
                if cartaEscogida == 'NE#C':
                    color_aleatorio = random.choice(['AZ', 'VE', 'RO', 'AM'])
                    cartaEscogida = color_aleatorio + "#C"
                monton.append(cartaEscogida)

            if isinstance(cartaEscogida, dict):
                valor = cartaEscogida['valor']
            else:
                _, valor = separar_carta(cartaEscogida)

            if valor == 'R':
                sentido = efecto_reversa(sentido, jugadores)
                if len(jugadores) == 2:
                    jugador_actual = efecto_bloqueo(jugador_actual, sentido, jugadores)
            elif valor == 'S':
                jugador_actual = efecto_bloqueo(jugador_actual, sentido, jugadores)
            elif valor == '+2':
                print("¡El siguiente jugador deberá robar 2 cartas!")
                robar(jugadores[(jugador_actual + sentido) % len(jugadores)], 2, baraja)
                jugador_actual = (jugador_actual + sentido) % len(jugadores)

        jugador_obj_actual = jugadores[jugador_actual]

        if len(jugador["mano"]) == 0:
            continuar = False
            print(jugador["nombre"] + " GANA LA PARTIDA")
            break

        for jugador in jugadores:
            carta = None
            if jugador is jugador_obj_actual:
                # cartaEscogida puede ser string o dict
                if isinstance(cartaEscogida, dict):
                    carta = cartaEscogida.get('carta', '')
                else:
                    carta = cartaEscogida or ''
            
            df_historial = mostrar_estadistica(jugador, df_historial, turno=turno, carta_jugada=carta)

        turno += 1


        jugador_actual = (jugador_actual + sentido) % len(jugadores)
        time.sleep(1)

        df_historial.to_csv("historial_juego10.csv", index=False) # o guardarlo con df_historial.to_csv()


        if os.path.exists("historial_juego10.csv"):
            print("✅ Archivo guardado correctamente.")
        else:
            print("❌ No se pudo guardar el archivo.")


if __name__ == "__main__":
    Iniciar_juego()