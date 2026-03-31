import threading
import time
import queue

# import window.uart.uart_module as uart_module
import common.uart.uart_module as uart_module
import common.Format_conversion as Format_conversion

class UartInfo(object):
    def __init__(self, fd, count, fail, ui):
        self.fd = fd
        self.count = count  # 测试次数
        self.fail = fail  # 失败次数
        self.tty = ui.this_com_combobox.get()
        self.btl = ui.this_btl_combobox.get()
        
        self.single_read_flag = 0
        self.ui = ui
        
        self.searil_q = queue.Queue()  # 创建一个先进先出队列
        
        self.rev_count = 0  # 接收字节数

        self.readstr = ""
        
        
        self.ui.this_open_button["command"] = self.serial_open_close
        # self.ui.this_Send_button["command"] = self.serial_Send

        self.thread_1 = None  # 外部同步UART启动线程1
        self.thread_2 = None  # 外部同步UART启动线程2
        self.uart_data_ana_function = None  # 外部调用解析函数

        self.ReadData_Thread_hand = None  # UART读取缓存函数
        self.uart_data_ana_Thread_hand = None  # UART解析及帧对齐函数
        self.serial_close_ReadData_Thread_flag = 0  # UART读取缓存函数，线程退出标志位
        self.serial_close_uart_data_ana_Thread_flag = 0  # UART解析及帧对齐函数，线程退出标志位
    

    # UART恢复默认参数
    def serial_def(self):
        self.count = 0  # 测试次数
        self.fail = 0  # 失败次数
        self.tty = self.ui.this_com_combobox.get()
        self.btl = self.ui.this_btl_combobox.get()

    # UART线程关闭函数，UART开关调用或者UART拔出调用，或者Windows退出调用
    def close_window(self):
        print("uart close_window")
        
        if self.ReadData_Thread_hand is not None:
            self.serial_close_ReadData_Thread_flag = 1
            self.ReadData_Thread_hand.join()
            self.ReadData_Thread_hand = None
            
        if self.uart_data_ana_Thread_hand is not None:
            self.serial_close_uart_data_ana_Thread_flag = 1
            self.uart_data_ana_Thread_hand.join()
            self.uart_data_ana_Thread_hand = None

    # 关闭UART
    def abnormal_close(self):
        try:
            if self.fd != -1:
                
                self.close_window()

                uart_module.DColsePort(self.fd)
                self.fd = -1  # 必须关闭UART,再进行赋值

                if self.thread_1 is not None:
                    self.thread_1(0)
                if self.thread_2 is not None:
                    self.thread_2(0)

                self.ui.this_open_button["text"] = "打开"
                self.ui.this_com_combobox["state"] = "enable"
                self.ui.this_btl_combobox["state"] = "enable"
                self.ui.this_uart_com_update_button["state"] = "enable"
        except:
            print("应该退出主程序了，不需要更新显示标签")

    # 打开UART
    def uart_open(self):
        self.fd = uart_module.DOpenPort(self.tty, self.btl, None)
        if(self.fd != -1):
            self.ReadData_Thread_hand = threading.Thread(target=self.ReadData_Thread)
            self.uart_data_ana_Thread_hand = threading.Thread(target=self.uart_data_ana_Thread)
            self.serial_close_ReadData_Thread_flag = 0
            self.serial_close_uart_data_ana_Thread_flag = 0
            self.ReadData_Thread_hand.start()
            self.uart_data_ana_Thread_hand.start()
                
            self.ui.this_open_button["text"] = "关闭"
            self.ui.this_com_combobox["state"] = "disable"
            self.ui.this_btl_combobox["state"] = "disable"
            self.ui.this_uart_com_update_button["state"] = "disable"

            if self.thread_1 is not None:
                self.thread_1(1)
            if self.thread_2 is not None:
                self.thread_2(1)
        
        return self.fd


    def serial_open_close(self):
        self.ui.this_open_button["state"] = "disable"
        if self.fd != -1:
            self.abnormal_close()

            print("正常关闭了uart")
        else:
            self.serial_def()
            if self.tty == "" or self.btl == "":
                print("参数为空！")
                return -2
            
            print("COM = ", self.tty, "波特率 = ", self.btl)
            
            if self.uart_open() != -1:
                print("正常打开了uart")

        self.ui.this_open_button["state"] = "enable"
    
    # def serial_Send(self):
    #     if self.fd == -1:
    #         print("serial is not open !")
    #         return
        
    #     Send_data = self.ui.this_Send_Entry.get()
    #     print("Send_data = ", Send_data)
    #     # 将其转换为bytes
    #     bytes_string = Send_data.encode('utf-8')
    #     # print("bytes_string = ", bytes_string)

    #     bytes_string = bytes([0x12, 0x34, 0x56])
    #     uart_module.DWritePort(self.fd, bytes_string)

    #     bytes_string = chr(126)
    #     print("bytes_string = ", bytes_string)

    #     # 添加Send data到记录框
    #     self.ui.this_rev_Text.insert("end", Send_data + "\r\n")
    

    # UART读取缓存函数
    def ReadData_Thread(self):
        while(1):
            if self.serial_close_ReadData_Thread_flag == 1:
                print("exit ReadData_Thread 2")
                return
            time.sleep(0.01)

            try:
                read_num = self.fd.in_waiting
                if self.single_read_flag == 0 and read_num > 0:
                    uart_readbuf = self.fd.read(read_num)

                    # 接收数量统计
                    self.rev_count += self.fd.in_waiting

            except:
                print("ReadData_Thread err, uart maybe close!")
                self.ReadData_Thread_hand = None
                self.abnormal_close()
                return
            try:
                if self.single_read_flag == 0 and read_num > 0:
                    self.max_listbox_data_parsing(read_num, uart_readbuf)
            except:
                print("max_listbox_data_parsing err")
            # if self.single_read_flag == 0 and read_num > 0:
            #     self.max_listbox_data_parsing(read_num, uart_readbuf)
    
    
    # UART解析及帧对齐函数
    def uart_data_ana_Thread(self):
        self.searil_q.queue.clear()
        self.searil_q = queue.Queue()  # 创建一个先进先出队列
        while(1):
            if self.serial_close_uart_data_ana_Thread_flag == 1:
                print("exit uart_data_ana_Thread 1")
                return

            try:
                if self.searil_q.empty() is False:
                    data_one_line = self.searil_q.get()
                    # print("data_one_line = ", data_one_line)
                    
                    if self.uart_data_ana_function is not None:
                        res = self.uart_data_ana_function(data_one_line)
                        if res == -1:
                            self.searil_q.queue.clear()
                            self.searil_q = None
                            print("重新创建队列")
                            self.searil_q = queue.Queue()  # 创建一个先进先出队列
                            print("队列异常了！")
                    
            except:
                print("uart_data_ana_Thread 22 err")
                # return
            
            time.sleep(0.1)
    

    # 帧头帧尾对齐
    def max_listbox_data_parsing(self, len1, data):
        # read_new = Format_conversion.uart_hexShow(data)
        read_new = Format_conversion.BINbytes_to_HEXstr(data, 0)  # BIN_to_HEXstr
        len2 = len(self.readstr)
        self.readstr += read_new
        this_len = len1 * 2 + len2  # - 3

        if this_len > 2000:
            self.readstr = ""
            print("max_listbox_data_parsing, this_len > 2000")
            return -1
        i = 0
        while(i < this_len):
            temp = self.readstr[i:(i+4)]
            if temp == "0d0a":  #协议解析1
            # if self.readstr[i:(i+4)] == "0d0a":
                result = self.readstr[:(i+4)]

                if self.readstr[(i+4):(i+6)] == "00":
                    self.readstr = self.readstr[(i+6):]
                    this_len = this_len - i - 6
                else:
                    self.readstr = self.readstr[(i+4):]
                    this_len = this_len - i - 4
                
                i = 0

                self.searil_q.put(result)

                # temp2 = result[:8]
                # if temp2 == "54544d3a":
                if result[:8] == "54544d3a":
                    res2 = MINWSEMI_data(result)
                    self.ui.this_rev_Text.insert("end", "--<" + res2 + "\r\n")

                continue
            elif temp == "0102":  #协议解析1
                if self.readstr[i:(i+16)] == "0102030405060708":
                    len1 = self.readstr[(i + 16):(i+24)]
                    Frame_length = Format_conversion.HEXstr_to_INT(len1, 0) * 2
                    if (this_len - i) >= Frame_length:
                        result = self.readstr[i:(i+Frame_length)]
                        self.readstr = self.readstr[(i+Frame_length):]

                        i = 0
                        this_len = this_len - i - Frame_length
                        self.searil_q.put(result)
                        continue
                        
            i += 2

    
    def MINEWSEMI_analyze(self, len, data):
        # 查找帧头“TTM:”
        result = ""
        for i in range(0, len, 1):
            if data[i:i + 3] == "54 " and data[i+3:i + 6] == "54 " and data[i+6:i + 9] == "4d " and data[i+9:i + 12] == "3a ":
                result = data[(i+2)*3:]
                break

        if result != "":
            len = len - i - 12
            for i in range(0, len, 1):
                if data[i:i + 3] == "0d " and data[i+3:i + 6] == "0a ":
                    result = result[:(i+2)*3]
                    return result
                
        return -1


    # 发送data
    def serial_Send_command(self, command):
        uart_module.DWritePort(self.fd, command)
    
    # 发送+超时读取
    def serial_Send_command_and_read(self, command, rev_len):
        # print("command = ", command)
        
        self.single_read_flag = 1  # 单个读取标志位
        uart_module.DWritePort(self.fd, command)
        if rev_len > 0:
            res1 = self.serial_rev_command()
        else:
            res1 = -2
        self.single_read_flag = 0
        return res1

    # 超时读取指令
    def serial_rev_command(self):
        read_count = 5
        readbuf = ""
        while(1):
            time.sleep(0.1)
            if self.fd.in_waiting:
                readbuf = self.fd.read(self.fd.in_waiting)

            if len(readbuf) > 0:
                return readbuf
            
            if read_count == 0:
                return -1
            else:
                read_count = read_count - 1


def MINWSEMI_data(data):
    send_command_head = ""
    # result_str = ""

    s1 = data.split("0d0a")
    s2 = s1[0]
    s21 = s2.split("2d")
    s21_0 = s21[0]
    send_command_head = Format_conversion.HEXStr_to_WORDstr(s21_0)

    len1 = len(s21)
    if len1 == 3:
        result_str = Format_conversion.HEXStr_to_WORDstr(s21[1])  # hexStr_to_str
        result_str += " = " + s21[2]
    else:
        result_str = ""  # 返回值为空

    return send_command_head + result_str
