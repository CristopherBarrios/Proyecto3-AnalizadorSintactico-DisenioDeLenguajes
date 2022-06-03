######################################################
# Programa que evalua producciones definidas en un 
# atg y construye la representacion postfix del arbol
# de parse apra el analisis lexico
######################################################

# This code is contributed by Nikhil Kumar Singh(nickzuck_007)
# # This code is contributed by Amarnath Reddy
# https://www.geeksforgeeks.org/stack-set-4-evaluation-postfix-expression/

#! imports 
from functions.functions import *

class ProductionPostfix:

    def __init__(self):
        

        self.precedence = {
            '_or': 1, 
            '_append': 2}
        self.postfixResult = []; self.operandsArray = []
        self.top = -1


    # verificacion de pila vacia
    def is_empty_none(self): return True if self.top == -1 else False

    # devolver el valor tope de la pila
    def take_top_of_stack(self): return self.operandsArray[-1]

    # verificacion si el token en 
    # cuestion tiene una presedencia
    # menor al token en el tope de la pila
    def greater_precedence(self, i):
        try:
            a = self.precedence[i.get_symbol_type()]; b_updated = self.take_top_of_stack(); b = self.precedence[b_updated.get_symbol_type()]; return True if a <= b else False
        except KeyError: return False

    # pop de un elemento de la pila
    def pop(self):
        # si no esta vacío
        # el top es -1 e 
        # indica el vacio
        if not self.is_empty_none():  self.top -= 1; return self.operandsArray.pop()  
        else: return "&"  # de lo contrario un valor espaecial


    def push(self, op): self.top += 1; self.operandsArray.append(op)

     # verificacion de no operador
    def not_op(self, tokenObject):
        if (tokenObject.get_symbol_type() == 'non_terminal'or tokenObject.get_symbol_type() == '_terminal' or tokenObject.get_symbol_type() == '_action'): return True
        return False

    # Verificacion de operador
    def isOp(self, tokenObject):
        if tokenObject.get_symbol_type() == '_or' or tokenObject.get_symbol_type() == '_append':
            return True
        return False

    def infix_to_postfix_prods(self, exp):
        for i in exp:
            # si el caracter actual 
            # es operando entonces 
            # se agrega al arreglo 
            # de resultado
            if i.get_symbol_type() == "production_name": self.postfixResult.append(i)
            elif self.not_op(i): self.postfixResult.append(i)
            elif self.isOp(i):
                while (len(self.operandsArray) > 0 and self.operandsArray[-1].get_symbol_type() != 'open_conditional_or_id' and self.operandsArray[-1].get_symbol_type() != 'open_while_cycle' and self.operandsArray[-1].get_symbol_type() != 'open_bracket' and self.greater_precedence(i)):
                    top = self.pop(); self.postfixResult.append(top)
                self.push(i)
            # se es parentesis de 
            # apertura se agrega a la pila
            elif (i.get_symbol_type() == 'open_conditional_or_id' or i.get_symbol_type() == 'open_while_cycle' or i.get_symbol_type() == 'open_bracket'): self.postfixResult.append(i); self.push(i)
            # Si el character es parentesis 
            # de cierre, se hace pop y se busca hasta encontrar
            elif (i.get_symbol_type() == 'closure_conditional_or_id' or i.get_symbol_type() == 'closure_while_cycle' or i.get_symbol_type() == 'closure_bracket'):
                # while not empty and is distinct from "("
                while((not self.is_empty_none()) and self.take_top_of_stack().get_symbol_type() != 'open_conditional_or_id' and self.take_top_of_stack().get_symbol_type() != 'open_while_cycle' and self.take_top_of_stack().get_symbol_type() != 'open_bracket'):
                    a = ""; a = self.pop()  # pop
                    self.postfixResult.append(a)  # add to postfixResult
                    if (a == ""): print("Parentesis de cerradura faltante"); return -1
                self.postfixResult.append(i)
                # se retorna -1 en dado caso lleguemos hasta el ciclo while
                if (not self.is_empty_none() and self.take_top_of_stack().get_symbol_type() != 'open_conditional_or_id' and self.take_top_of_stack().get_symbol_type() != 'open_while_cycle' and self.take_top_of_stack().get_symbol_type() != 'open_bracket'): return -1
                else: self.pop()  # sino, entonces pop

         # verificacion de parentesis de apertura
        while len(self.operandsArray):
            character = self.pop()
            if (character.get_symbol_type() == "open_conditional_or_id" or character.get_symbol_type() == "open_while_cycle" or character.get_symbol_type() == "open_bracket"): 
                return "error_posfix_error"
            self.postfixResult.append(character)

        return self.postfixResult




