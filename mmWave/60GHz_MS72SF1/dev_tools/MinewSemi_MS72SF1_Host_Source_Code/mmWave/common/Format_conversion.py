import struct
import binascii
import common.system.sys_data as sys_data


# INT转HEX字符串
# HEX字符串转BIN串
# 字节串（单词或者句子）转 HEX字符串
# # FLOAT转HEX字符串

# HEX字符串转字节串（单词或者句子）
# HEX字符串转有符号INT
# HEX字符串转有符号FLOAT
# BIN串转HEX字符串


# 输入：INT_data:INT
# 输入：this_len:输出的HEX字符串为几个字节
# 输入：big_or_little:0=小端，1=大端
# 输出：HEX字符串
def INT_to_HEXStr(INT_data, this_len, big_or_little):

    if big_or_little == 0:
        data = INT_data.to_bytes(this_len, 'little')
    else:
        data = INT_data.to_bytes(this_len, 'big')

    return data

# 输入：HEX字符串（长度无限制：''）.去掉空格
# 输出：bytes字符串，输入字符为奇数，自动补0
def HEXstr_to_HEXStr(HEX_data):
    data = HEX_data
    len1 = len(data)
    if len1 % 2 != 0:  #"fromhex"这个算法必须为2个字节对齐
        data = data[:-1]
    data3 = bytes.fromhex(data)

    return data3

# 输入：单词、句子
# 输出：HEX字符串
def WORDstr_to_HEXStr(word_str):
    return word_str.encode('utf-8')


# 输入：HEX字符串
# 输出：二进制串，用于串口驱动发送。
# 注意：该二进制串可以用加法进行组合，但是不能用len()计算长度
def HEXStr_to_BINbytes(HEX_str):
    # 将其转换为bytes
    bytes_string = HEX_str.encode('utf-8')
    # print("bytes_string = ", bytes_string)
    return bytes_string


# 功能：HEX字符串转ASCII字符串（单词、句子）（有非ASCII转换异常）
# HEX字符串转字节串（单词或者句子）
# 例："48656c6c6f" ==> "hello"
# 字符串 >> 二进制 >> hex >> hex 字符串 
# 输入：字符串，HEX十六进制（长度无限制：''）.去掉空格
# 输出：ASCII字符串
# def hex_to_str(hex_str):
def HEXStr_to_WORDstr(hex_str):
    bytes_obj = bytes.fromhex(hex_str)
    return bytes_obj.decode('utf-8')


# 功能：HEX字符串转ASCII字符串（单词、句子）（其中有二进制也可以转换，只是为乱码）
# 输入：字符串，HEX十六进制（长度无限制：''）
# 输出：ASCII字符串
# def hexStr_and_hex_to_str(hex_str):
def HEXStr_to_WORDstr3x(hex_str):
    hex = hex_str.encode('utf-8')
    str_bin = binascii.unhexlify(hex)

    # res = str_bin.decode('utf-8')
    res = str(str_bin)
    return res


# HEX字符串转有符号INT
# 输入：4个字节十六进制字符串（8个字符）。小端模式
# 输入：big_or_little:0=小端，1=大端
# 输出：十进制有符号整数
# def hex_to_int_lowendian(hex_str):
def HEXstr_to_INT(hex_str, big_or_little):
    integer = int(hex_str, 16)

    if big_or_little == 0:
        le_int_value = int.from_bytes(integer.to_bytes(4, 'big'), 'little')  # 输入小端
        # print(le_int_value)  # 输出结果将是在小端字节序下0xABCD的整数形式
    else:
        le_int_value = int.from_bytes(integer.to_bytes(4, 'little'), 'little')  # 输入大端

    return le_int_value


# 功能：HEX字符串转有符号FLOAT
# （IEEE754）单精度浮点型，小端在前
# 输入：4个字节十六进制字符串（8个字符）
# 输入：big_or_little:0=小端，1=大端
# 输出：有符号浮点数
# def hex_string_to_float(hex_str):
def HEXstr_to_float(hex_str, big_or_little):
    # 将十六进制字符串转换为字节序列
    byte_seq = bytes.fromhex(hex_str)
    
    # 使用struct解包字节序列为浮点数
    if big_or_little == 0:
        float_num = struct.unpack('<f', byte_seq)[0]  # 小端
    else:
        float_num = struct.unpack('>f', byte_seq)[0]  # 大端

    return float_num


# 功能：BIN转HEX字符串
# 例：（uart驱动读取二进制串）b'AB25CD36EF58' ==> （十六进制字节串，可以进行切片和分析）'414232354344333645463538'
# 输入：二进制（长度无限制：b''）
# 输入：cmd == 0：不需要空格，cmd == 1：用空格分隔不同字节
# 输出：十六进制字符串，有空格
# def this_hexShow(argv):
def BINbytes_to_HEXstr(argv, cmd):
    try:
        result = ''
        hLen = len(argv)
        for i in range(hLen):
            hvol = argv[i]
            hhex = '%02x' % hvol
            if cmd == 0:
                result += hhex
            else:
                result += hhex+' '

        return result
    except Exception as e:
        print("---异常--1:", e)
        return -1
