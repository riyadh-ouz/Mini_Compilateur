from syn_sem import analyser, table_symboles
from exe import executer

from lex import ErreurLexicale
from syn_sem import ErreurSyntaxique
from syn_sem import ErreurSemantique

import sys

if len(sys.argv) == 2:

    try:
        with open(sys.argv[1]) as f:
            source = f.read()
        arbre = analyser(source)

        if input("Si vous voulez voir l'arbre abstrait et la table des symboles, entrez '1': ") == '1':
            arbre.visualiser()
            print('La table des symboles:\n', table_symboles)
        
        print("\nExécution...\n")
        executer(arbre)

        raise SystemExit
    
    except ErreurLexicale as l:
        print("ErreurLexicale: %s" % l)
    except ErreurSyntaxique as sn:
        print("ErreurSyntaxique: %s" % sn)
    except ErreurSemantique as sm:
        print("ErreurSemantique: %s" % sm)
            
    except ValueError:
        print("Erreur d'éxécution: entrée invalide")
    except IndexError:
        print("Erreur d'éxécution: erreur d'indice")

else:
    print("No input file!")
