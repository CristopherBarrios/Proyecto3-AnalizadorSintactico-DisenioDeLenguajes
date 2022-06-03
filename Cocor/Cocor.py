######################################################
# Cocor.py
######################################################

#imports
import os
import sys
sys.path.append(".")
from os.path import basename
from functions.functions import functions
from infix_postfix_related.InfixRegexToPostfixWords import InfixRegexToPostfixWords
import pickle

#other
from infix_postfix_related.ProductionInplicitData import SymbolType, ProductionInplicitData
from infix_postfix_related.ProductionPostfix import ProductionPostfix


#Clase de implementacion_________________________________________________
class Cocor:
    """Clase con definiciones varias de COCO/R
    """
    # Constructor de las variables
    def __init__(self):
        
        #characters
        self.charactersInFile = {}
        self.charactersInFileSubs2 = {}

        #keywords
        self.keyWordsInFile = {}

        #tokens
        self.tokensInFile = {}
        self.tokensConvertionInFile = {}
        self.tokensReadyForPosFix = {}
        self.tokensSubstitutionExp = {}
        self.tokensSubstitution = {}
        self.finalExpression = {}

        self.tokensArray = []
        self.dictEnumTokens = {}
        
        #productions
        self.productionsInFile = {}
        self.productionsInFileStr = {}

        self.dictProdEnd2 = {}
        self.dictProdEnd = {}
        self.productions = []
        self.cCharact = []
        self.first_Pos_Dict = {}  # esta es la primera pos

        self.block_Prods = []
        self.tabulation = 1
        
        #classes
        self.functions = functions()
        self.objToPostfix = InfixRegexToPostfixWords()

# gets ------------------

    def getCharacters(self):
        return self.charactersInFileSubs2

    def getTokens(self):
        return self.tokensSubstitution

    def getKeywods(self):
        return self.keyWordsInFile
    

# ZONA PARA LA LECTURA DEL ARCHIVO-----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
    def read_def_cfg(self,file='def_file.cfg'):
        """Funcion para leer el archivo con la definicion de tokens
        """
        here = os.path.dirname(os.path.abspath(__file__))
        file_ = file
        filepath = os.path.join(here+'\\atgs\\', file_)
        header = ''

        #productions related
        productionBody = ''
        productionBodyStr = ''
        leftSide = ''
        prod_body = False
        #-------------------

        with open(filepath,'r') as fp:
            line = fp.readline()
            cnt = 1
            while line:
                line = line.rstrip()
                line.rstrip()
                if (not(line.startswith('(.')) or not(line.startswith('/*'))) and len(line) > 0:
                    if(line.startswith('CHARACTERS')):
                        header = 'CHARACTERS'
                    elif(line.startswith('KEYWORDS')):
                        header = 'KEYWORDS'
                    elif(line.startswith('TOKENS')):
                        header = 'TOKENS'
                    elif(line.startswith('PRODUCTIONS')):
                        header = 'PRODUCTIONS'

                    if('=' in line and header != 'PRODUCTIONS'):
                        arr_ = line.split('=')
                        arr_[0] = arr_[0].replace(' ','')
                        arr_[1] = arr_[1][:-1]
                        if(header == 'CHARACTERS'):
                            self.charactersInFile[arr_[0]] = arr_[1]
                        elif(header == 'KEYWORDS'):
                            self.keyWordsInFile[arr_[0]] = arr_[1]
                        elif(header == 'TOKENS'):
                            self.tokensInFile[arr_[0]] = arr_[1]
                    elif(header == 'PRODUCTIONS' and ('END' not in line)):
                        if not(line.startswith('PRODUCTIONS')):
                            if not(prod_body):
                                if '=' in line:
                                    line = line.replace('=','')
                                    line = line.replace(' ','')
                                    leftSide = line
                                    
                                    prod_body = True
                                else:
                                    leftSide += line
                                    line = fp.readline()
                                    cnt += 1
                                    leftSide += line
                                    leftSide = leftSide.replace('=','')
                                    leftSide = leftSide.replace(' ','')
                                    leftSide = leftSide.rstrip()
                                    
                                    prod_body = True
                            elif prod_body:
                                if line.count('.') == 1:
                                    line = line.replace(' ','')
                                    #si es verdadero entonces el punto esta al final de una expresion cualquiera y hay que quitarlo
                                     
                                    if(len(line) != 1):
                                        productionBody = line.replace('.','')
                                        productionBody,productionBodyStr = self.parseProduction(productionBody)
                                    #si es falso, entonces solo hay un punto en esa linea y se ignora
                                    else:
                                        #ahora aca tenemos todo el cuerpo de la produccion en una linea
                                        
                                        productionBody,productionBodyStr = self.parseProduction(productionBody)

                                    self.productionsInFile[leftSide] = productionBody
                                    self.productionsInFileStr[leftSide] = productionBodyStr
                                    
                                    self.isolatedProdNames(leftSide)
                                    

                                    prod_body = False
                                    leftSide = ''
                                    productionBody = ''
                                else:
                                    productionBody += line
                            elif line.count('.') == 1:
                                self.productionsInFile[leftSide] = productionBody
                                prod_body = False
                                leftSide = ''
                                productionBody = ''

                #print("Line {}: {}".format(cnt, line.strip()))
                line = fp.readline()
                cnt += 1

        self.charactersSubstitution()
        self.cocorToP1Convention()
        self.tokensPreparationPostfix()#

        self.orBetweenExpresions()

        #!para ver todos los tokens unidos en una expresion
        self.expresionSubstitutions()

        #!para ver cada uno de los tokens por separado
        self.tokensSubstitutions() 

        #!analizis de producciones
        self.prodsBuilding()
        print()
        self.prodsFIRST()
        print()
        self.FIRSTtoProds()
        print()

        filename = 'dictEnumTokens'
        resultDumpFile = open('Cocor/archivosGenerados/'+filename, 'wb')
        for i in range(len(self.tokensArray)):
            self.dictEnumTokens[self.tokensArray[i]] = i+1
        #print(self.dictEnumTokens)
        pickle.dump(self.dictEnumTokens, resultDumpFile)
        resultDumpFile.close()

        print("postfix convertion")
        cont = 0
        for key, production in self.dictProdEnd.items():
            cont += 1; postfixProduction = ProductionPostfix().infix_to_postfix_prods(production)
            for index in postfixProduction:
                ss = ', '.join(index.get_production_info())
                print("{"+ss+"}", end='  ¬  ')
            print('\n')
        print()

        self.parserConstructor()

# ZONA DE TRATAMIENTO DE PRODUCCIONES ---------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
    def isolatedProdNames(self,prodName):
        """Almacenamiento de los nombres de las producciones
        en cuestion en un array.

        - Args:
            - prodName (str): el nombre de la produccion en cuestion
        """
        founded = prodName.find('<')
        if(founded != -1):
            ind = prodName.index('<')
            toCut = len(prodName) - ind
            isoProdName = prodName[:-toCut]
            isoProdName = isoProdName.replace(' ','')
            self.productions.append(isoProdName)
        else:
            prodName = prodName.replace(' ','')
            self.productions.append(prodName)

    def prodCharac(self,charac):
        for c in charac:
            self.cCharact.append(c)

    def parseProduction(self,production):
        production = production.replace(' ','')
        prodArray = []
        c = 0
        while c < len(production):
            currentChar = production[c]
            if production[c] == " ":
                c += 1
            elif(production[c] in '}{|]['):
                prodArray.append(production[c])
                c += 1
            elif(production[c] == "(" and production[c+1] == "&"):
                prodArray.append(production[c]+production[c+1])
                c += 2
            elif(production[c] == "&" and production[c+1] == ")"):
                prodArray.append(production[c]+production[c+1])
                c += 2
            elif(production[c] == "$"):
                prodArray.append(production[c])
                c += 1
            elif(production[c] in "><"):
                prodArray, c = self.intoLessGreaterThan(production,c,prodArray)
            elif(production[c] == "(" and production[c+1] == "."):
                prodArray, c = self.intoStringPattern(production,c,prodArray)
            elif(production[c].isalpha()):
                prodArray, c = self.alphaNumericIterator(production,c,prodArray)
            elif(production[c] in "'\""):
                prodArray, c = self.intoQuotationsApostrophesV3(production,c,prodArray)
            else:
                c += 1
                print('else')
        production += ' '
        return prodArray, production


    def productionReplacement(self, constructedProd):
        """reamplazo de ciertos valores de la produccion que no se
        necesitan para hacer el respectivo parseo.

        Args:
            constructedProd (str): la produccion
        Returns:
            str: la produccion sin los valores obsoletos
        """
        constructedProd = constructedProd.replace(" ", "")
        constructedProd = constructedProd.replace(")", "")

        return constructedProd


    def getCompProduction(self, line, index, lastProd):
        """  
        Devuelve el valor correspondiente a la produccion en cuestion
        
        - Args:
            - line (int): line nuber
            - index (int): el index actual
            - lastProd (str): produccion anterior
        """
        newProd = ""; newProd = lastProd; cont = 0
        for i in line:
            if(int(cont) > int(index)):
                if(i.isalpha()): self.block_Prods.append(cont); newProd += i
                else: break
            cont += 1
        return newProd


    def FIRSTtoProds(self):
        """Funcion para asignar la primera pos correspondiente a cada 
        objeto que representa a la produccion en cuestion
        """
        for key in self.dictProdEnd:
            im_In_Conditional = False; addedAlready = False; definition = self.dictProdEnd[key]
            for objProdIndex in range(len(definition)):
                prod_Actual_Obj = definition[objProdIndex]
                prod_Forward_Obj = ""
                if(objProdIndex != len(definition)-1):
                    prod_Forward_Obj = definition[objProdIndex+1]
                if(prod_Actual_Obj.get_symbol_type() == "open_while_cycle" and prod_Forward_Obj.get_symbol_type() == "non_terminal"):
                    for i in self.first_Pos_Dict[prod_Forward_Obj.get_non_terminal_name()]: prod_Actual_Obj.set_add_first_pos(i)
                    break
                    
                elif(prod_Actual_Obj.get_symbol_type() == "open_conditional_or_id" and prod_Forward_Obj.get_symbol_type() == "non_terminal"):
                    for i in self.first_Pos_Dict[prod_Forward_Obj.get_non_terminal_name()]: prod_Actual_Obj.set_add_first_pos(i)
                elif(prod_Actual_Obj.get_symbol_type() == "open_while_cycle" and prod_Forward_Obj.get_symbol_type() == "open_conditional_or_id"):
                    
                    for i in range(objProdIndex+1, len(definition)):
                        if(im_In_Conditional and addedAlready == False):
                            if(definition[i].get_symbol_type() == "_terminal" or definition[i].get_symbol_type() == "non_terminal"):
                                addedAlready == True
                                if(definition[i].get_symbol_type() == "_terminal"):
                                    deff = definition[i].get_first_pos()
                                    for defiPos in deff: prod_Actual_Obj.set_add_first_pos(defiPos)
                        elif(definition[i].get_symbol_type() == "open_conditional_or_id"): im_In_Conditional = True
                elif(prod_Actual_Obj.get_symbol_type() == "open_conditional_or_id" and prod_Forward_Obj.get_symbol_type() == "_terminal"):
                    for i in prod_Forward_Obj.get_first_pos(): prod_Actual_Obj.set_add_first_pos(i)
                    
                elif(prod_Actual_Obj.get_symbol_type() == "open_bracket" and prod_Forward_Obj.get_symbol_type() == "_terminal"):
                    for i in prod_Forward_Obj.get_first_pos(): prod_Actual_Obj.set_add_first_pos(i)
                    


    def prodsBuilding(self):
        """ Construccion de la representacion
        de producciones en el archivo leido en
         cuestion
        """
        local_Dict_Productions = self.productionsInFileStr
        print("")
        print("")
        print(local_Dict_Productions)

        for keyy in local_Dict_Productions:
            definit = local_Dict_Productions[keyy]; final_prod = []; arrayProdTemp = []
            has_paramss, is_syntax_v1, is_only_one_token = False,False,False
            is_syntax, token, prod_params, string_construction = "","","",""

            self.block_Prods = []
            if(">" in keyy and "<" in keyy ):
                indexkeyyMenor = keyy.find("<")
                indexkeyyMayor = keyy.find(">")
                empty_key = keyy[0:indexkeyyMenor]
                parameters = keyy[indexkeyyMenor+1:indexkeyyMayor]
                new_var_type = ProductionInplicitData(SymbolType.production_name) 
                new_var_type.set_non_terminal_name(empty_key) 
                new_var_type.set_params(parameters) 
                new_var_type.set_is_function()
                arrayProdTemp.append(new_var_type)
            else:
                new_var_type = ProductionInplicitData(SymbolType.production_name); new_var_type.set_non_terminal_name(keyy); new_var_type.set_is_function()
                arrayProdTemp.append(new_var_type)
            for index in range(len(definit)-1):
                if(index not in self.block_Prods):
                    string_construction += definit[index]
                    actual_prod = definit[index]
                    forward_production = definit[index+1]
                    if(actual_prod == "(" and forward_production == "."):
                        self.block_Prods.append(index)
                        self.block_Prods.append(index+1)
                        is_syntax_v1 = True
                    elif(actual_prod == "." and forward_production == ")"):
                        self.block_Prods.append(index)
                        self.block_Prods.append(index+1)
                        new_var_type = ProductionInplicitData(SymbolType._action); new_var_type.set_action(is_syntax)
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(is_syntax)
                        is_syntax,string_construction = "",""
                        is_syntax_v1 = False
                    elif(is_syntax_v1):
                        is_syntax += definit[index]
                    elif(actual_prod == "(" and forward_production == "&"):
                        self.block_Prods.append(index)
                        self.block_Prods.append(index+1)
                        new_var_type = ProductionInplicitData(SymbolType.open_conditional_or_id); new_var_type.set_terminal_name("(&")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append("(&")
                        string_construction = ""
                    elif(actual_prod == "&" and forward_production == ")"):
                        self.block_Prods.append(index)
                        self.block_Prods.append(index+1)
                        new_var_type = ProductionInplicitData(SymbolType.closure_conditional_or_id)
                        new_var_type.set_terminal_name("&)")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append("&)")
                        string_construction = ""
                    elif(actual_prod in "'\""):
                        string_construction = ""
                        if(is_only_one_token == False):
                            is_only_one_token = True
                        else:
                            if(token in self.tokensArray):
                                numToken = self.tokensArray.index(token) + 1
                            else:
                                self.tokensArray.append(token)
                                numToken = len(self.tokensArray)
                            new_var_type = ProductionInplicitData(SymbolType._terminal)
                            new_var_type.set_terminal_name(token); new_var_type.set_add_first_pos(token); new_var_type.set_token_order(numToken)
                            arrayProdTemp.append(new_var_type)
                            token = ""
                            is_only_one_token = False
                    elif(is_only_one_token):
                        token += definit[index]
                    elif(has_paramss == True and actual_prod == ">"):
                        new_var_type.set_params(prod_params)
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(prod_params)
                        has_paramss = False
                        string_construction, prod_params = "",""
                    elif(has_paramss):
                        if(actual_prod != ">" and actual_prod != "<"):
                            prod_params += definit[index]
                    elif(self.productionReplacement(string_construction) in self.cCharact and not(forward_production.isalpha())):
                        acumNuevo = self.productionReplacement(string_construction)
                        if(acumNuevo in self.tokensArray):
                                numToken = self.tokensArray.index(acumNuevo) + 1
                        else:
                            self.tokensArray.append(acumNuevo)
                            numToken = len(self.tokensArray)
                        new_var_type = ProductionInplicitData(SymbolType._terminal)
                        new_var_type.set_terminal_name(acumNuevo)
                        new_var_type.set_add_first_pos(acumNuevo)
                        new_var_type.set_token_order(numToken)
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(acumNuevo)
                        string_construction = ""
                    elif(self.productionReplacement(string_construction) in self.productions and not(forward_production.isalpha())):
                        acumNuevo = self.productionReplacement(string_construction)
                        new_var_type = ProductionInplicitData(SymbolType.non_terminal)
                        new_var_type.set_non_terminal_name(acumNuevo)
                        new_var_type.set_is_function()
                        if(forward_production == "]"):
                            if(acumNuevo in self.tokensArray):
                                numToken = self.tokensArray.index(acumNuevo) + 1
                            else:
                                self.tokensArray.append(acumNuevo)
                                numToken = len(self.tokensArray)
                            new_var_type.set_add_first_pos(acumNuevo); new_var_type.set_token_order(numToken)
                        if(forward_production == "<"):
                            has_paramss = True
                        else:
                            arrayProdTemp.append(new_var_type)
                        final_prod.append(acumNuevo)
                        string_construction = ""
                    elif(self.productionReplacement(string_construction) in self.productions):
                        production = self.getCompProduction(definit, index, string_construction) 
                        production = self.productionReplacement(production)
                        new_var_type = ProductionInplicitData(SymbolType.non_terminal) 
                        new_var_type.set_non_terminal_name(production) 
                        new_var_type.set_is_function()
                        indexProd = definit.find(production)
                        acum = ""
                        contLocal = 0
                        boolLocal = False
                        definicionLocal = definit[indexProd:len(definit)]
                        for i in definicionLocal:
                            acum += i
                            contLocal += 1
                            if(acum == production):
                                if(definicionLocal[contLocal] == "<"):
                                    has_paramss = True
                                    boolLocal = True
                        if(boolLocal == False):
                            arrayProdTemp.append(new_var_type)
                        final_prod.append(production)
                        string_construction = ""
                    elif(self.productionReplacement(string_construction) in self.tokensArray and not(forward_production.isalpha())):
                        string_constructionNuevo = self.productionReplacement(string_construction)
                        if(string_constructionNuevo in self.tokensArray):
                            numToken = self.tokensArray.index(string_constructionNuevo) + 1
                        else:
                            self.tokensArray.append(string_constructionNuevo)
                            numToken = len(self.tokensArray)
                        if(string_constructionNuevo=="}"):
                            new_var_type = ProductionInplicitData(SymbolType.closure_while_cycle); new_var_type.set_terminal_name("}")
                            arrayProdTemp.append(new_var_type)
                            final_prod.append(string_constructionNuevo)
                            string_construction = ""
                        elif(string_constructionNuevo=="{"  and forward_production=='"'):
                            new_var_type = ProductionInplicitData(SymbolType.open_while_cycle); new_var_type.set_terminal_name("{")
                            arrayProdTemp.append(new_var_type)
                            final_prod.append(string_constructionNuevo)
                            string_construction = ""
                        else:
                            new_var_type = ProductionInplicitData(SymbolType._terminal); new_var_type.set_terminal_name(string_constructionNuevo)
                            new_var_type.set_add_first_pos(string_constructionNuevo); new_var_type.set_token_order(numToken)
                            arrayProdTemp.append(new_var_type)
                            final_prod.append(string_constructionNuevo)
                            string_construction = ""
                    elif(actual_prod == "{"):
                        new_var_type = ProductionInplicitData(SymbolType.open_while_cycle); new_var_type.set_terminal_name("{")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(actual_prod)
                        string_construction = ""
                    elif(actual_prod == "}"):
                        new_var_type = ProductionInplicitData(SymbolType.closure_while_cycle); new_var_type.set_terminal_name("}")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(actual_prod)
                        string_construction = ""
                    elif(actual_prod == "["):
                        new_var_type = ProductionInplicitData(SymbolType.open_bracket);new_var_type.set_terminal_name("[")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(actual_prod)
                        string_construction = ""
                    elif(actual_prod == "]"):
                        new_var_type = ProductionInplicitData(SymbolType.closure_bracket)
                        new_var_type.set_terminal_name("]")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(actual_prod)
                        string_construction = ""
                    elif(actual_prod == "|"):
                        new_var_type = ProductionInplicitData(SymbolType._or); new_var_type.set_terminal_name("|")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(actual_prod)
                        string_construction = ""
                    elif(actual_prod == "$"):
                        new_var_type = ProductionInplicitData(SymbolType._append); new_var_type.set_terminal_name("$")
                        arrayProdTemp.append(new_var_type)
                        final_prod.append(actual_prod)
                        string_construction = ""
            newArrayProduction = []
            for objIndex in range(len(arrayProdTemp)):
                productionActual = arrayProdTemp[objIndex]
                if(objIndex == len(arrayProdTemp)-1):
                    nextProduction = arrayProdTemp[objIndex]
                else:
                    nextProduction = arrayProdTemp[objIndex+1]
                newArrayProduction.append(productionActual)
                if(not isinstance(nextProduction, str)):
                    if((nextProduction.get_symbol_type() == "_action" or nextProduction.get_symbol_type() == "_terminal" or nextProduction.get_symbol_type() == "non_terminal") and productionActual.get_symbol_type() != "OR" and productionActual.get_symbol_type() != "open_conditional_or_id" and productionActual.get_symbol_type() != "open_bracket" and productionActual.get_symbol_type() != "open_while_cycle" and productionActual.get_symbol_type() != "production_name" and objIndex != len(arrayProdTemp)-1):
                        tipoCharProd = ProductionInplicitData(SymbolType._append)
                        tipoCharProd.set_terminal_name("$")
                        newArrayProduction.append(tipoCharProd)
            
            self.dictProdEnd[keyy] = newArrayProduction
            keyLocal = keyy.replace(" ", "")
            if("<" in keyy and ">" in keyy):
                keyLocal = keyy[0:keyy.find("<")].replace(" ", "")
            self.dictProdEnd2[keyLocal] = newArrayProduction
    
    
    def prodsFIRST(self):
        """Calculo de la funcion FirstPost para
        cada una de las producciones en cuestion.
        """
        for x in reversed(self.productions):
            is_conditional_prod = False; noTerminalBool = False; terminalBool = False
            for index in range(len(self.dictProdEnd2[x])):
                keyy = self.dictProdEnd2[x][index]; prod_Temp_Arr = []
                # Si el simbolo o token en cuestion 
                # es un no terminal, entonces significa 
                # primera pos en primera instancia 
                # se agrega keyy del simbolo no terminal 
                if keyy.get_symbol_type() == "non_terminal": self.first_Pos_Dict[x] = self.first_Pos_Dict[keyy.get_non_terminal_name()]; break
                elif keyy.get_symbol_type() == "_terminal":
                    # prod_Temp_Arr contiene la keyy del simbolo no terminal
                    prod_Temp_Arr.append(keyy.get_terminal_name()); self.first_Pos_Dict[x] = prod_Temp_Arr
                    # se agrega el diccionario de first pos a prod_Temp_Arr
                    for i in range(index+1, len(self.dictProdEnd2[x])):
                        # El aposicion 2 contiene las ultimas producciones
                        index_2 = self.dictProdEnd2[x][i]
                        if(is_conditional_prod and index_2.get_symbol_type() != "closure_conditional_or_id"):
                            # Si en dado caso fuera un parentesis de cerraadura para un condicional
                            if(index_2.get_symbol_type() == "non_terminal" and noTerminalBool == False):
                                noTerminalBool = True
                                for firsttPos in self.first_Pos_Dict[index_2.get_non_terminal_name()]: prod_Temp_Arr.append(firsttPos); self.first_Pos_Dict[x] = prod_Temp_Arr
                            if(index_2.get_symbol_type() == "_terminal" and terminalBool == False): terminalBool = True; prod_Temp_Arr.append(index_2.get_terminal_name()); self.first_Pos_Dict[x] = prod_Temp_Arr
                        # sino entonces es un parentesis de cerradura para un condicional
                        elif(index_2.get_symbol_type() == "open_conditional_or_id"): is_conditional_prod = True
                        elif(index_2.get_symbol_type() == "closure_conditional_or_id"): is_conditional_prod = False
                    break
        for keyy,item in self.first_Pos_Dict.items():
            print('NAME: '+ str(keyy))
            print('FIRST:')
            for i in item:
                print('\t'+str(i))


    def variableParser(self,filee,tabs=1,enter_necesary=True):
        """Funcion para construccion de la parte variable del parser.

        Args:
            f (file): el archivo en el cual se escribe
            tabs (int, optional): tab size for each circunstance. Defaults to 1.
            enter_necesary (bool, optional): [description]. Defaults to True.
        """
        m=[]
        for keyy, prodd in self.dictProdEnd.items():
            filee.write('\n')
            m.append(keyy)
            print(keyy)
            instPos = ProductionPostfix(); postfix = instPos.infix_to_postfix_prods(prodd)
            has_paramss = False; prev_prod = False
            for x in postfix:
                if(x.get_symbol_type() == "production_name"):
                    prev_prod = False
                    if(x.get_params() == ""):
                        current_non_terminal_name = x.get_non_terminal_name()
                        filee.write(" "*self.tabulation*4 + 'def ' + current_non_terminal_name + '(self):')
                    else:
                        first_pos_length = len(x.get_params()); has_paramss = True
                        filee.write(" "*self.tabulation*4 + 'def ' + x.get_non_terminal_name() + '(self, ' + x.get_params()[3:first_pos_length] + '):')
                    filee.write('\n')
                    self.tabulation += 1
                elif(x.get_symbol_type() == "_terminal"):
                    posToken = self.tokensArray.index( x.get_terminal_name()) + 1; prev_prod = False
                    filee.write(" "*self.tabulation*4 + 'self.Expectation(' + str(posToken) + ')')
                    filee.write('\n')
                elif(x.get_symbol_type() == "non_terminal"):
                    prev_prod = False; params = ""
                    if(x.get_params() != ""):
                        first_pos_length = len(x.get_params())
                        params = x.get_params()[3:first_pos_length]
                        filee.write(" "*self.tabulation*4 + params + ' = self.' + x.get_non_terminal_name()+'(' + params + ')')
                    else: filee.write(" "*self.tabulation*4 + 'self.' + x.get_non_terminal_name()+'()')
                    filee.write('\n')
                elif(x.get_symbol_type() == "closure_while_cycle"):
                    prev_prod = False; self.tabulation -= 1; filee.write('\n')
                elif(x.get_symbol_type() == "open_while_cycle"):
                    count, conta, sintaxis, prev_prod = 0, 0, "", False
                    first_pos_length = len(x.get_first_pos())
                    sintaxis = self.gettingFIRST(count,conta,first_pos_length,sintaxis,x,postfix)
                    filee.write(" "*self.tabulation*4 + 'while ' + sintaxis + ':')
                    self.tabulation += 1
                    filee.write('\n')
                elif(x.get_symbol_type() == "closure_conditional_or_id"):
                    prev_prod = True
                    self.tabulation -= 1
                    filee.write('\n')
                elif(x.get_symbol_type() == "open_conditional_or_id"):
                    count, conta, sintaxis = 0, 0, ""
                    first_pos_length = len(x.get_first_pos())
                    sintaxis = self.gettingFIRST(count,conta,first_pos_length,sintaxis,x,postfix)
                    condition = "if"
                    if(prev_prod): condition = "elif"
                    filee.write(" "*self.tabulation*4 + condition + '(' + sintaxis + '):')
                    self.tabulation += 1
                    filee.write('\n')
                elif(x.get_symbol_type() == "_action"):
                    prev_prod = False
                    filee.write(" "*self.tabulation*4 + x.get_action())
                    filee.write('\n')
                elif(x.get_symbol_type() == "closure_bracket"):
                    prev_prod = False; self.tabulation -= 1; filee.write('\n')
                elif(x.get_symbol_type() == "open_bracket"):
                    count,conta, sintaxis, prev_prod = 0, 0, "", False
                    first_pos_length = len(x.get_first_pos())
                    sintaxis = self.gettingFIRST(count,conta,first_pos_length,sintaxis,x,postfix)
                    filee.write(" "*self.tabulation*4 + 'if(' + sintaxis + '):')
                    self.tabulation += 1
                    filee.write('\n')
            if(has_paramss):
                filee.write(" "*self.tabulation*4 + "return result")
                filee.write('\n')
            self.tabulation -= 1
        filee.write('\n')
        filee.write(" "*self.tabulation*4 + 'def Main(self):''\n')
        self.tabulation += 1
        filee.write(" "*self.tabulation*4 + 'self.GetBrandNewToken()''\n')
        filee.write(" "*self.tabulation*4 + "# call to first gramatic's symbol"'\n')
        filee.write(" "*self.tabulation*4 + 'self.'+ m[0] +'()')
        self.tabulation -= 1
        filee.write('\n')

    
    def gettingFIRST(self,count,conta,first_pos_length,sintaxis,x,postfix):
        if(x.get_first_pos()== []):
            y = postfix[postfix.index(x)+1]
            for tok in y.get_first_pos():
                x.set_add_first_pos(tok)
        for w in x.get_first_pos():
            count += 1 
            posToken = self.tokensArray.index(w) + 1; sintaxis += "self.forward_token.getNum() == " + str(posToken)
            if(count < first_pos_length): sintaxis += " or "
        return sintaxis

    def parserConstructor(self):
        file_current = open("Cocor/archivosGenerados/ParserScanner/Parser.py", "w", encoding="utf8")
        file_current.write('''

import os
from os.path import basename
import sys
sys.path.append(".")
import pickle
from menu.Menu import *


class Parser():

    def __init__(self) -> None:
        self.scanner_tokens = ""; self.dict_enum_tokens = ""
        self.ultimate_token = ""; self.forward_token = ""
        self.scanner_tokens_var1 = []


    def Expectation(self, token_id):
        if self.forward_token.getNum() == token_id: self.GetBrandNewToken() 
        else: self.errorHandlerAdvise(token_id)


    def GetBrandNewToken(self):
        self.ultimate_token = self.forward_token
        if len(self.scanner_tokens_var1) > 0: self.forward_token = self.scanner_tokens_var1.pop(0)
        else: self.forward_token = self.forward_token


    def readDumpStates(self):
        self.scanner_tokens = pickle.load(open("Cocor/archivosGenerados/tokensInFile",'rb'))
        self.dict_enum_tokens = pickle.load(open("Cocor/archivosGenerados/dictEnumTokens",'rb'))
        for llave, valor in self.dict_enum_tokens.items():
            for x in self.scanner_tokens:
                valoresToken = x.get_token_info()
                if(llave == valoresToken[0]): x.set_num(valor)
                elif(valoresToken[0] == "__error__" and (valoresToken[1] == llave)): x.set_num(valor)
        for x in range(len(self.scanner_tokens)): 
            if(self.scanner_tokens[x].getNum() != ""): self.scanner_tokens_var1.append(self.scanner_tokens[x])
        print()


    def getNumber(self):
        if(self.forward_token.get_value() != "+" and self.forward_token.get_value() != "-" and self.forward_token.get_value() != "*" and self.forward_token.get_value() != "/" and self.forward_token.get_value() != ";"):
            return int(self.ultimate_token.get_value())
        else:
            return self.ultimate_token.get_value()


    def getVar(self):
        return self.forward_token.get_value()

        ''')
        self.variableParser(file_current)
        file_current.write('''


    def errorHandlerAdvise(self, token_id):
        for x in self.scanner_tokens_var1:
            if(x.getNum() == token_id):
                if(x.get_token_type() == "__error__"): 
                    error_print = x.get_value(); print('expected:  '+error_print)
                elif(x.get_token_type() != "__error__"): 
                    error_print = x.get_token_type(); print('expected:  '+error_print)


# tests__________
if __name__ == "__main__":
    mainParser()
        ''')


# ZONA DE FUNCIONES PARA RECORRER EXPRESIONES REGULARES DE COCO/R -----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
    def intoBraces(self,tokens_exp,c,expArray):
        """Recorre los contenidos dentro de { } y retorna el valor de conversion ()*. 
        Puede tener recursion pero se asume que no habran mas {} dentro de la expresion.

        Args:
            tokens_exp (str): cadena con tokens
            c (int): contador externo
            expArray (list): lista con todos los tokens encontrados en tokens_exp

        Returns:
            list: expArray actualizado
            int: el contador actualizado
        """
        word_set = ['(']
        c += 1
        currentChar = (tokens_exp[c])
        while (c < len(tokens_exp) and (tokens_exp[c].isalpha() or tokens_exp[c] in "|}{'\"") ):
            if tokens_exp[c] == '}':
                word_set.append(')*')
                c += 1
                expArray.append(''.join(word_set))
                break
            elif tokens_exp[c] == '{':
                expArray, c = self.intoBraces(tokens_exp,c,expArray)
            else:
                word_set.append(tokens_exp[c])
                c += 1
        return expArray,c


    def intoBrackets(self,tokens_exp,c,expArray):
        """Recorre los contenidos dentro de [ ] y retorna el valor. 
        Hay recursion ya que pueden haber mas [ ] dentro.
        Args:
            tokens_exp (str): cadena con tokens
            c (int): contador externo
            expArray (list): lista con todos los tokens encontrados en tokens_exp
        Returns:
            list: expArray actualizado
            int: el contador actualizado
        """
        word_set = ['(']
        expArray.append('(')
        c += 1
        currentChar = (tokens_exp[c])
        while (c < len(tokens_exp) and (tokens_exp[c].isalpha() or tokens_exp[c] in "|][}{'\"") ):
            currentChar = (tokens_exp[c])
            if tokens_exp[c] == ']':
                word_set.append(')|ε')
                openp = 0
                closep = 0
                for b in expArray:
                    if(')|ε' in b):
                        closep +=1
                    elif(b == '('):
                        openp += 1

                if(''.join(word_set) == "()|ε" and (closep != openp-1)):
                    exp = expArray.pop()
                    exp = exp + ')|ε'
                    expArray.append(exp)
                elif(''.join(word_set) == "()|ε" and (closep == openp-1)):
                    expArray.append(')|ε')
                else: 
                    expArray.append(''.join(word_set))
                c += 1
                break
            elif tokens_exp[c] == '[':
                expArray, c = self.intoBrackets(tokens_exp,c,expArray)
            elif tokens_exp[c] == '{':
                expArray, c = self.intoBraces(tokens_exp,c,expArray)
            elif tokens_exp[c] in "'\"":
                expArray, c = self.intoQuotationsApostrophes(tokens_exp,c,expArray)
            elif tokens_exp[c].isalpha():
                expArray, c = self.alphaNumericIterator(tokens_exp,c,expArray)
            else:
                word_set.append(tokens_exp[c])
                c += 1
        return expArray,c


    def intoParenthesis(self,tokens_exp,c,expArray):
        """Recorre los contenidos dentro de ( ) y retorna el valor. 
        Hay recursion ya que pueden haber mas ( ) dentro.

        Args:
            tokens_exp (str): cadena con tokens
            c (int): contador externo
            expArray (list): lista con todos los tokens encontrados en tokens_exp

        Returns:
            list: expArray actualizado
            int: el contador actualizado
        """
        word_set = ['(']
        c += 1
        currentChar = (tokens_exp[c])
        while (c < len(tokens_exp) and (tokens_exp[c].isalpha() or tokens_exp[c] in "|)('\"") ):
            currentChar = (tokens_exp[c])
            if tokens_exp[c] == ')':
                word_set.append(tokens_exp[c])
                c += 1
                expArray.append(''.join(word_set))
                break
            elif tokens_exp[c] == '(':
                expArray, c = self.intoParenthesis(tokens_exp,c,expArray)
            else:
                word_set.append(tokens_exp[c])
                c += 1
        return expArray,c


    def intoQuotationsApostrophes(self,tokens_exp,c,expArray):
        """Recorre los contenidos dentro de ' ' o " " considerando | dentro y retorna el valor.

        Args:
            tokens_exp (str): cadena con tokens
            c (int): contador externo
            expArray (list): lista con todos los tokens encontrados en tokens_exp

        Returns:
            list: expArray actualizado
            int: el contador actualizado
        """
        if tokens_exp[c] == '"':
            q = '"'
        elif tokens_exp[c] == "'":
            q = "'"
        word_set = []
        c += 1
        word_set.append(q) #no se necesita que este la comilla o apostrofe del principio
        while c < len(tokens_exp):
            forwardOr = False
            if c+1 < (len(tokens_exp)):
                if tokens_exp[c+1] == "|":
                    forwardOr = True
            if forwardOr:
                if tokens_exp[c+2] in "'\"":
                    word_set.append(tokens_exp[c]) #se inserta el '
                    word_set.append(tokens_exp[c+1]) #se inserta el |
                    word_set.append(tokens_exp[c+2]) #se inserta el proximo '
                    c += 3
                else:
                    word_set.append(tokens_exp[c])
                    c += 1
                #continues
            elif tokens_exp[c] == q:
                #no se necesita que este la comilla o apostrofe del final
                word_set.append(tokens_exp[c]) 
                c += 1
                break
            else:
                word_set.append(tokens_exp[c])
                c += 1

        expArray.append(''.join(word_set))
        return expArray, c 


    def intoQuotationsApostrophesV2(self,tokens_exp,c,expArray):
        """Recorre los contenidos dentro de ' ' o " " sin cosidrerar | y hace operaciones con set.
        Para uso en parseo de cacacteres

        Args:
            tokens_exp (str): cadena con tokens
            c (int): contador externo
            expArray (list): lista con todos los tokens encontrados en tokens_exp

        Returns:
            list: expArray actualizado
            int: el contador actualizado
        """
        if tokens_exp[c] == '"':
            q = '"'
        elif tokens_exp[c] == "'":
            q = "'"
        word_set = []
        c += 1
        word_set.append(q) #no se necesita que este la comilla o el apostrofe dentro del string
        while c < len(tokens_exp):
            if tokens_exp[c] == q:
                word_set.append(tokens_exp[c])
                c += 1
                break
            else:
                word_set.append(tokens_exp[c])
                c += 1
        
        itemsCount = 0
        expTempArray = []
        for i in word_set:
            if i not in '\'"':
                if(itemsCount > 0):
                    expArray.append(set(map(ord,set(i))))
                    expArray.append('~')
                else:
                    expArray.append(set(map(ord,set(i))))
                    expArray.append('~')
                    expTempArray.append(set(map(ord,set(i))))
                itemsCount += 1

        if len(expTempArray) == 0:
            if(word_set.count("'") > word_set.count('"')):
                expArray.append(set(map(ord,set('"'))))
            elif(word_set.count("'") < word_set.count('"')):
                expArray.append(set(map(ord,set("'"))))
        else:
            #sacamos el ultimo operador de concatenacion que esta demas
            if(itemsCount > 0):
                expArray.pop() 
                
        return expArray, c 


    def intoQuotationsApostrophesV3(self,tokens_exp,c,expArray):
        """Recorre los contenidos dentro de ' ' o " " y retorna el valor.
        Para uso en parseo de producciones.

        Args:
            tokens_exp (str): cadena con tokens
            c (int): contador externo
            expArray (list): lista con todos los tokens encontrados en tokens_exp

        Returns:
            list: expArray actualizado
            int: el contador actualizado
        """
        if tokens_exp[c] == '"':
            q = '"'
        elif tokens_exp[c] == "'":
            q = "'"
        word_set = []
        c += 1

        while c < len(tokens_exp):
            forwardOr = False
            if c+1 < (len(tokens_exp)):
                if tokens_exp[c+1] == "|":
                    forwardOr = True
            if forwardOr:
                if tokens_exp[c+2] in "'\"":
                    word_set.append(tokens_exp[c]) #se inserta el '
                    word_set.append(tokens_exp[c+1]) #se inserta el |
                    word_set.append(tokens_exp[c+2]) #se inserta el proximo '
                    c += 3
                else:
                    word_set.append(tokens_exp[c])
                    c += 1
                #continues
            elif tokens_exp[c] == q:

                c += 1
                break
            else:
                word_set.append(tokens_exp[c])
                c += 1

        expArray.append(''.join(word_set))
        return expArray, c 


    def alphaNumericIterator(self,tokens_exp,c,expArray,considerOr=True):
        """Recorre una cadena de letras tomando en cuenta | y la retorna.

        Args:
            tokens_exp (str): cadena con tokens
            c (int): contador externo
            expArray (list): lista con todos los tokens encontrados en tokens_exp

        Returns:
            list: expArray actualizado
            int: el contador actualizado
        """
        word_set = []
        if considerOr:
            while (c < len(tokens_exp) and (tokens_exp[c].isalpha() or tokens_exp[c] == "|")):
                word_set.append(tokens_exp[c])
                c += 1
        else:
            while (c < len(tokens_exp) and tokens_exp[c].isalpha()):
                word_set.append(tokens_exp[c])
                c += 1
        word = ''.join(word_set)

        expArray.append(''.join(word_set))
        return expArray, c


    def intoLessGreaterThan(self,prod_exp,c,prodArray):
        """Recorre los contenidos dentro de < > y retorna el valor. 
        Hay recursion ya que pueden haber mas < > dentro.

        Args:
            prod_exp (str): cadena con tokens
            c (int): contador externo
            prodArray (list): lista con todos los tokens encontrados en prod_exp

        Returns:
            list: prodArray actualizado
            int: el contador actualizado
        """

        word_set = []
        c += 1
        currentChar = (prod_exp[c])
        while (c < len(prod_exp) and (prod_exp[c].isalpha() or prod_exp[c].isnumeric() or prod_exp[c] in ">< ") ):
            currentChar = (prod_exp[c])
            if prod_exp[c] == '>':

                c += 1
                prodArray.append(''.join(word_set))
                break
            else:
                word_set.append(prod_exp[c])
                c += 1
        return prodArray,c


    def intoStringPattern(self,prod_exp,c,prodArray):
        """Recorre los contenidos dentro de un patron de string como (. .) y retorna el valor. 
        Hay recursion ya que pueden haber mas (. .) dentro.

        Args:
            prod_exp (str): cadena con tokens
            c (int): contador externo
            prodArray (list): lista con todos los tokens encontrados en prod_exp

        Returns:
            list: prodArray actualizado
            int: el contador actualizado
        """
        strPatternOpen = '(.'
        strPatternClose = '.)'

        word_set = []
        c += len(strPatternOpen)
        currentChar = (prod_exp[c])
        while (c < len(prod_exp)):
            currentChar = (prod_exp[c])
            if (prod_exp[c]+prod_exp[c+1]) == strPatternClose:

                c += len(strPatternOpen)
                prodArray.append(''.join(word_set))
                break
            elif (prod_exp[c]+prod_exp[c+1]) == strPatternOpen:
                prodArray, c = self.intoStringPattern(prod_exp,c,prodArray)
            else:
                word_set.append(prod_exp[c])
                c += 1
        return prodArray,c

# ZONA DE TRATAMIENTO DE CARACTERES -----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------

    def setOperations(self,i,char_def,set1):
        chr_result_operations = [set1]
        while i < len(char_def):
            if(char_def[i] == '+'):
                set2 = char_def[i+1]
                set1_ = chr_result_operations.pop()
                snum = ''
                if('chr(' in set2.lower()):
                    for e in set2:
                        if(e.isdigit()):
                            snum += e
                    num = int(snum)
                    set2 = set(chr(num))
                    if(isinstance(set1_, str)):
                        set1_ = set(set1_)
                    if(isinstance(set2, str)):
                        set2 = set(set2)
                    if(isinstance(set1_, list)):
                        set1_ = set1_[0]
                    if(isinstance(set2, list)):
                        set2 = set2[0]
                    chr_result_operations.append(set1_.union(set2))
                else:
                    if(isinstance(set1_, str)):
                        set1_ = set(set1_)
                    if(isinstance(set2, str)):
                        set2 = set(set2)
                    if(isinstance(set1_, list)):
                        set1_ = set1_[0]
                    if(isinstance(set2, list)):
                        set2 = set2[0]
                    chr_result_operations.append(set1_.union(set2))
                i += 2
            elif(char_def[i] == '-'):
                set2 = char_def[i+1]
                set1_ = chr_result_operations.pop()
                snum = ''
                if('chr(' in set2.lower()):
                    for e in set2:
                        if(e.isdigit()):
                            snum += e
                    num = int(snum)
                    set2 = set(chr(num))
                    chr_result_operations.append(set1_.difference(set2))
                else:
                    chr_result_operations.append(set1_.difference(set2))
                i += 2
            else:
                print('no operations else!!!!!!!!!!! :O')
                i += 1
        return i, chr_result_operations


    def whenChrFound(self,char_def,i,subs_char_def):
        if('..' in char_def):
            snum = ''
            enum = ''
            for e in char_def[i]:
                if(e.isdigit()):
                    snum += e
            for e in char_def[i+2]:
                if(e.isdigit()):
                    enum += e
            start = int(snum)
            end = int(enum)
            i += 3
            chr_range = set([chr(char) for char in range(start,end)])
            if(i < len(char_def)):
                i,chr_result_operations = self.setOperations(i,char_def,chr_range)
                subs_char_def.append(chr_result_operations)
            else:
                subs_char_def.append(chr_range)

            return i, subs_char_def
        else:
            snum = ''
            for e in char_def[i]:
                if(e.isdigit()):
                    snum += e
            num = int(snum)
            i += 1
            first_char_in_expresion = [set([chr(num)])]
            if(i < len(char_def)):
                i,chr_result_operations = self.setOperations(i,char_def,first_char_in_expresion)
                subs_char_def.append(chr_result_operations) 
            else:
                subs_char_def.append(first_char_in_expresion)

            return i, subs_char_def


    def whenAoraFound(self,char_def,i,subs_char_def):
        if('..' in char_def):
            start = ord(char_def[i])
            end = ord(char_def[i+2])
            letter_range = [set([chr(char) for char in range(start,end)])]
            i += 3
            if(i < len(char_def)):
                i,chr_result_operations = self.setOperations(i,char_def,letter_range)
                subs_char_def.append(chr_result_operations)
            else:
                subs_char_def.append(letter_range)
        else:
            any_word = set(char_def[i])
            i += 1
            if(i < len(char_def)):
                i,chr_result_operations = self.setOperations(i,char_def,any_word)
                subs_char_def.append(chr_result_operations)
            else:
                subs_char_def.append([any_word])

        return i, subs_char_def


    def whenANYFound(self,char_def,i,subs_char_def):
        anyy = set([chr(char) for char in range(0,255)])
        i += 1
        if(i < len(char_def)):
            i,chr_result_operations = self.setOperations(i,char_def,anyy)
            subs_char_def.append(chr_result_operations) 
        else:
            subs_char_def.append(anyy)

        return i, subs_char_def


    def dictSubstitionItself(self,dict1):
        dict_result = {}
        for key,char_def in dict1.items():
            i = 0
            new_exp = []
            while i < len(char_def):
                value_key = char_def[i]
                substitution = self.functions.get_value_from_dict(value_key,dict1)
                if(substitution != None):
                    new_exp.append(substitution[0])
                else:
                    new_exp.append(char_def[i])
                i += 1

            dict_result[key] = new_exp
        return dict_result


    def dictSubstitionOther(self,dict1,dict2):
        dict_result = {}
        for key,char_def in dict1.items():
            i = 0
            new_exp = []
            while i < len(char_def):
                value_key = char_def[i]
                substitution = self.functions.get_value_from_dict(value_key,dict2)
                if(substitution != None):
                    new_exp.append(substitution)
                else:
                    new_exp.append(char_def[i])
                i += 1

            dict_result[key] = new_exp
        return  dict_result


    def charactersSubstitution(self):
        """funcion que sustituye caracteres
        """
        charactersInFileSubs0 = {}
        charArray = []
        # ciclo para convertir los strings en arrays que encapsulen cada operando (item) de la expresion del caracter
        for key, char_def in self.charactersInFile.items():
            new_char_def = []
            has_space_char = False

            ss = char_def.split(' ')
            for i in ss:
                if (len(i) > 0):
                    e = ''
                    if(i.count('"') == 2):
                        e = i.replace('"','')
                        new_char_def.append(e)
                    elif(i.count("'") == 2):
                        e = i.replace("'",'')
                        new_char_def.append(e)
                    else:
                        new_char_def.append(i)

            # if para espacio en blanco ' '
            if("'" in new_char_def):
                ind = new_char_def.index("'")
                if(ind+1 < len(new_char_def)):
                    obj_ind2 = new_char_def[ind+1]
                    if(obj_ind2 == "'"):
                        new_char_def.pop(ind)
                        new_char_def.pop(ind)
                        new_char_def.insert(ind,'CHR(32)')
            if key == 'operadores' or key == 'operators':
                new_char_def[0] = new_char_def[0] + '='
            charactersInFileSubs0[key] = new_char_def
            self.prodCharac(new_char_def)

        charactersInFileSubs1 = self.dictSubstitionItself(charactersInFileSubs0)

        # sustitucion de las especificaciones de la tabla ascii en el archivo

        #! CHECAR LUEGO DE HEXDIGIT!!!!
        for key,char_def in charactersInFileSubs1.items():
            subs_char_def = []
            subs_char_def2 = []

            i = 0
            while i < len(char_def):
                curr = char_def[i]
                if(char_def[i] == ' '):
                    i +=1
                    continue
                elif('chr(' in char_def[i].lower()):
                    i, subs_char_def = self.whenChrFound(char_def,i,subs_char_def)
                elif('ANY' in char_def[i]):
                    i, subs_char_def = self.whenANYFound(char_def,i,subs_char_def)
                elif('A' in char_def[i] or 'a' in char_def[i]):
                    i, subs_char_def = self.whenAoraFound(char_def,i,subs_char_def)
                else:
                    any_word = set(char_def[i])
                    i += 1
                    if(i < len(char_def)):
                        i,chr_result_operations = self.setOperations(i,char_def,any_word)
                        subs_char_def.append(chr_result_operations) 
                    else:
                        subs_char_def.append([any_word])

            self.charactersInFileSubs2[key] = set(map(ord,subs_char_def[0][0])) 


# ZONA DE TRATAMIENTO DE TOKENS -----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
    def cocorToP1Convention(self):
        """funcion para acoplar las expresiones regulares al proyecto 1 haciendo conversiones como: 
        - kleene closure
            - digit{digit} = digit digit *
            - {} = * (0 o mas)  -->  r*
        - positive closure
            - [digit] = digit? = digit|ε
            - [] = ? (cero o una instancia)  -->  r? = r|ε
        - concatenacion
            - '~' = operador explicito para concatenacion
        """
        closures = []
        expArray = []
        for key, tokens_exp in self.tokensInFile.items():
            c = 0
            while c < len(tokens_exp):
                currentChar = tokens_exp[c]
                if tokens_exp[c] == " ":
                    c += 1
                    continue
                elif(tokens_exp[c] == "{"):
                    expArray, c = self.intoBraces(tokens_exp,c,expArray)
                elif(tokens_exp[c] == "("):
                    expArray, c = self.intoParenthesis(tokens_exp,c,expArray)
                elif(tokens_exp[c] == "["):
                    expArray, c = self.intoBrackets(tokens_exp,c,expArray)
                elif(tokens_exp[c].isalpha() or c == '|'):
                    expArray, c = self.alphaNumericIterator(tokens_exp,c,expArray)
                elif(tokens_exp[c] in "'\""):
                    expArray, c = self.intoQuotationsApostrophes(tokens_exp,c,expArray)
                elif(tokens_exp[c] in "})]"):
                    print('Revisar cerraduras de apertura en la expresion')
                else:
                    c += 1
                    print('else')

            finalExpArray = []
            c = 0

            if('(' in expArray):
                while (c < len(expArray)):
                    if(expArray[c] == '('):
                        exp = expArray[c] + expArray[c+1]
                        finalExpArray.append(exp)
                        c += 2
                    else:
                        finalExpArray.append(expArray[c])
                        c += 1
                finalExpString = '~'.join(finalExpArray)
                finalExpString = finalExpString.replace('~)',')')
                self.tokensConvertionInFile[key] = finalExpString
            else:
                expString = '~'.join(expArray)
                expString = expString.replace('~)',')')
                self.tokensConvertionInFile[key] = expString
            expArray = []

    def tokensPreparationPostfix(self):
        """funcion que prepara las expresiones para ser convertidas a formato postfix ya que estan en infix
        """
        expOpArray = []
        except_arr = []
        for key, tokens_exp in self.tokensConvertionInFile.items():
            c = 0
            if ('EXCEPT' in tokens_exp or 'KEYWORDS' in tokens_exp):
                except_arr.append('EXCEPT KEYWORDS')
                numToRemove = (len('EXCEPT')+len('KEYWORDS')+2)
                numCharacters = len(tokens_exp)-numToRemove
                tokens_exp_new = tokens_exp[:numCharacters]
            else:
                tokens_exp_new = tokens_exp

            while c < len(tokens_exp_new):
                currentChar = tokens_exp_new[c]
                if tokens_exp_new[c] == " ":
                    c += 1
                    continue
                elif(tokens_exp_new[c] in "~*|)("):
                    expOpArray.append(tokens_exp_new[c])
                    c += 1
                elif(tokens_exp_new[c].isalpha()):
                    expOpArray, c = self.alphaNumericIterator(tokens_exp_new,c,expOpArray,False)
                elif(tokens_exp_new[c] in "'\""):
                    expOpArray, c = self.intoQuotationsApostrophesV2(tokens_exp_new,c,expOpArray)
                else:
                    print(tokens_exp_new[c])

            if(len(except_arr) == 0):
                self.tokensReadyForPosFix[key] = expOpArray
                self.tokensArray.append(key)
            else:
                self.tokensReadyForPosFix[key] = expOpArray
                self.tokensArray.append(key)
            expOpArray = []
            except_arr = []


    def orBetweenExpresions(self):
        exp_final = []
        for key, exp in self.tokensReadyForPosFix.items():
            exp.insert(0,'(')
            exp += ['~','#',')']
            exp.append('|')
            exp_final += exp

        #Eliminamos el ultimo or | que no se necesita
        exp_final.pop() 


        exp_final_dict = {}
        exp_final_dict['exp'] = exp_final

        for key, exp in exp_final_dict.items():
            self.finalExpression[key] =  self.objToPostfix.infix_to_postfix(exp)


    def expresionSubstitutions(self):
        """Expresion final postfix con sustituciones aplicadas
        """
        dict1 = self.finalExpression
        dict2 = self.charactersInFileSubs2
        self.tokensSubstitutionExp = self.dictSubstitionOther(dict1,dict2)

        result = self.tokensSubstitutionExp['exp']
        return result


    def tokensSubstitutions(self):
        """Visualizar todas las expresiones infix sustituidas. 
            Funciona bien sin correr orBeetweenExpressions antes
        """
        dict1 = self.tokensReadyForPosFix
        dict2 = self.charactersInFileSubs2
        self.tokensSubstitution = self.dictSubstitionOther(dict1,dict2)