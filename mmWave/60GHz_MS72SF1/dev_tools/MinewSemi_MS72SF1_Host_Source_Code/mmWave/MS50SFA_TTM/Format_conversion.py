from system.sys_data import sys_data2


def get_Signed_integer_from_hex_str(res2):
    res2 = "FF" + res2
    res3 = int(res2, 16)
    original_num = from_twos_complement(res3, 16)

    # print("original_num = ", original_num)
    return original_num
    
def get_combobox_item_count(combobox):
    # 获取下拉列表中的所有元素
    all_items = combobox["values"]
    # 计算元素数量
    item_count = len(all_items)
    print(f"Combobox item count: {item_count}")
    return item_count


def this_hexShow(argv):
    try:
        result = ''
        hLen = len(argv)
        for i in range(hLen):
            hvol = argv[i]
            hhex = '%02x' % hvol
            result += hhex+' '

        return result
    except Exception as e:
        print("---异常--1:", e)
        return -1


def hex_to_str(hex_str):
    bytes_obj = bytes.fromhex(hex_str)
    return bytes_obj.decode('utf-8')

#  1. 字符串转 hex 字符串 
#  字符串 >> 二进制 >> hex >> hex 字符串 
import binascii

def str_to_hexStr(string):
    str_bin = string.encode('utf-8')
    return binascii.hexlify(str_bin).decode('utf-8')

#  2. hex 字符串转字符串 
#  hex 字符串 >> hex >> 二进制 >> 字符串 
import binascii

def hexStr_to_str(hex_str):
    hex = hex_str.encode('utf-8')
    str_bin = binascii.unhexlify(hex)

    res = str_bin.decode('utf-8')
    return res

def hexStr_and_hex_to_str(hex_str):
    hex = hex_str.encode('utf-8')
    str_bin = binascii.unhexlify(hex)

    # res = str_bin.decode('utf-8')
    res = str(str_bin)
    return res


def from_twos_complement(num, bits):
    if num & (1 << (bits - 1)):
        return num - (1 << bits)
    else:
        return num
 