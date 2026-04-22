from mmWave_hardware import *
import time

config = mmWaveConfig()
hardware_interface = mmWaveHardwareInterface(config)


from mmwave_visualizer_Qt6 import *


app = QApplication(sys.argv)

window = mmWaveVisualizer(is_ceiling=False)
integrate_with_hardware(window, hardware_interface)   # hardware_interface is your mmWaveHardwareInterface
hardware_interface.start()
window.show()
sys.exit(app.exec())