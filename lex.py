# Analyse Lexicale

from ply import lex

mots_cles = {
    'main':'MAIN', 'debut':'DEBUT', 'fin':'FIN', 'chaine':'T_CHAINE', 'entier':'T_ENTIER',
    'lire':'LIRE', 'afficher':'AFFICHER', 'si':'SI','fsi':'FSI', 'sinon':'SINON',
    'fsinon': 'FSINON', 'tantque':'TQ', 'ftq':'FTQ', 'ou': 'OU', 'et': 'ET',
    'non': 'NON'
}

tokens = (
    'MAIN', 'DEBUT', 'FIN', 'T_CHAINE', 'T_ENTIER','LIRE', 'AFFICHER',
    'SI', 'FSI', 'SINON', 'FSINON', 'TQ', 'FTQ',
    'OU', 'ET', 'NON',

    'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LBRACKT', 'RBRACKT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
    'COLN', 'SEMI',
    
    'IDN', 'NUM', 'STRING',
)


t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment(t):
    r'(/\*(.|\n)*?\*/)|(//.*)'
    pass

def t_IDN(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in mots_cles:
        t.type = mots_cles[t.value]
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_STRING = r'\"([^\\\n]|(\\.))*?\"'

t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKT = r'\['
t_RBRACKT = r'\]'

t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='

t_COLN = r':'
t_SEMI = r';'


# La gestion des erreurs lexicales
class ErreurLexicale(Exception):
    def __init__(self, msg):
        self.msg = msg

def t_error(t):
    raise ErreurLexicale("caractère invalide '%s' --> Ligne: %s" % (t.value[0], t.lineno))


lex.lex(debug=0)
