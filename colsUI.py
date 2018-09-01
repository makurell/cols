import time
import uiautomation as automation
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTabWidget, QVBoxLayout, QPushButton, QListView, \
    QListWidget, QListWidgetItem, QHBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt, pyqtSlot


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
        w, h = 400, 70
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
        # self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.setContentsMargins(0,0,0,0)

        wgt=QWidget()
        hbox=QHBoxLayout(self)
        hbox.addWidget(QPushButton('test'))
        wgt.setLayout(hbox)

        scroll_area = QScrollArea()
        # hbox = QHBoxLayout()
        # hbox.addWidget(QPushButton('test'))
        # scroll_area.setLayout(hbox)
        # scroll_area.setWidget(hbox)
        scroll_area.setWidget(wgt)

        self.tab1.layout.addWidget(scroll_area)

        # wgt = QWidget()
        # wgt.addWidget(QLabel('test'))
        # wgt.addWidget(QLabel('test2'))
        # wgt.addWidget(QLabel('test3'))
        # wgt.addWidget(QLabel('test4'))
        # wgt.tab1.setLayout(self.tab1.layout)

        # scroll_area= QScrollArea()
        # scroll_area.setWidget(wgt)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

if __name__=='__main__':
    app = QApplication(sys.argv)
    ui = ColsUI(app)
    ui.show()
    sys.exit(app.exec_())