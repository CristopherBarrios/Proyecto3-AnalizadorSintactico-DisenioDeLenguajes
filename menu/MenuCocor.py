from Cocor.Cocor import Cocor
from functions.functions import functions
import pickle
from direct.DirectAFDWords import DirectAFDWords

def bienvenidoCocor():
    print("\n-------------------- Coco/R tests ----------------------")
    print("")


def menuCocor():
    print("Selecionar opcion: ")
    print("\t1. Leer archivos")
    print("\t2. Metodo de Conversion Directa y generar Scanner.py")
    print("\t3. Salir")

####COCOR________________________________________________________________________________________________
def mainCocor():
    bienvenidoCocor()
    coco_obj = Cocor()

    postfixRegex = []
    def_file = ''
    while True:

        menuCocor()
        option = input('Ingrese una opcion: ')
        print("")

        if(option == '1'):
            def_file = input('Ingrese el nombre del archivo con las definiciones (Ej. 1.atg): ')
            print("")
        
            coco_obj.read_def_cfg(def_file)

            postfixRegex = coco_obj.expresionSubstitutions()

            tks = coco_obj.getTokens()
            chars = coco_obj.getCharacters()
            kws = coco_obj.getKeywods()

        elif(option == '2'):
            # Pruebas de funcionalidad

            if(postfixRegex == ['ERROR_POSTFIX_)']):
                print('\n ")" faltante en la expresion regular ingresdigit. Vuelva a intentar. \n')
            else:
                print(' - postfix     = '+ str(postfixRegex))
                tokens = functions.getRegExUniqueTokensV2(postfixRegex)
                print(' - alfabeto (tokens): '+str(tokens))

                #chain = 'digit letter digit letter letter'
                chain = '12356'

                objdirect = DirectAFDWords(tokens,chain,postfixRegex,chars,tks,kws)
                AFD = objdirect.generateDirectAFD()

                # Its important to use binary mode
                store_transitions = open('Cocor/archivosGenerados/scanner'+def_file[:-4]+'.scann'.lower(), 'ab')
                # source, destination
                pickle.dump(objdirect, store_transitions)                     
                store_transitions.close()

                f = open("Cocor/archivosGenerados/ParserScanner/Scanner.py", "w", encoding='utf8')
                f.write(
'''

# imports__________________________

import os
from os.path import basename
import sys
sys.path.append(".")

from Cocor.TokenImplictData import *
from menu.Menu import *

import time
import pickle
import string


# Clase de implementacion_________________________________________________

class Scanner:
    """Archivo que utiliza las transiciones del AFD generado
    a partir de una gramatica cualquiera escrita en COCO/R,
    para reconocer los tokens un archivo de prueba cualquiera.
    """
    def __init__(self,testFile = 'test_file.txt'):
        self.scanner = pickle.load(open('Cocor/archivosGenerados/scanner'+testFile[:-4]+'.scann'.lower(),'rb'))
        self.resultAFDArray = self.scanner.resultAFDArray
        self.acceptingStatesIdentifiers = self.scanner.acceptingStatesIdentifiers
        
        self.scannedTokens = []

        self.testFile = os.getcwd() + '\\\\Cocor\\\\tests\\\\' + testFile
        self.line_to_read = ''

        
    def read_test_file(self):
        """Funcion para leer el archivo de prueba 
            y almacenar sus contenidos.
        """
        here = os.path.dirname(os.path.abspath(__file__))
        file_ = self.testFile
        filepath = os.path.join(here, file_)
        with open(filepath, 'r') as fp:
            line = fp.readline()
            while line:
                print("File contents: {}".format(line.strip()))
                print('')
                self.line_to_read += line
                line = fp.readline()


    def getStateId(self, states_list):
        """Regresara el identificador del estado

        Args:
            states_list (list): lista de estados

        Returns:
            int: el estado
        """
        for value in self.resultAFDArray:
            if(value[1] == states_list):
                return value[0]


    def move(self,states_set,character):
        """Representacion de la funcion move(A,a) 
        para la simulacion del AFD formado a partir 
        de los tokens definidos en un archivo atg.

        - Args:
            - states_set (list): arreglo de estados
            - c_state (set): el caracter o estado en cuestion

        - Returns:
            - list: nuevo array de estados si hay transicion
        """
        new_states_array = []
        for state in states_set:
            # trans sera nuestra transicion y debemos 
            # verificar si el caracter en cuestion esta
            # en ese set con uno o varios valores
            for trans in self.resultAFDArray:
                inSet = (ord(character)) in trans[2]
                if( inSet and len(trans[3]) > 0 and state == trans[0]):
                    nextState = self.getStateId(trans[3])
                    if(nextState not in new_states_array):
                        new_states_array.append(nextState)
        return new_states_array


    def getTokenExplicitIdentifierV2(self, tokenArray):
        """Funcion que retornara el identificador explicito 
        del token en cuestion. Retornara el lado izquierdo
        de la expresion, por asi decirlo. 
        Ej. [number = digit(digit)*] --> <number>

        Args:
            estados (list): lista de estados

        Returns:
            set: el set con los posibles caracteres pertenecientes
            a ese token particular
        """
        statesSetList = []; tokenExplicitIdentifier = ""
        finalStates = self.scanner.getFinalStateId()
        for value in self.resultAFDArray:
            for finalState in finalStates:
                if(str(finalState) in value[1]):
                    for current_token in tokenArray:
                        if(current_token == value[0]):
                            if(value[1] not in statesSetList): statesSetList.append(value[1])

        acceptingIdentifier = {}
        acceptingIdentifierNumbers = []
        # En esta seccion se comprobara 
        # cual es el identificador explicito
        # del token
        for statesSet in statesSetList:
            for posibleState in statesSet:
                for keyy, value in self.acceptingStatesIdentifiers.items():
                    if(int(posibleState) == keyy): acceptingIdentifier[keyy] = value; acceptingIdentifierNumbers.append(keyy)

        # En caso que la lista de identificadores 
        # tuviera varios elementos
        if(len(acceptingIdentifier) > 1):
            minValueIdent = min(acceptingIdentifierNumbers)
            for keyy, value in acceptingIdentifier.items():
                if(minValueIdent == keyy): tokenExplicitIdentifier = value
        else:
            for keyy, value in acceptingIdentifier.items(): tokenExplicitIdentifier = value

        return tokenExplicitIdentifier


    def dumpTokensLeidos(self):
        dumpFile = open('Cocor/archivosGenerados/tokensInFile', 'wb')
        pickle.dump(self.scannedTokens, dumpFile)
        dumpFile.close()


    def simulation(self):
        """Funcion para simular una linea de entrada
        desde un archivo de prueba.

        - Returns:
            - int: 0
        """

        #contador local para llevar la posicion del caracter leido
        counter = 0

        #la dinamica aqui es leer un token y leer al mismo tiempo el siguiente
        # para saber si existira transicion cuando pasemos al siguiente
        # caracter leido, de lo contrario no sabriamos como continuar 
        # en cierto punto
        S = [0]; S_next = [0]

        #construccion de la cadena leida
        token_construction = ""
        #acumulador de estados
        string_array = []

        # En este ciclo encapsularemos cada uno de 
        # los caracteres de la linea de entrada
        for character in self.line_to_read: string_array.append(character)

        #insertamos un espacio vacio al inicio
        string_array.append(" ")
        
        #Este caso se da cuando hay un solo token en el archivo
        while len(string_array) > 0:
            if(counter == len(self.line_to_read)-1):
                characterToEvaluate = self.line_to_read[counter]
                token_construction += characterToEvaluate
                S = self.move(S,characterToEvaluate)
                token = self.getTokenExplicitIdentifierV2(S)
                scannedToken = TokenImplicitData()
                if(len(token) == 0):
                    print('Invalid token: ', token_construction)
                    scannedToken.set_token_type("__error__"); scannedToken.set_value(token_construction); self.scannedTokens.append(scannedToken)
                    break
                else:
                    print('token: '+ token_construction + ' has type: '+str(token))
                    scannedToken.set_token_type(token); scannedToken.set_value(token_construction); self.scannedTokens.append(scannedToken)
                    break
            characterToEvaluate = self.line_to_read[counter]
            nextCharacterToEvaluate = self.line_to_read[counter+1]
            token_construction += characterToEvaluate
            S = self.move(S,characterToEvaluate)
            S_next = self.move(S,nextCharacterToEvaluate)

            # Este caso se da cuando a travez del siguiente token ya no hay 
            # transicion hacia otro estado
            if(len(S) > 0 and len(S_next) == 0):  
                token = self.getTokenExplicitIdentifierV2(S)
                scannedToken = TokenImplicitData()
                if(len(token) == 0):
                    print('Invalid token: ', token_construction)
                    S = [0]; S_next = [0]
                    scannedToken.set_token_type("__error__"); scannedToken.set_value(token_construction); self.scannedTokens.append(scannedToken)
                    token_construction = ""; counter -= 1
                else:
                    print('token: '+ token_construction + ' has type: '+str(token))
                    S = [0]; S_next = [0]
                    scannedToken.set_token_type(token); scannedToken.set_value(token_construction); self.scannedTokens.append(scannedToken)
                    token_construction = ""
            elif(len(S) == 0):
                print('Invalid token: ', token_construction)
                S = [0]; S_next = [0]
                scannedToken = TokenImplicitData()
                scannedToken.set_token_type("__error__"); scannedToken.set_value(token_construction); self.scannedTokens.append(scannedToken)
                token_construction = ""

            counter += 1
            character_popping = string_array.pop()

        print('')



# tests__________
if __name__ == "__main__":
    mainScanner()
'''
                )

                f.close()

        elif(option == '3'):
            print('\nAdios! ')
            break
        else:
            input('No se ha elejido ninguna opcion en el menu. Intentalo otra vez! Enter -->')

functions = functions()
