import sys
from PyQt_execute_sample import Child
from PyQt5.QtWidgets import *

def main():
    app = QApplication(sys.argv)
    dlg = Child() #Child를 호출한다는 점이 중요
    dlg.exec()
    
if __name__ == "__main__":
    main()