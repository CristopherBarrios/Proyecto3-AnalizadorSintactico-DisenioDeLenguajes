######################################################
# Programa que encapsula infomacion relacionada a la
# lectura de producciones.
######################################################

#! zona de imports

from enum import Enum

class ProductionInplicitData():
    """Clase para el manejo de valores de las 
    producciones contenidas en las definicioens
    estipuladas del atg en cuestion.
    """
    def __init__(self, varType) -> None:
        self.firstPos = [] ;self.params = "" ;self.tokenOrder = "" ;self.isFunction = False ;self.ntName = ""; self.tName = ""; self.action = ""; self.varType = varType

    #getsss____________________

    def get_action(self):return self.action

    def get_terminal_name(self):return self.tName

    def get_non_terminal_name(self):return self.ntName

    def get_token_order(self):return self.tokenOrder

    def get_is_function(self):return self.isFunction

    def get_params(self):return self.params

    def get_first_pos(self):return self.firstPos

    def get_symbol_type(self):return self.varType.name

    def get_production_info(self):
        '''arr = [
            self.varType.name, 
            self.tName, 
            self.ntName, 
            self.action, 
            self.params, 
            self.firstPos, 
            self.tokenOrder
            ]
        return (
            arr
        )'''
        return [
        str(self.varType.name), 
        str(self.tName), 
        str(self.ntName), 
        str(self.action), 
        str(self.tokenOrder),
        str(list(self.params)), 
        str(set(self.firstPos))
        ]
        


    #setsss__________________________
    def set_action(self, parametro):self.action = parametro

    def set_terminal_name(self, parametro):self.tName = parametro
    
    def set_non_terminal_name(self, parametro):self.ntName = parametro

    def set_token_order(self, parametro):self.tokenOrder = parametro
    
    def set_is_function(self):self.isFunction = True
    
    def set_params(self, param):self.params =param

    def set_add_first_pos(self, parametro):self.firstPos.append(parametro)


class SymbolType(Enum):
    non_terminal                = 1
    _append = 2; _or = 3; _kleene = 4; _action = 5; 
    _terminal                   = 6
    open_conditional_or_id      = 7
    closure_conditional_or_id   = 8
    production_name             = 9
    open_while_cycle            = 10
    closure_while_cycle         = 11
    open_bracket                = 12
    closure_bracket             = 13