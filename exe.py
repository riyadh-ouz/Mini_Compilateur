from syn_sem import _type
from syn_sem import table_symboles

from syn_sem import ErreurSemantique

# ==============================================================================================
# Utilités
def taille_tableau(idn): # Retourne la taille s'il sagit d'un tableau, None sinon
    if type(table_symboles[idn][0]) == tuple: return table_symboles[idn][0][1]
    return None

# ==============================================================================================
def executer(arbre, _in=input, _out=print):

    # Un bloque d'instructions
    if arbre.racine == 'main' or arbre.racine == 'bloque':
        for instr in arbre.fils:
            executer(instr, _in, _out)

    # Une affectation
    if arbre.racine == '=':
        var = arbre.fils[0]
        idn = var.racine
        taille = taille_tableau(idn)
        if taille: # Vérifier s'il s'agit d'un élément d'un tableau
            indice = eval_exp(var.fils[0]) # Calculer son indice, can raise an IndexError
            table_symboles[idn][1][indice] = eval_exp(arbre.fils[1]) # can raise an IndexError
        else: table_symboles[idn][1] = eval_exp(arbre.fils[1])

    # Une lecture
    if arbre.racine == 'lire':
        var = arbre.fils[0]
        tmp = _in()
        if _type(var) == 'entier': tmp = int(tmp) # can raise a ValueError

        idn = var.racine
        taille = taille_tableau(idn)
        if taille:
            indice = eval_exp(var.fils[0])  # can raise an IndexError
            table_symboles[idn][1][indice] = tmp # can raise an IndexError
        else: table_symboles[idn][1] = tmp

    # Un affichage
    if arbre.racine == 'afficher': _out(str(eval_exp(arbre.fils[0])))

    # Les instructions de branchement
    if arbre.racine == 'si':
        if eval_condition(arbre.fils[0]): executer(arbre.fils[1], _in, _out)
    if arbre.racine == 'si-sinon':
        if eval_condition(arbre.fils[0]): executer(arbre.fils[1], _in, _out)
        else: executer(arbre.fils[2], _in, _out)
    if arbre.racine == 'tq':
        while eval_condition(arbre.fils[0]): executer(arbre.fils[1], _in, _out)

# ==============================================================================================
def eval_exp(exp):
    
    if type(exp.racine) == int: return exp.racine
    
    if exp.racine == '+':
        if len(exp.fils) == 2: return eval_exp(exp.fils[0]) + eval_exp(exp.fils[1])
        else: return eval_exp(exp.fils[0])

    if exp.racine == '-':
        if len(exp.fils) == 2: return eval_exp(exp.fils[0]) - eval_exp(exp.fils[1])
        else: return - eval_exp(exp.fils[0])

    if exp.racine == '*': return eval_exp(exp.fils[0]) * eval_exp(exp.fils[1])
    if exp.racine == '/': return eval_exp(exp.fils[0]) // eval_exp(exp.fils[1])

    if exp.racine in table_symboles: # une variable
        idn = exp.racine
        taille = taille_tableau(idn)
        if taille:
            indice = eval_exp(exp.fils[0]) # can raise an IndexError
            if table_symboles[idn][1][indice] == None: # can raise an IndexError
                raise ErreurSemantique("'%s' est non initialisé" % idn)
            return table_symboles[idn][1][indice]
        if table_symboles[idn][1] == None: raise ErreurSemantique("'%s' est non initialisé" % idn)
        return table_symboles[idn][1]

    else: return exp.racine[1: -1] # une chaine de caractères

# ==============================================================================================
def eval_condition(cond):
    if cond.racine == 'ou': return eval_condition(cond.fils[0]) or eval_condition(cond.fils[1])
    if cond.racine == 'et': return eval_condition(cond.fils[0]) and eval_condition(cond.fils[1])
    if cond.racine == 'non': return not eval_condition(cond.fils[0])
    if cond.racine == '<': return eval_exp(cond.fils[0]) < eval_exp(cond.fils[1])
    if cond.racine == '<=': return eval_exp(cond.fils[0]) <= eval_exp(cond.fils[1])
    if cond.racine == '>': return eval_exp(cond.fils[0]) > eval_exp(cond.fils[1])
    if cond.racine == '>=': return eval_exp(cond.fils[0]) >= eval_exp(cond.fils[1])
    if cond.racine == '==': return eval_exp(cond.fils[0]) == eval_exp(cond.fils[1])
    if cond.racine == '!=': return eval_exp(cond.fils[0]) != eval_exp(cond.fils[1])
# ==============================================================================================