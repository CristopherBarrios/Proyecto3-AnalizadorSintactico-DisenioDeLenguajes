######################################################
# Programa que evalua una expresion regular en notacion
# infix, sustituye operadores equivalentes y la 
# traduce a notacion postfix 
######################################################

#Clase de implementacion_________________________________________________
class InfixRegexToPostfixWords:
    '''
    Clase que convierte una expresion infix a formato postfix

    Atributos:
     - expresion --> la expresion regular en formato infix
    '''
    # Constructor de las variables
    def __init__(self):
        self.operators_precedence = {
        1: '(',
        2: '|',
        3: '~', # operador de concatenacion explicito
        4: '?',
        4: '*',
        4: '+'
        }


    def get_key(self,character):
        '''
        Funcion que retorna la llave para un caracter cualquiera.

        Parametros:
        - character: un caracter o token 
        '''
        for key, value in self.operators_precedence.items():
            if character == value:
                return key
        return None


    def get_precendence(self,character):
        '''
        Funcion que retorna la precedencia del operador ingresado.
        Parametros:
        - character: un caracter o token
        - return - la precedencia correspondiente
        '''
        precedence = self.get_key(character)
        precedence = 5 if precedence == None else precedence
        return precedence


    def infix_to_postfix(self,expresion):
        '''
        Funcion que convierte una expresion regular en formato infix a formato postfix.
        Esta expresion regular es ingresada al instancia un objeto de esta clase.
        '''
        postfix = ''
        postfix_exp = []
        stack = []

        #!la expresion ya viene lista para pasarse a posfix
        eqRegex = expresion

        for cc in range(len(eqRegex)):
            c = eqRegex[cc]
            if (c == '('):
                stack.append(c)
            elif(c == ')'):
                #si el ultimo elemento de la pila es '(' 
                while (stack[-1] != '('): 
                    postfix_exp.append(stack.pop())

                stack.pop();
            else:
                while(len(stack) > 0):
                    peekedChar = stack[-1]

                    peekedCharPrecedence = self.get_precendence(peekedChar)
                    currentCharPrecedence = self.get_precendence(c)

                    if(peekedCharPrecedence >= currentCharPrecedence):
                        postfix_exp.append(stack.pop())
                    else:
                        break

                stack.append(c)

        while(len(stack) > 0):
            postfix_exp.append(stack.pop())

        if('(' in postfix_exp):
            postfix_exp = ['ERROR_POSTFIX_)']
        print(' - infixEq     = '+str(eqRegex))
        print(' - postfix     = '+str(postfix_exp))

        return postfix_exp