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
    extra_vars = {'vi', 'all_modules', 'image_utils', 'viewer'}
    extra_callables = {'update_workEnv', 'clear_workEnv', 'get_module', 'get_batch_manager', 'get_workEnv', 'get_image, get_meta'}
    extra_classes = {'ViewerWorkEnv', 'ImgData'}

    def get_tokens_unprocessed(self, text):
        for index, token, value in Python3Lexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.extra_vars:
                yield index, Name.Namespace, value
            elif token is Name and value in self.extra_callables:
                yield index, Name.Function, value
            elif token is Name and value in self.extra_classes:
                yield index, Name.Class, value
            else:
                yield index, token, value

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
