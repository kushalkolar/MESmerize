#Adapted from https://github.com/baoboa/pyqt5/blob/master/examples/richtext/syntaxhighlighter.py

#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

from PyQt5.QtCore import QFile, QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMenu, QWidget,
        QMessageBox, QTextEdit)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

#        self.setupFileMenu()
#        self.setupHelpMenu()
        self.setupEditor()

        self.setCentralWidget(self.editor)
#        self.setWindowTitle("Syntax Highlighter")

#    def about(self):
#        QMessageBox.about(self, "About Syntax Highlighter",
#                "<p>The <b>Syntax Highlighter</b> example shows how to " \
#                "perform simple syntax highlighting by subclassing the " \
#                "QSyntaxHighlighter class and describing highlighting " \
#                "rules using regular expressions.</p>")

#    def newFile(self):
#        self.editor.clear()
#
#    def openFile(self, path=None):
#        if not path:
#            path, _ = QFileDialog.getOpenFileName(self, "Open File", '',
#                    "python scripts (*.py)")
#
#        if path:
#            inFile = QFile(path)
#            if inFile.open(QFile.ReadOnly | QFile.Text):
#                text = inFile.readAll()
#
#                try:
#                    # Python v3.
#                    text = str(text, encoding='ascii')
#                except TypeError:
#                    # Python v2.
#                    text = str(text)
#
#                self.editor.setPlainText(text)

    def setupEditor(self):
        font = QFont()
        font.setFamily('Ubuntu Mono')
        font.setFixedPitch(True)
        font.setPointSize(12)

        self.editor = QTextEdit()
        self.editor.setFont(font)

        self.highlighter = Highlighter(self.editor.document())

#    def setupFileMenu(self):
#        fileMenu = QMenu("&File", self)
#        self.menuBar().addMenu(fileMenu)
#
#        fileMenu.addAction("&New...", self.newFile, "Ctrl+N")
#        fileMenu.addAction("&Open...", self.openFile, "Ctrl+O")
#        fileMenu.addAction("E&xit", QApplication.instance().quit, "Ctrl+Q")
#
#    def setupHelpMenu(self):
#        helpMenu = QMenu("&Help", self)
#        self.menuBar().addMenu(helpMenu)
#
#        helpMenu.addAction("&About", self.about)
#        helpMenu.addAction("About &Qt", QApplication.instance().aboutQt)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)
        
        keywords = ['False', 'None', 'True', 'and', 'as', 'assert', 'break', 'class',
                    'continue', 'def', 'del', 'elif', 'if', 'else', 'except', 'finally',
                    'for', 'from', 'import', 'global', 'in', 'is', 'lambda', 'not',
                    'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']

        keywordPatterns = ['\\b' + k + '\\b' for k in keywords]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat) for pattern in keywordPatterns]
        
        viewer_words = ['viewer', 'imgdata', 'seq', 'meta',
                        'running_modules', 'roi_manager', 'workEnv']
        viewer_syntax_words = ['\\b' + w + '\\b' for w in viewer_words]

        viewer_syntax = QTextCharFormat()
        viewer_syntax.setFontWeight(QFont.Bold)
        viewer_syntax.setForeground(Qt.darkMagenta)
        self.highlightingRules += [(QRegExp(pattern), viewer_syntax) for pattern in viewer_syntax_words]
        
        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(Qt.darkGray)
        self.highlightingRules.append((QRegExp("#[^\n]*"),
                singleLineCommentFormat))

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.red)
        
        numberFormat = QTextCharFormat()
        numberFormat.setForeground(Qt.red)
        self.highlightingRules.append((QRegExp("[\s]?[,]?[.]?\d+"), numberFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(Qt.darkGreen)
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))
        # self.highlightingRules.append((QRegExp("\'.*\'"), quotationFormat))


        functionFormat = QTextCharFormat()
        functionFormat.setFontWeight(QFont.Bold)
        functionFormat.setForeground(Qt.blue)
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
                functionFormat))

        viewer_callables = ['update_workEnv', 'clear_workEnv', 'get_module', 'get_batch_manager', 'get_workEnv']
        
        viewer_callables_syntax = ['\\b' + w + '\\b' for w in viewer_callables]
        
        viewer_callables_syntax_highlight = QTextCharFormat()
        viewer_callables_syntax_highlight.setFontWeight(QFont.Bold)
        viewer_callables_syntax_highlight.setForeground(Qt.magenta)
        self.highlightingRules += [(QRegExp(pattern), viewer_callables_syntax_highlight) for pattern in viewer_callables_syntax]


        self.commentStartExpression = QRegExp('/"""*')
        self.commentEndExpression = QRegExp('\\"""')

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength);


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 512)
    window.show()
    sys.exit(app.exec_())