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

from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from pygments import highlight
from pygments.lexers.python import Python3Lexer
from pygments.formatter import Formatter
from pygments.token import Name, Keyword


def hex2QColor(c):
    r=int(c[0:2],16)
    g=int(c[2:4],16)
    b=int(c[4:6],16)
    return QColor(r,g,b)


class ViewerLexer(Python3Lexer):
    extra_vars = {'viewer', 'running_modules', 'roi_manager'}
    extra_callables = {'update_workEnv', 'clear_workEnv', 'get_module', 'get_batch_manager', 'get_workEnv'}

    def get_tokens_unprocessed(self, text):
        for index, token, value in Python3Lexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.extra_vars:
                yield index, Name.Namespace, value
            elif token is Name and value in self.extra_callables:
                yield index, Name.Function, value
            else:
                yield index, token, value


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        self.setupEditor()

        self.setCentralWidget(self.editor)

    def setupEditor(self):
        font = QFont()
        font.setFamily('Ubuntu Mono')
        font.setFixedPitch(True)
        font.setPointSize(12)

        self.editor = QTextEdit()
        self.editor.setFont(font)

        # self.highlighter = Highlighter(self.editor.document())

class QFormatter(Formatter):

    def __init__(self):
        Formatter.__init__(self)
        self.data = []

        self.styles = {}
        for token, style in self.style:
            qtf = QTextCharFormat()

            if style['color']:
                qtf.setForeground(hex2QColor(style['color']))
            if style['bgcolor']:
                qtf.setBackground(hex2QColor(style['bgcolor']))
            if style['bold']:
                qtf.setFontWeight(QFont.Bold)
            if style['italic']:
                qtf.setFontItalic(True)
            if style['underline']:
                qtf.setFontUnderline(True)
            self.styles[str(token)] = qtf

    def format(self, tokensource, outfile):
        global styles
        self.data = []


        for ttype, value in tokensource:
            l = len(value)
            t = str(ttype)
            self.data.extend([self.styles[t], ] * l)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)
        self.formatter = QFormatter()
        self.lexer = ViewerLexer()

    def highlightBlock(self, text):

        cb = self.currentBlock()
        p = cb.position()

        text = self.document().toPlainText()

        highlight(text, self.lexer, self.formatter)

        for i in range(len(text)):
            try:
                self.setFormat(i, 1, self.formatter.data[p + i])
            except IndexError:
                pass


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 512)
    window.show()
    sys.exit(app.exec_())