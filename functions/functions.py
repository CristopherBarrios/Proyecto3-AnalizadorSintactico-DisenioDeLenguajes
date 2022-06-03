class functions:
    """functions class
    """
    def getRegExUniqueTokensV2(self,postfix_regex):
        '''
        Funcion que obtiene los tokens unicos o el lenguaje de una expresion regular en formato postfix.
        '''
        ops = '*|~#'
        tokens = []
        for i in range(len(postfix_regex)):
            token = postfix_regex[i]

            if(token != '*' and token != '|' and token != '~' and token != '#'):
                tokens.append(token)

        tokens_ = []
        [tokens_.append(x) for x in tokens if x not in tokens_]

        return tokens_


    def isOperandV2(self,character):
        """
        REtorna TRUE si el caracter ingresado es un alfanumerico, FALSE de lo contrario
        *@param ch: el caracter a ser probado
        """
        sett = False
        if (isinstance(character,set)): sett = True
        if sett or character == "ε" or character == "#":
            return True
        return False


    def get_value_from_dict(self,ext_key,dictionary):
        '''
        Funcion que retorna la llave para un caracter cualquiera en un diccionario.

        Parametros:
        - character: un caracter o token 
        '''
        for key, value in dictionary.items():
            if ext_key == key:
                return value

        return None