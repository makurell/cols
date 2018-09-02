import os
import time
import uiautomation as automation
import sys
from cols import ColFile, ColItem, ColSection

from PyQt5.QtGui import QPixmap, QIcon, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTabWidget, QVBoxLayout, QPushButton, QListView, \
    QListWidget, QListWidgetItem, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QGridLayout, QLayout, QFileDialog
from PyQt5.QtCore import Qt, pyqtSlot, QSize


def get_chrome_url(focused=False):
    try:
        if not focused:
            control = automation.FindControl(automation.GetRootControl(),lambda c,d: c.ClassName.startswith('Chrome'))
        else:
            control = automation.GetFocusedControl()
            control_list = []
            while control:
                control_list.insert(0, control)
                control = control.GetParentControl()
            if len(control_list) == 1:
                control = control_list[0]
            else:
                control = control_list[1]
        address_control = automation.FindControl(control, lambda c, d: isinstance(c,automation.EditControl) and "Address and search bar" in c.Name)
        return address_control.CurrentValue()
    except AttributeError:
        return None


TASKBAR_HEIGHT=50
IMG_WIDTH=130
class ColsUI(QMainWindow):
    app: QApplication

    def __init__(self,app,cf:ColFile):
        super().__init__(flags=
                         Qt.WindowStaysOnTopHint
                         # | Qt.FramelessWindowHint
                         )
        self.app=app
        self.cf=cf
        self.__init_ui()

    def __init_ui(self):
        self.__init_positioning()
        self.__init_core()

    def __init_positioning(self):
        screen_size = self.app.primaryScreen().size()
        w, h = 550, 200
        self.setGeometry(screen_size.width() - w, screen_size.height() - h - TASKBAR_HEIGHT, w, h)
        self.setFixedHeight(h)
        self.setContentsMargins(0,0,0,0)

    def __init_core(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(CoreWidget(self))
        pass


class CoreWidget(QWidget):

    def onbutclicked(self,but):
        print(but.height())

    def __init_sec(self):
        #container stuff
        wgt = QWidget()
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignBottom)
        vbox.setContentsMargins(4, 4, 0, 4)
        vbox.setSpacing(0)

        #top imgbutton
        imgbut = QPushButton()
        imgbut.setContentsMargins(0, 0, 0, 0)
        imgbut.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        pixmap = QPixmap('assets/test.jpg')
        ratio = pixmap.width() / pixmap.height()
        pixmap = pixmap.scaled(IMG_WIDTH, IMG_WIDTH / ratio, Qt.KeepAspectRatio)
        imgbut.setIcon(QIcon(pixmap))
        imgbut.setIconSize(pixmap.size())
        imgbut.setFixedWidth(IMG_WIDTH)
        imgbut.setFixedHeight(120)

        imgbut.clicked.connect(lambda: self.onbutclicked(imgbut))
        vbox.addWidget(imgbut)

        #bottom label
        label = QLabel('lel')
        label.setAlignment(Qt.AlignCenter)
        label.setContentsMargins(0, 4, 0, 0)
        vbox.addWidget(label)

        wgt.setLayout(vbox)
        return wgt

    def __init_tab(self):
        #container stuff
        tab = QWidget()
        tab.layout = QVBoxLayout(self)
        tab.layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(20)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        widget = QWidget()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        #secs
        for i in range(10):
            hbox.addWidget(self.__init_sec())

        #adding widgets
        widget.setLayout(hbox)
        scroll.setWidget(widget)
        tab.layout.addWidget(scroll)
        tab.setLayout(tab.layout)
        return tab

    def __init__tabs(self):
        tabs = QTabWidget()

        # Add tabs
        tabs.addTab(self.__init_tab(), "Tab 1")

        return tabs

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.__init__tabs())
        self.setLayout(self.layout)

if __name__=='__main__':
    app = QApplication(sys.argv)

    if os.path.isfile('data.col'):
        cf = ColFile('data.col')
    else:
        cf = ColFile(QFileDialog.getOpenFileName()[0])
    cf.base_path = 'cols'
    cf.parse()
    cf.render()
    print('Ready')

    ui = ColsUI(app,cf)
    ui.show()
    sys.exit(app.exec_())