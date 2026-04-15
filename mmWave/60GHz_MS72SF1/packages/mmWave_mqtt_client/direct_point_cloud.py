from mmWave_hardware import *
import time

config = mmWaveConfig()
hardware_interface = mmWaveHardwareInterface(config, mode=1)


from mmwave_visualizer_Qt6 import *


app = QApplication(sys.argv)

window = mmWaveVisualizer()
integrate_with_hardware(window, hardware_interface)   # hardware_interface is your mmWaveHardwareInterface
hardware_interface.start()
window.show()
sys.exit(app.exec_())