import base64
import tempfile
import ctypes

import os


# # 打开文件（不存在则创建新文件），选择写入模式
def make_file_name_from_picture_name(image_name):
    
    current_path = os.getcwd()
    print(current_path)

    s1 = image_name.split('\\')
    file_name = s1[len(s1)-1]
    s2 = file_name.split('.')
    module_name = s2[0]

    current_path += "\img\\"
    image_patch = os.path.join(current_path, file_name)
    python_file_name = module_name + ".py"
    python_file_patch = os.path.join(current_path, python_file_name)

    return image_patch, python_file_patch, module_name


# 将ICO文件编码为Base64字符串
def picture_change_to_Base64(Picture_name):
    with open(Picture_name, 'rb') as icon_file:
        encoded_logo = base64.b64encode(icon_file.read()).decode()
    
    return encoded_logo


def write_picture_to_file(encoded_logo, file_name, Variable_name):
    file = open(file_name, "w")
    
    # 写入内容
    file.write(Variable_name + " = " + '"')
    file.write(encoded_logo)
    file.write('"\r\n')
    # 关闭文件
    file.close()

# '.ico'
def Create_file_from_data(encoded_icon_tem, image_type):
    with tempfile.NamedTemporaryFile(suffix=image_type, delete=False) as icon_file:
        icon_file.write(base64.b64decode(encoded_icon_tem))
        icon_path = icon_file.name

    return icon_path


def get_ico():
    Create_file_patch_ico_logo = Create_file_from_data(img.MINEWSEMI_logo_ico_32.MINEWSEMI_logo_ico_32, '.ico')

    return Create_file_patch_ico_logo


def get_logo_img():
    Create_file_patch_logo = Create_file_from_data(img.MINEWSEMI_logo_300.MINEWSEMI_logo_300, '.png')

    return Create_file_patch_logo


def get_product_img():
    Create_file_patch_product = Create_file_from_data(img.MINEWSEMI_product_300.MINEWSEMI_product_300, '.png')

    return Create_file_patch_product


def get_mmWave_map():
    Create_file_patch_mmWave_map = '"' + Create_file_from_data(img.mmWave_map.data, '.png') + '"'

    return Create_file_patch_mmWave_map


import img.MINEWSEMI_logo_ico_32
import img.MINEWSEMI_logo_300
import img.MINEWSEMI_product_300

def meke_python_file_from_image(picture_file_name):
    picture_name, python_name, module = make_file_name_from_picture_name(picture_file_name)
    write_picture_to_file(picture_change_to_Base64(picture_name), python_name, module)


# meke_python_file_from_image("D:\work\itool\mmWave\img\\MINEWSEMI_logo_ico_32.ico")
# meke_python_file_from_image("D:\work\itool\mmWave\img\\MINEWSEMI_logo_300.png")
# meke_python_file_from_image("D:\work\itool\mmWave\img\\MINEWSEMI_product_300.png")

