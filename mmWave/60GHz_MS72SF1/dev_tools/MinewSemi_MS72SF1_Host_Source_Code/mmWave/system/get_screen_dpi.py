import ctypes
 
# 定义一些常量
SM_CXSCREEN = 0
SM_CYSCREEN = 1
 
# 获取系统DPI的函数
def get_system_dpi():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    GetDpiForSystem = user32.GetDpiForSystem
    GetDpiForSystem.restype = ctypes.c_uint
    
    try:
        dpi_x = GetDpiForSystem()
        dpi_y = GetDpiForSystem()
    except Exception as e:
        raise Exception('Error retrieving DPI:', e)
    
    return dpi_x
 
# 获取屏幕的实际大小（以像素为单位）
def get_screen_size():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    GetSystemMetrics = user32.GetSystemMetrics
    GetSystemMetrics.restype = ctypes.c_int
    
    width = GetSystemMetrics(SM_CXSCREEN)
    height = GetSystemMetrics(SM_CYSCREEN)
    
    return width, height
 
# 使用示例
# dpi = get_system_dpi()
# print(f'System DPI: {dpi}')
# screen_width, screen_height = get_screen_size()
# print(f'Screen size (pixels): {screen_width} x {screen_height}')
