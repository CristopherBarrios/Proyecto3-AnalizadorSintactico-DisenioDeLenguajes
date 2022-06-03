
# zona de imports de librerías
import time
import collections
import sys
sys.path.append(".")
from functions.functions import *
from graphs.NodeD import *

class DirectAFDWords:
    """Clase que comvierte una expresion regular en formato postfix a un automara finito determinista AFD.
    """

    def __init__(self, tokens, chain, postfixRegex,chars,tks,kws):
        self.expresionPostfix = postfixRegex
        self.tokens = tokens
        
        self.globalCounter = 1
        self.globalCounter2 = 0
        self.nextPosDict = {}
        self.functions = functions()
        self.DStates = []
        self.DStates2 = []
        
        self.nodesArray = []
        self.resultAFD = {}
        self.resultAFDArray = []
        # variables para el AFN
        
        #cocor related
        self.tokenIdentifiers = tks

        self.acceptingStatesIdentifiers = {}
        self.identifiersCounter = 0

        #zzz
        self.chain = chain
        self.characters = chars
        self.keywords = kws


        
    def getPosFromCharacter(self, character):
        """
        Dada una letra, nos retorna el valor 
        de id de esa letra. Puede haber varias
        """
        array = []
        for num, node in self.resultAFD.items():
            if(node.getNodeChar() == character):
                array.append(node.getNodeId())

        return array


    def getFinalStateId(self):
        """Obtenemos los estados finales del 
        diccionario de nextPost.
            
        Returns:
            list: el estado final de nextPos
        """
        accepting_states = []
        for num, value in self.nextPosDict.items():
            if len(value) == 0:
                accepting_states.append(num)

        return accepting_states


    def getAcceptingStatesAFD(self):
        """Obtenemos estados de aceptacion 
        del AFD

        Returns:
            list: los estados de aceptacion 
            del afd
        """
        arrayValores = []
        for value in self.resultAFDArray:
            finalstates = self.getFinalStateId()
            for fstate in finalstates:
                if(str(fstate) in value[1]):
                    arrayValores.append(value[0])

        return arrayValores


    def isAnnullable(self, Nodes, character):
        """Tabla magica para anulable de cada 
        nodo en question

        Args:
            Nodes (list): array de nodos
            character (str): el caracter en cuestion

        Returns:
            bool: es anulable o no
        """
        if(character == "ε"):
            return True
        else:
            if(self.functions.isOperandV2(character)):
                return False
            elif (character == "|"):
                nodeC1 = Nodes.pop()
                nodeC2 = Nodes.pop()
                annullableC1 = nodeC1.getAnnullable()
                annullableC2 = nodeC2.getAnnullable()
                return (annullableC1 or annullableC2)
            elif(character == '~'):
                nodeC1 = Nodes.pop()
                nodeC2 = Nodes.pop()
                annullableC1 = nodeC1.getAnnullable()
                annullableC2 = nodeC2.getAnnullable()
                return (annullableC1 and annullableC2)
            elif(character == "*"):
                nodeC1 = Nodes.pop()
                annullableC1 = nodeC1.getAnnullable()
                return (True)

        return "FALSE"


    def firstPos(self, Nodes, character):
        """Tabla magica para firstPos de un 
        nodo en cuestion

        Args:
            Nodes (list): array de nodos
            character (str): el caracter en cuestion

        Returns:
            list: los estados pertenecientes a firstPos del nodo en cuestion
        """
        if(character == "ε"):
            return ""
        else:
            if(self.functions.isOperandV2(character)):
                nodeC1 = Nodes.pop()
                nodeC1Id = nodeC1.getNodeId()
                return [nodeC1Id]
            elif (character == "|"):
                nodeC1 = Nodes.pop()
                nodeC2 = Nodes.pop()
                firstPosC1 = nodeC1.get_first_pos()
                firstPosC2 = nodeC2.get_first_pos()
                if(firstPosC1 == ""): firstPosC1 = []
                if(firstPosC2 == ""): firstPosC2 = []
                arrayFinalOr = firstPosC1+firstPosC2
                #ordenamiento
                arrayFinalOr = list(dict.fromkeys(arrayFinalOr))
                arrayFinalOr.sort()

                return arrayFinalOr
            elif(character == '~'):
                nodeC1 = Nodes.pop()
                nodeC2 = Nodes.pop()
                annullableC1 = nodeC1.getAnnullable()
                firstPosC1 = nodeC1.get_first_pos()
                firstPosC2 = nodeC2.get_first_pos()
                if(firstPosC1 == ""): firstPosC1 = []
                if(firstPosC2 == ""): firstPosC2 = []
                if(annullableC1): arrayFinalAND = firstPosC1+firstPosC2
                else: arrayFinalAND = firstPosC1

                #ordenamiento
                arrayFinalAND = list(dict.fromkeys(arrayFinalAND))
                arrayFinalAND.sort()

                return arrayFinalAND
            elif(character == "*"):
                nodeC1 = Nodes.pop()
                firstPosC1 = nodeC1.get_first_pos()
                if(firstPosC1 == ""): firstPosC1 = []
                arrayFinalKleene = firstPosC1
                #ordenamiento
                arrayFinalKleene = list(dict.fromkeys(arrayFinalKleene))
                arrayFinalKleene.sort()

                return arrayFinalKleene
        return "FALSE"


    def lastPos(self, Nodes, character):
        """Tabla magica para lastPos de un nodo 
        en cuestion

        Args:
            Nodes (list): array de nodos
            character (str): el caracter en cuestion

        Returns:
            list: los estados pertenecientes a lastPos del nodo 
            en cuestion
        """
        if(character == "ε"):
            return ""
        else:
            # si es un character, entonces regresaremo el mismo 
            # id, esa seria la primera pos
            if(self.functions.isOperandV2(character)):
                nodeC1 = Nodes.pop()
                nodeC1Id = nodeC1.getNodeId()
                return [nodeC1Id]
            elif (character == "|"):
                nodeC1 = Nodes.pop()
                nodeC2 = Nodes.pop()
                lastPosC1 = nodeC1.getLastPos()
                lastPosC2 = nodeC2.getLastPos()
                if(lastPosC1 == ""): lastPosC1 = []
                if(lastPosC2 == ""): lastPosC2 = []
                arrayFinalOr = lastPosC1+lastPosC2
                #ordenamiento
                arrayFinalOr = list(dict.fromkeys(arrayFinalOr))
                arrayFinalOr.sort()

                return arrayFinalOr
            elif(character == '~'):
                nodeC1 = Nodes.pop()
                nodeC2 = Nodes.pop()
                annullableC2 = nodeC2.getAnnullable()
                lastPosC1 = nodeC1.getLastPos()
                lastPosC2 = nodeC2.getLastPos()
                if(lastPosC1 == ""): lastPosC1 = []
                if(lastPosC2 == ""): lastPosC2 = []
                if(annullableC2): arrayFinalAND = lastPosC1+lastPosC2
                else: arrayFinalAND = lastPosC2
                #ordenamiento
                arrayFinalAND = list(dict.fromkeys(arrayFinalAND))
                arrayFinalAND.sort()

                return arrayFinalAND
            elif(character == "*"):
                nodeC1 = Nodes.pop()
                lastPosC1 = nodeC1.getLastPos()
                if(lastPosC1 == ""):
                    lastPosC1 = []
                arrayFinalKleene = lastPosC1
                #ordenamiento
                arrayFinalKleene = list(dict.fromkeys(arrayFinalKleene))
                arrayFinalKleene.sort()

                return arrayFinalKleene
        return "FALSE"


    def nextPos(self, Nodes, character):
        """Tabla magica para nextPos(followPos) 
        de un nodo en cuestion

        Args:
            Nodes (list): array de nodos
            character (str): el caracter en cuestion

        Returns:
            list: los estados pertenecientes a nextPos
             del nodo en cuestion
        """
        # si es character, retorna el mismo id, esa seria la firstpos
        if(character == '~'):
            nodeC1 = Nodes.pop()
            nodeC2 = Nodes.pop()

            lastPosC1 = nodeC1.getLastPos()
            firstPosC2 = nodeC2.get_first_pos()
            if(firstPosC2 == ""):
                firstPosC2 = []
            if(lastPosC1 == ""):
                lastPosC1 = []

            arrayTemporal = []
            for x in lastPosC1:
                arrayTemporal = self.nextPosDict[int(x)]
                arrayTemporal = arrayTemporal+firstPosC2
                #ordenamiento
                arrayTemporal = list(dict.fromkeys(arrayTemporal))
                arrayTemporal.sort()
                self.nextPosDict[int(x)] = arrayTemporal
        if(character == "*"):
            nodeC1 = Nodes.pop()
            lastPosC1 = nodeC1.getLastPos()
            firstPosC1 = nodeC1.get_first_pos()
            if(lastPosC1 == ""):
                lastPosC1 = []
            if(firstPosC1 == ""):
                firstPosC1 = []
            for x in lastPosC1:
                arrayTemporal = self.nextPosDict[int(x)]
                arrayTemporal = arrayTemporal+firstPosC1
                #ordenamiento
                arrayTemporal = list(dict.fromkeys(arrayTemporal))
                arrayTemporal.sort()
                self.nextPosDict[int(x)] = arrayTemporal


    def generateDirectAFD(self):
        """Funcion que centraliza el calculo de anulable, 
        firstPos, lastPos y nextPost(followPos) 
        para obtener el AFD de resultado.
        """
        # comenzamos a construir el arbol 
        for postfixValue in self.expresionPostfix:
            if(self.functions.isOperandV2(postfixValue)): # letra
                if(postfixValue == "ε"):  # si es un 'ε' entonces no se le agrega numeración
                    nodeFirstPos = ""
                    nodeLastPos = ""
                    node = NodeD()
                    node.setCaracterNodo(postfixValue)
                    node.setNodoId("")

                    node.setAnnullable(self.isAnnullable(node, postfixValue))
                    nodeFirstPos = [node]
                    nodeLastPos = [node]
                    node.setFirstPos(self.firstPos(nodeFirstPos, postfixValue))
                    node.setLastPos(self.lastPos(nodeLastPos, postfixValue))
                    self.resultAFD[self.globalCounter2] = node
                    self.globalCounter2 += 1
                    self.nodesArray.append(node)  # agregamos el nodo
                else:  # cualquier otra letra INCLUYENDO el # lleva numeracion
                    node = NodeD()
                    nodeFirstPos = ""
                    nodeLastPos = ""
                    node.setCaracterNodo(postfixValue)
                    node.setNodoId(str(self.globalCounter))
                    self.nextPosDict[self.globalCounter] = []

                    if(postfixValue == "#"):
                        self.acceptingStatesIdentifiers[self.globalCounter] = list(self.tokenIdentifiers.keys())[self.identifiersCounter]
                        self.identifiersCounter += 1

                    self.globalCounter += 1  # aumentamos el counter global
                    nodeFirstPos = [node]
                    nodeLastPos = [node]
                    node.setAnnullable(self.isAnnullable(node, postfixValue))
                    node.setFirstPos(self.firstPos(nodeFirstPos, postfixValue))
                    node.setLastPos(self.lastPos(nodeLastPos, postfixValue))
                    self.resultAFD[self.globalCounter2] = node

                    self.globalCounter2 += 1
                    self.nodesArray.append(node)  # agregamos el nodo
            # el OR es operador por lo tanto no tiene numero
            elif(postfixValue == "|"):  
                nodeOrAnulable = ""
                nodeOrfirstPos = ""
                nodeOrlastPos = ""
                nodeOr = NodeD()
                nodeOr.setCaracterNodo(postfixValue)
                nodeOr.setNodoId("")
                nodeb = self.nodesArray.pop()
                nodea = self.nodesArray.pop()
                nodeOrAnulable = [nodeb, nodea]
                nodeOrfirstPos = [nodeb, nodea]
                nodeOrlastPos = [nodeb, nodea]
                nodeOr.setAnnullable(self.isAnnullable(nodeOrAnulable, postfixValue))
                nodeOr.setFirstPos(self.firstPos(nodeOrfirstPos, postfixValue))
                nodeOr.setLastPos(self.lastPos(nodeOrlastPos, postfixValue))
                # agregar al diccionario AFD de resultado global
                self.resultAFD[self.globalCounter2] = nodeOr
                self.globalCounter2 += 1
                self.nodesArray.append(nodeOr)  # se agrega el nodo en cuestion

            # el AND o concatenacion es operador por lo tanto no tiene numero
            elif(postfixValue == '~'):  
                nodeAndAnulable = ""
                nodeAndfirstPos = ""
                nodeAndlastPos = ""
                nodeAndSiguientePos = ""
                nodeAnd = NodeD()
                nodeAnd.setCaracterNodo(postfixValue)
                nodeAnd.setNodoId("")
                nodeb = self.nodesArray.pop()
                nodea = self.nodesArray.pop()
                nodeAndAnulable = [nodeb, nodea]
                nodeAndfirstPos = [nodeb, nodea]
                nodeAndlastPos = [nodeb, nodea]
                nodeAndSiguientePos = [nodeb, nodea]
                nodeAnd.setAnnullable(self.isAnnullable(nodeAndAnulable, postfixValue))
                nodeAnd.setFirstPos(self.firstPos(nodeAndfirstPos, postfixValue))
                nodeAnd.setLastPos(self.lastPos(nodeAndlastPos, postfixValue))
                self.nextPos(nodeAndSiguientePos, postfixValue)
                # agregar al diccionario AFD de resultado global
                self.resultAFD[self.globalCounter2] = nodeAnd
                self.globalCounter2 += 1
                self.nodesArray.append(nodeAnd)  # se agrega el nodo en cuestion

            # el * es operador por lo tanto no tiene numero
            elif(postfixValue == "*"):  
                nodeKleeneAnulable = ""
                nodeKleenefirstPos = ""
                nodeKleenelastPos = ""
                nodeKleeneSiguientePos = ""
                nodeKleene = NodeD()
                nodeKleene.setCaracterNodo(postfixValue)
                nodeKleene.setNodoId("")
                node = self.nodesArray.pop()
                nodeKleeneAnulable = [node]
                nodeKleenefirstPos = [node]
                nodeKleenelastPos = [node]
                nodeKleeneSiguientePos = [node]
                nodeKleene.setAnnullable(self.isAnnullable(nodeKleeneAnulable, postfixValue))
                nodeKleene.setFirstPos(self.firstPos(nodeKleenefirstPos, postfixValue))
                nodeKleene.setLastPos(self.lastPos(nodeKleenelastPos, postfixValue))
                self.nextPos(nodeKleeneSiguientePos, postfixValue)
                # agregar al diccionario AFD de resultado global
                self.resultAFD[self.globalCounter2] = nodeKleene
                self.globalCounter2 += 1
                self.nodesArray.append(nodeKleene) # se agrega el nodo en cuestion

        rootNode = self.nodesArray.pop()
        initStates = rootNode.get_first_pos()
        self.DStates.append(initStates)
        self.DStates2.append(initStates)
        counter = -1

        while len(self.DStates) > 0:
            internalState = self.DStates.pop()
            counter += 1
            for tokenn in self.tokens:
                if(tokenn != str("ε")):
                    tokenPos = self.getPosFromCharacter(tokenn)
                    nextPosID = []
                    for id in tokenPos:
                        if(id in internalState):
                            nextPosID = nextPosID + self.nextPosDict[int(id)]
                    if(not(nextPosID in self.DStates2)):
                        self.DStates.append(nextPosID)
                        self.DStates2.append(nextPosID)
                        self.resultAFDArray.append([counter, internalState, tokenn, nextPosID])
                    elif(len(internalState) > 0):
                        self.resultAFDArray.append([counter, internalState, tokenn, nextPosID])