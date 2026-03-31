import serial
import serial.tools.list_ports


def DOpenPort(portx, bps, thimeout):
    ser = -1
    try:
        #打开串口，并得到串口对象
        ser = serial.Serial(portx, bps, timeout=thimeout)
        #判断是否打开成功
        if (False == ser.is_open):
            ser = -1
            print("serial open Err")
        else:
            print("serial is ready")
    except Exception as e:
        print("----异常---", e)

    return ser


def DColsePort(ser):
    ser.close()

    print("DColsePort")


def DWritePort(ser, data):
    result = ser.write(data)  # 写data
    return result


def hexShow(argv):
    try:
        result = ''
        hLen = len(argv)
        for i in range(hLen):
            hvol = argv[i]
            hhex = '%02x' % hvol
            result += hhex+' '

        return result
    except Exception as e:
        print("---异常--2:", e)
        return -1


def DReadPort(ser):
    # 循环接收data，可用线程实现
    readstr = ""
    if ser.in_waiting:
        readbuf = ser.read(ser.in_waiting)
        if readbuf[0] == 0x55 and readbuf[1] == 0xaa:
            readstr = readbuf
        else:
            readstr = readstr + readbuf

        hexShow(readstr)


def serial_update(box):
    ports = serial.tools.list_ports.comports()
    update_com = []
    for port in ports:
        print("ports = ", port.device)
        update_com.append(port.device)
    
    box.set("")
    box["values"] = update_com
    if len(update_com) > 0:
        box.current(0)

