import MS50SFA_TTM.Format_conversion as Format_conversion
from system.sys_data import sys_data2


# 写入data到模块
def command_Send(input_data, uart, uart_ui):
    this_data = input_data
    name = this_data.name
    print("write: ", name)
    result_data = -1

    try:
        command = get_bytes_form_data(this_data.command, this_data.command_type)
        data = get_bytes_form_data(this_data.data, this_data.data_type)
        command_end = get_bytes_form_data(this_data.command_end, this_data.command_end_type)
        
        command_write_bytes = command + data + command_end
        uart_ui.this_rev_Text.insert("end", "\r\n" + this_data.name + "\r\n")

        command_write_str = this_data.command + str(this_data.data)  # + this_data.command_end
        uart_ui.this_rev_Text.insert("end", command_write_str + "\r\n")
    except:
        print("Assertion error: command_Send, input data is err.", name)
        result_data = -2
    
    if uart.fd != -1:
        try:
            result = uart.serial_Send_command_and_read(command_write_bytes, 1)
        except:
            print("Assertion error: command_Send, uart is err.", name)

        # 返回值处理
        try:
            if result != -1 and result != -2:
                # result_str = result.decode('utf-8')[1:-1]
                result_str = result.decode('utf-8')
                result_str1 = result_str.replace("\r\n\x00", "")
                
                uart_ui.this_rev_Text.insert("end", result_str1 + "\r\n")
            elif result == -2:
                print("uart 无需返回值")
            else:
                if this_data.name != "透传发送":
                    print("uart 无返回值")
                    uart_ui.this_rev_Text.insert("end", "uart 无返回值 ! \r\n")
                    result_data = -1
        except:
            print("Assertion error: command_Send, data analyze err.", name)
            result_data = -2
    else:
        uart_ui.this_rev_Text.insert("end", "not write, COM not open ! \r\n")
        print("uart not open !")
        
    uart_ui.this_rev_Text.see("end")
    uart_ui.window.update()
    
    return result_data


#从模块读取
def get_data_from_remote(data, uart, uart_ui):

    this_data = data
    name = this_data.name

    result_data = -1
    
    try:
        command_read = this_data.command + this_data.data + this_data.command_end
        print("read: ", name)
        
        bytes_string = command_read.encode('utf-8')  # 将其转换为bytes
        hex_command = Format_conversion.this_hexShow(bytes_string)  # 十六进制指令显示
        
        uart_ui.this_rev_Text.insert("end", "\r\n" + name + "\r\n")
        uart_ui.this_rev_Text.insert("end", command_read + "\r\n")
    except:
        print("Assertion error: get_data_from_remote, input value is err")
        result_data = -2

    if uart.fd != -1:
        try:
            # 发送指令与读取返回值
            result = uart.serial_Send_command_and_read(bytes_string, 1)
        except:
            print("Assertion error: get_data_from_remote, uart data err")
            result_data = -2

        try:
            if result != -1:
                result_str = str(result)[2:-1]
                hex_result = Format_conversion.this_hexShow(result)
                # s1 = hex_result.split(" 00 ")
                s1 = hex_result.split(" 0d 0a 00 ")
                s2 = s1[0]
                s21 = s2.split(" 2d ")
                s21_0 = s21[0]
                send_command_head = Format_conversion.hex_to_str(s21_0)
                
                if len(s21) >= 2:
                    s22 = s21[1]
                    s3 = s22.replace(' ', '')
                    s4 = str(s3)
                else:
                    s4 = ""  # 返回值为空

                result_data = get_read_result(s4, this_data.rev_type)
                uart_ui.this_rev_Text.insert("end", send_command_head + " " + result_data + "\r\n")

                # 结果更新显示
                
            else:
                print("uart 无返回值")
                uart_ui.this_rev_Text.insert("end", "not read, uart 无返回值 ! \r\n")
                result_data = -1
        except:
            print("Assertion error: get_data_from_remote, rev data analyze err")
            result_data = -2
    else:
        uart_ui.this_rev_Text.insert("end", "not read, COM not open ! \r\n")
        print("uart not open ! read")
            
    uart_ui.this_rev_Text.see("end")
    uart_ui.window.update()

    return result_data


#解析读取结果
def get_read_result(str1, type):
    str1 = str1.replace(" ", "")
    if type == "INT":
        res1 = str(int(str1, 16))
    elif type == "HEX":
        res1 = str1
    elif type == "ASCII":
        res1 = Format_conversion.hex_to_str(str1)
    
    return res1


# 写入结果解析
def get_result_write(command, str1, type):
    
    len1 = len(command)
    if command[:12] == "54 54 4d 3a " and command != str1[:len1]:
        return -1  # 指令不符合
    
    len2 = len(str1)
    len3 = len1 + 10
    if len2 > len3:
        str1 = str1[len1:-10]
    else:
        # res = str1.encode('utf-8')
        return ""
    
    str1 = str1.replace(" ", "")
    if type == "INT":
        res1 = str(int(str1, 16))
    elif type == "HEX":
        res1 = str1
    elif type == "ASCII":
        try:
            res1 = Format_conversion.hex_to_str(str1)
        except:
            res1 = "default"
            print("转换不成功！", str1)
    
    return res1


def string_to_binary(string):
    binary_string = ""
    for char in string:
        binary = bin(ord(char))[2:]  # 获取每个字符的ASCII码，并将其转换为二进制字符串
        padded_binary = binary.zfill(8)  # 将每个二进制字符串填充到8位
        binary_string += padded_binary
    return binary_string


def get_bytes_form_data(data, type_w):
    if data is None or type_w is None:
        data3 = "".encode('utf-8')
        return data3
    if "INT" == type_w:
        data3 = data.to_bytes(1, 'big')
    elif "ASCII" == type_w:
        data3 = data.encode('utf-8')
    elif "HEX" == type_w:
        len1 = len(data)
        if len1 % 2 != 0:  #"fromhex"这个算法必须为2个字节对齐
            data = data[:-1]
        data3 = bytes.fromhex(data)

    return data3
