# Analyse Syntaxique-Sémantique

from ply import yacc
import lex


# Récupérer les lexèmes de l'analyse lexicale
tokens = lex.tokens

# Initialiser la table des symboles (un dictionnaire type:valeur)
table_symboles = {}

# ==============================================================================================
# Utilités pour la gestion des erreurs sémantiques

def est_declaree(idn): # Vérifier si un identificateur est déclaré
    return idn in table_symboles

def _type(exp): # Retourner le type d'une expression
    if type(exp._type) == tuple: return exp._type[0]
    return exp._type

class ErreurSemantique(Exception):
    def __init__(self, msg):
        self.msg = msg

# ==============================================================================================
# La structure d'arbre abstrait
class Noeud:
    def __init__(self, racine, fils=None, _type=None):
        self.racine = racine
        self._type = _type
        if fils: self.fils = fils
        else: self.fils = []

    def visualiser(self):
        tmp = []
        for f in self.fils: tmp.append(f.racine)
        print(self.racine, ' -> ', tmp)
        for f in self.fils: f.visualiser()

# ==============================================================================================
# La grammaire

def p_main(p):
    'main : MAIN COLN liste_decl DEBUT liste_instr FIN'
    p[0] = Noeud('main', p[5]) # p[5] est la liste des instructions

def p_liste_decl(p):
    '''liste_decl : decl SEMI liste_decl
    | vide'''

def p_decl(p):
    'decl : IDN COLN type'
    if type(p[3]) == tuple:
        taille = p[3][1]
        table_symboles[p[1]] = [p[3], [None] * taille]
    else: table_symboles[p[1]] = [p[3], None]

def p_type(p):
    '''type : T_CHAINE
    | T_ENTIER
    | T_CHAINE LBRACKT NUM RBRACKT
    | T_ENTIER LBRACKT NUM RBRACKT'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = (p[1], p[3]) # Le type est un tuple s'il sagit d'un tableau

def p_liste_instr(p):
    '''liste_instr : instr liste_instr
    | vide'''
    if len(p) == 3: p[0] = [p[1]] + p[2]
    elif len(p) == 2: p[0] = []

def p_instr(p):
    '''instr : aff
    | lire
    | afficher
    | si
    | tq'''
    p[0] = p[1]


# Affectation, Lecture & Affichage

def p_var(p):
    '''var : IDN LBRACKT exp RBRACKT
    | IDN'''
    if not est_declaree(p[1]):
        raise ErreurSemantique("'%s' n'est pas déclaré --> Ligne: %s" % (p[1].value, p.lineno(1)))
    if len(p) == 2: p[0] = Noeud(p[1], None, table_symboles[p[1]][0])
    else: p[0]= Noeud(p[1], [p[3]], table_symboles[p[1]][0])

def p_aff(p):
    'aff : var ASSIGN exp SEMI'    
    if _type(p[1]) != _type(p[3]):
        raise ErreurSemantique("affectation de types incompatibles --> Ligne: %s" % p.lineno(1))
    p[0] = Noeud('=', [p[1], p[3]])

def p_lire(p):
    'lire : LIRE LPAREN var RPAREN SEMI'
    p[0] = Noeud('lire', [p[3]])

def p_afficher(p):
    'afficher : AFFICHER LPAREN exp RPAREN SEMI'
    p[0] = Noeud('afficher', [p[3]])


# Les instructions de branchement

def p_si(p):
    'si : SI LPAREN condition RPAREN COLN liste_instr FSI SEMI sinon'
    p[6] = Noeud('bloque', p[6])
    if p[9]: p[0] = Noeud('si-sinon', [p[3], p[6], p[9]])
    else: p[0] = Noeud('si', [p[3], p[6]])

def p_sinon(p):
    '''sinon : SINON COLN liste_instr FSINON SEMI
    | vide'''
    if len(p) == 6: p[0] = Noeud('bloque', p[3])

def p_tq(p):
    'tq : TQ LPAREN condition RPAREN COLN liste_instr FTQ SEMI'
    p[6] = Noeud('bloque', p[6])
    p[0] = Noeud('tq', [p[3], p[6]])


# Les expressions arithmétiques

precedence = (
    ('left', 'OU'),
    ('left', 'ET'),
    ('right', 'NON'),
    
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS', 'UPLUS')
)

def p_exp_binaire(p):
    '''exp : exp PLUS exp
    | exp MINUS exp
    | exp TIMES exp
    | exp DIVIDE exp'''
    if _type(p[1]) != 'entier' or _type(p[3]) != 'entier':
        raise ErreurSemantique("types incompatibles --> Ligne: %s" % p.lineno(2))
    p[0] = Noeud(p[2], [p[1], p[3]], 'entier')

def p_exp_unaire(p):
    '''exp : MINUS exp %prec UMINUS
    | PLUS exp %prec UPLUS'''
    if _type(p[2]) != 'entier':
        raise ErreurSemantique("types incompatibles --> Ligne: %s" % p.lineno(1))
    p[0] = Noeud(p[1], [p[2]], 'entier')

def p_exp_paren(p):
    "exp : LPAREN exp RPAREN"
    p[0] = p[2]

def p_exp_num(p):
    'exp : NUM'
    p[0] = Noeud(p[1], None, 'entier')

def p_exp_var(p):
    'exp : var'
    p[0] = p[1]

def p_exp_string(p):
    'exp : STRING'
    p[0] = Noeud(p[1], None, 'chaine')


# Les conditions (expressions logiques)

def p_condition_logique(p):
    '''condition : condition OU condition
    | condition ET condition'''
    p[0] = Noeud(p[2], [p[1], p[3]], 'booleen')

def p_condition_non(p):
    'condition : NON condition %prec NON'
    p[0] = Noeud(p[1], [p[2]], 'booleen')

def p_condition_paren(p):
    'condition : LPAREN condition RPAREN'
    p[0] = p[2]

def p_condition_compar(p):
    '''condition : exp LT exp
    | exp LE exp
    | exp GT exp
    | exp GE exp
    | exp EQ exp
    | exp NE exp'''
    p[0] = Noeud(p[2], [p[1], p[3]], 'booleen')


# La production vide (epsilon)
def p_vide(p):
    'vide : '

# ==============================================================================================
# Gestion des erreurs syntaxiques
class ErreurSyntaxique(Exception):
    def __init__(self, msg):
        self.msg = msg

def p_error(p):
    if p:
        raise ErreurSyntaxique("'%s' --> Ligne: %s" % (p.value, p.lexer.lineno))
    else:
        raise ErreurSyntaxique("fichier vide!")

# ==============================================================================================

analyseur = yacc.yacc()

def analyser(data, debug=0):
    return analyseur.parse(data, debug=debug)
