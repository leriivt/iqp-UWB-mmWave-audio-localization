import tkinter as tk
import tkinter.ttk as ttk

class TRX_display_ui(object):
    def __init__(self, frame_trx):
        uart_trx_frame = tk.Frame(frame_trx)
        # 创建一个Scrollbar和Text组件，并将它们关联
        scrollbar = tk.Scrollbar(uart_trx_frame)
        self.this_rev_Text = tk.Text(uart_trx_frame, width=45, height=48)
        scrollbar.config(command=self.this_rev_Text.yview)
        # 放置组件
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.this_rev_Text.pack()
        uart_trx_frame.place(x=10, y=40)

        # # 创建单独hex格式显示
        # uart_trx_hex_frame = tk.Frame(frame_trx)
        # # 创建一个Scrollbar和Text组件，并将它们关联
        # scrollbar_hex = tk.Scrollbar(uart_trx_hex_frame)
        # self.this_rev_hex_Text = tk.Text(uart_trx_hex_frame, width=30, height=24)
        # scrollbar.config(command=self.this_rev_hex_Text.yview)
        # # 放置组件
        # scrollbar_hex.pack(side=tk.RIGHT, fill=tk.Y)
        # self.this_rev_hex_Text.pack()
        # uart_trx_hex_frame.place(x=10, y=360)
    
        ttk.Button(frame_trx, text="清除", command=self.clear_rxt_text, width=4).place(x=10, y=10)

    def clear_rxt_text(self):
        print("clear_rxt_text")
        self.this_rev_Text.delete('1.0', 'end')
        # self.this_rev_hex_Text.delete('1.0', 'end')
