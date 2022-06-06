from PyQt5 import QtCore, QtWidgets

import syn_sem
import exe

from lex import ErreurLexicale
from syn_sem import ErreurSyntaxique
from syn_sem import ErreurSemantique


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Mini-Compilateur OUZGHARA, 2022"
        
        self.fichier_courant = None # Le chemin du fichier courant
        self.text_modifie = False # L'état des changements
        self.arbre = None # L'arbre abstrait généré lors de la compilation

        self.initUI()
    # ==============================================================================================
    def initUI(self):

        self.resize(800, 600)
        
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)

        self.editeur = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.editeur.setStyleSheet("""QPlainTextEdit {
            font-family:'Consolas';
            font-size: 18px;
            color: #ddd;
            background-color: #2b2b2b;}""")
        self.verticalLayout.addWidget(self.editeur)

        self.etat = QtWidgets.QTextEdit(self.centralwidget)
        self.etat.setEnabled(False)
        self.etat.setMaximumSize(QtCore.QSize(16777215, 30))
        self.etat.setStyleSheet("""QTextEdit {
            font-family:'Consolas';
            font-size: 17px;
            color: blue;
            background-color: #ddd;}""")
        self.verticalLayout.addWidget(self.etat)
        self.etat.hide()

        self.console = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.console.setMaximumSize(QtCore.QSize(16777215, 180))
        self.console.setStyleSheet("""QPlainTextEdit {
            font-family:'Consolas';
            font-size: 16px;
            color: green;
            background-color: #000;}""")
        self.verticalLayout.addWidget(self.console)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))

        self.menuFichier = QtWidgets.QMenu(self.menubar)
        
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.actionOuvrir = QtWidgets.QAction(self)
        self.actionEnregistrer = QtWidgets.QAction(self)
        self.actionCompiler = QtWidgets.QAction(self)
        self.actionExecuter = QtWidgets.QAction(self)
        self.actionA_propos = QtWidgets.QAction(self)

        self.menuFichier.addAction(self.actionOuvrir)
        self.menuFichier.addAction(self.actionEnregistrer)
        
        self.menubar.addAction(self.menuFichier.menuAction())
        self.menubar.addAction(self.actionCompiler)
        self.menubar.addAction(self.actionExecuter)
        self.menubar.addAction(self.actionA_propos)

        self.actionOuvrir.triggered.connect(self.ouvrir_fichier)
        self.actionEnregistrer.triggered.connect(self.sauv_fichier)
        self.actionCompiler.triggered.connect(self.compiler)
        self.actionExecuter.triggered.connect(self.executer)
        self.actionA_propos.triggered.connect(self.a_propos)
        self.editeur.textChanged.connect(self.est_modifie)

        self.retranslateUi()
    # ==============================================================================================
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", self.title))
        self.menuFichier.setTitle(_translate("MainWindow", "Fichier"))
        self.actionOuvrir.setText(_translate("MainWindow", "Ouvrir..."))
        self.actionOuvrir.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionEnregistrer.setText(_translate("MainWindow", "Enregistrer..."))
        self.actionEnregistrer.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionCompiler.setText(_translate("MainWindow", "Compiler"))
        self.actionCompiler.setShortcut(_translate("MainWindow", "Ctrl+B"))
        self.actionExecuter.setText(_translate("MainWindow", "Exécuter"))
        self.actionExecuter.setShortcut(_translate("MainWindow", "Ctrl+F5"))
        self.actionA_propos.setText(_translate("MainWindow", "A propos"))
    # ==============================================================================================
    # ==============================================================================================
    def est_modifie(self):
        self.text_modifie = True
    # ==============================================================================================
    def reset(self):
        self.text_modifie = False
        self.arbre = None
        self.etat.hide()
        self.etat.setText('')
        self.console.setPlainText('')
    # ==============================================================================================
    def ouvrir_fichier(self):
        if self.text_modifie:
            msgBox = QtWidgets.QMessageBox()
            title = "Sauvegarder les changements?"
            msg = "Voulez vous sauvegarder les changements avant d'ouvrir un nouveau fichier?"
            reponse = msgBox.question(self, title, msg, msgBox.Yes | msgBox.No | msgBox.Cancel)
            if reponse == msgBox.Yes: self.sauv_fichier()
            elif reponse == msgBox.Cancel: return

        _chemin_fichier, filtre = QtWidgets.QFileDialog.getOpenFileName(self, "Ouvrir")
        if _chemin_fichier == '': return
        self.fichier_courant = _chemin_fichier
        with open(self.fichier_courant, "r") as f:
            file_contents = f.read()
        self.setWindowTitle(self.fichier_courant)
        self.editeur.setPlainText(file_contents)
        self.reset()
    # ==============================================================================================
    def sauv_fichier(self):
        if not self.fichier_courant:
            # Il n'existe pas un fichier ouvert, donc sauvegarder un nouveau fichier
            _chemin_fichier, filtre = QtWidgets.QFileDialog.getSaveFileName(self, "Enregistrer sous")
            if _chemin_fichier == '': return
            self.fichier_courant = _chemin_fichier
        elif not self.text_modifie: return

        file_contents = self.editeur.document().toPlainText()
        with open(self.fichier_courant, "w") as f:
            f.write(file_contents)
        self.setWindowTitle(self.fichier_courant)
        self.text_modifie = False
    # ==============================================================================================
    def closeEvent(self, event):
        if self.text_modifie:
            msgBox = QtWidgets.QMessageBox()
            title = "Sauvegarder les changements?"
            msg = "Voulez vous sauvegarder les changements avant de quitter?"
            reponse = msgBox.question(self, title, msg, msgBox.Yes | msgBox.No | msgBox.Cancel)
            if reponse == msgBox.Yes: self.sauv_fichier()
            elif reponse == msgBox.No: event.accept()
            else: event.ignore()
    # ==============================================================================================
    # ==============================================================================================
    def compiler(self):
        source = self.editeur.document().toPlainText()
        if source == '':
            title = 'Vide!'
            msg = "Svp, veuillez écrire un programme."
            QtWidgets.QMessageBox.warning(self, title, msg, QtWidgets.QMessageBox.Close)
        else:
            self.arbre = None
            self.etat.show()
            self.console.setPlainText('')

            try:
                self.arbre = syn_sem.analyser(source)
                self.etat.setText("Réussi: l'arbre abstrait a été généré.")
                return True
            except ErreurLexicale as l:
                self.etat.setText("ErreurLexicale: %s" % l)
            except ErreurSyntaxique as sn:
                self.etat.setText("ErreurSyntaxique: %s" % sn)
            except ErreurSemantique as sm:
                self.etat.setText("ErreurSemantique: %s" % sm)
        return False
    # ==============================================================================================
    def afficher(self, exp):
        self.console.setPlainText(self.console.document().toPlainText() + str(exp) + '\n')
    # ==============================================================================================
    def lire(self):
        title = 'Data'
        msg = ''
        data, done = QtWidgets.QInputDialog.getText(self, title, msg)
        if done: return data
        raise ValueError
    # ==============================================================================================
    def executer(self):
        if not self.arbre:
            title = 'Programme non compilé!'
            msg = "Svp, veuillez compiler votre programme d'abord."
            QtWidgets.QMessageBox.warning(self, title, msg, QtWidgets.QMessageBox.Close)
            return
        
        try:
            self.etat.setText("En cours d'éxécution...")
            self.console.setPlainText('')
            exe.executer(self.arbre, self.lire, self.afficher)
            self.etat.setText("Fin d'éxécution.")

        except ErreurSemantique as sm:
            self.etat.setText("ErreurSemantique: %s" % sm)
        except ValueError:
            self.etat.setText("Erreur d'éxécution: erreur d'entrée")
        except IndexError:
            self.etat.setText("Erreur d'éxécution: erreur d'indice")
    # ==============================================================================================
    def a_propos(self):
        title = 'A propos de nous'
        msg ="""
            Réalisé par:
            EOC. OUZGHARA Riyadh

            1 ère Année
            Génie Informatique

            Section: 1
            Groupe: C"""
        QtWidgets.QMessageBox.information(self, title, msg, QtWidgets.QMessageBox.Close)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = App()
    win.show()
    sys.exit(app.exec_())
