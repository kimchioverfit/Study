from PyQt5.QtWidgets import *
from PyQt_ui_sample import ProgressDialog

class Child(ProgressDialog):
    def __init__(self):
        super().__init__()

    def excute(self, progress_callback = None, progress_type = None, lot_list_callback = None):
        print()
    
    excute_this_fn = excute
    # self.fn =fn 을 통해서 Command + Template Method 구현을 할 수 있는 이유는
    # main 함수에서 Child 생성하기 때문. 
    # Child 생성자가 호출되면, 자식 인스턴스를 먼저 생성하고 부모 생성자를 실행함.
    # 그렇기 때문에, Progress에서 worker가 run한다는 것은 자식인스턴스를 run한다는것임
    # excute_this_fn = excute 이렇게 해주는 이유는, 런타임에 동작을 바꿀 수 있는 여지가 있기 때문.
    # if some_condition:
    #     self.excute_this_fn = self.func_a
    # else:
    #     self.excute_this_fn = self.func_b
    # 이런식으로 만들어주면, worker가 함수를 run할때, 조건에 따라 다른 함수를 호출하게 구현이 가능함.

