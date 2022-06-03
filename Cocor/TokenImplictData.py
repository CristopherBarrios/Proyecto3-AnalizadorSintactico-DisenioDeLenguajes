######################################################
# Programa que encapsula infomacion relacionada a un 
# token en especifico.
######################################################


class TokenImplicitData:
    def __init__(self):
        self.tokenType = ""; self.enum = ""; self.val = ""

    #getssss
    def get_token_type(self):
        return self.tokenType

    def getNum(self): 
        return self.enum

    def get_value(self): 
        return self.val

    def get_token_info_v2(self): 
        return '~'.join([str(self.tokenType), str(self.val), str(self.enum)])

    def get_token_info(self): 
        return [self.tokenType, self.val, self.enum]

    #setsssssss
    def set_token_type(self, tipo): 
        self.tokenType = tipo

    def set_num(self, val): 
        self.enum = val
        
    def set_value(self, val):
        self.val = val
