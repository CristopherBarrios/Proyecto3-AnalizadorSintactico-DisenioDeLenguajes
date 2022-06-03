
# imports _________________________
import os
import sys
import glob
sys.path.append(".")
from menu.MenuCocor import *



# functions ________________________
def bienvenido():
    print("")
    print("========================================================")
    print("---------------------- Bienvenido ----------------------")
    print("========================================================")
    print("")


def bienvenidoMenuPrincipal():
    print("-------------------- Menu principal ---------------------")
    print("")


def bienvenidoScanner():
    print("\n--------------------- SCANNER -------------------------")
    print("")


def bienvenidoParser():
    print("\n---------------------- Parser -------------------------")


def menuPrincipal():
    print("Selecionar opcion: ")
    print("1. Coco/R tests.")
    print("2. SCANNER")
    print("3. Parser")
    print("4. Limpiar Memoria")
    print("5. Salir del programa")


def menuScanner():
    print("Seleccione una opcion.")
    print("	1. Leer archivo de prueba")
    print("	2. Salir")


####SCANNER______________________________________________________________________________________________
def mainScanner():
    from Cocor.archivosGenerados.ParserScanner.Scanner import Scanner
    bienvenidoScanner()

    while True:
        menuScanner()
        option = input('Ingrese una opcion: ')
        print("")

        if(option == '1'):
            file_name = str(input("Ingrese el nombre del archivo de prueba (Ej. 1.txt): "))
            print("")

            obj = Scanner(file_name)
            obj.read_test_file()
            obj.simulation()
            obj.dumpTokensLeidos()

        elif(option == '2'):
            print('Adios! ')
            break
        else:
            input('No se ha elejido ninguna opcion en el menu. Intentalo de nuevo! Enter -->')


####PARSER________________________________________________________________________________________________
def mainParser():
    bienvenidoParser()
    from Cocor.archivosGenerados.ParserScanner.Parser import Parser
    obj = Parser()
    obj.readDumpStates()
    obj.Main()


def limpiarMemoria():
    files = glob.glob(os.getcwd()+'/Cocor/archivosGenerados/**', recursive=True)
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            a = e
    input('La memoria se ha limpiado correctamente Enter -->')


def main():
    bienvenido()
    while True:
        bienvenidoMenuPrincipal()
        menuPrincipal()
        option = input('ingrese una opcion: ')
        print("")

        if(option == '1'):
            mainCocor()
        elif(option == '2'):
            mainScanner()
        elif(option == '3'):
            mainParser()
        elif(option == '4'):
            limpiarMemoria()
        elif(option == '5'):
            print('\nAdios! ')
            break
        else:
            input('No se ha elejido ninguna opcion en el menu. Intentalo de nuevo! Enter -->')    