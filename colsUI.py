import time
import uiautomation as automation
import sys

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTabWidget, QVBoxLayout, QPushButton, QListView, \
    QListWidget, QListWidgetItem, QHBoxLayout, QLabel, QScrollArea, QSizePolicy
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
class ColsUI(QMainWindow):
    app: QApplication

    def __init__(self,app):
        super().__init__(flags=
                         Qt.WindowStaysOnTopHint
                         # | Qt.FramelessWindowHint
                         )

        self.app=app
        self.__init_ui()

    def __init_ui(self):
        self.__init_positioning()
        self.__init_tabs()

    def __init_positioning(self):
        screen_size = self.app.primaryScreen().size()
        w, h = 400, 150
        self.setGeometry(screen_size.width() - w, screen_size.height() - h - TASKBAR_HEIGHT, w, h)
        self.setContentsMargins(0,0,0,0)

    def __init_tabs(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(MyTableWidget(self))
        pass


class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        # layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.setContentsMargins(0,0,0,0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(20)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        widget=QWidget()
        hbox=QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)

        # size_pol = QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        # size_pol.setHorizontalStretch(0)
        # size_pol.setVerticalStretch(0)
        # size_pol.setHeightForWidth(size_pol.hasHeightForWidth())
        size_pol=QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        for i in range(10):
            but=QPushButton()
            but.setContentsMargins(0,0,0,0)
            but.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
            hbox.addWidget(but)
        widget.setLayout(hbox)

        scroll.setWidget(widget)

        self.tab1.layout.addWidget(scroll)
        self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

if __name__=='__main__':
    app = QApplication(sys.argv)
    ui = ColsUI(app)
    ui.show()
    sys.exit(app.exec_())