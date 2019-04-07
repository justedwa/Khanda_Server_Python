# Circumflex Designs 2017
#
#   init_comm(port_name)        Opens named com port and initializes comm
#   end_comm()                  Closes comm port
#
#   output_state(out_on)        If state is < 1 then output is turned off.  Otherwise, it is turned on.
#
#   volts_setpoint_set(volts)   Sets output voltage to volts
#   volts_setpoint_get()        Returns voltage setpoint from power supply
#   volts_meas()                Returns the output voltage measurement from the power supply
#
#   amps_setpoint_set(amps)     Sets output current (limit) to amps
#   volts_setpoint_get()        Returns current setpoint from power supply
#   volts_meas()                Returns the output current measurement from the power supply
#
#   status_get()                Returns the power supply status flags
#

import serial
import time

class PSU_Device:
"""
This is a class for accessing Variable PSU control (TP3005P)

Attributes:
    ser1 (Serial object): serial port of attached PSU device
Methods:
    __init__: Creates PSU object from specified port
    init_comm(port_name):        Opens named com port and initializes comm
    end_comm():                  Closes comm port
    output_state(out_on):        If state is < 1 then output is turned off.  Otherwise, it is turned on.
    volts_setpoint_set(volts):   Sets output voltage to volts
    volts_setpoint_get():        Returns voltage setpoint from power supply
    volts_meas():                Returns the output voltage measurement from the power supply
    amps_setpoint_set(amps):     Sets output current (limit) to amps
    volts_setpoint_get():        Returns current setpoint from power supply
    volts_meas():                Returns the output current measurement from the power supply
    status_get():                Returns the power supply status flags
    
"""
    def __init__(self,PSU_PORT):
        self.ser1 = PSU_PORT

    def output_state(out_on):
        time.sleep(0.05)
        if out_on >= 1:
            cmd = b'OUTPUT1:\\r\\n'
            print("Output On")
        else:
            cmd = b'OUTPUT0\\r\\n'
            print ("Output Off")
        ser1.write(cmd)
        time.sleep(0.05)


    def volts_setpoint_set(volts):
        time.sleep(0.05)
        cmd = b'VSET1:'                      #b'VSET1:07.00\\r\\n'
        cmd = cmd + format(volts, "=05.2F").encode('ascii')
        cmd = cmd + b'\\r\\n'
        ser1.write(cmd)

    def volts_setpoint_get():
        time.sleep(0.05)
        cmd = b'VSET1?\\r\\n'
        ser1.write(cmd)
        line = ser1.readline()
        volts = float(line.decode('utf8'))
        return volts

    def volts_meas():
        time.sleep(0.05)
        cmd = b'VOUT1?\\r\\n'
        ser1.write(cmd)
        line = ser1.readline()
        volts = float(line.decode('utf8'))
        return volts


    def amps_setpoint_set(amps):
        time.sleep(0.05)
        cmd = b'ISET1:'                      #b'ISET1:2.500\\r\\n'
        cmd = cmd + format(amps, "=05.3F").encode('ascii')
        cmd = cmd + b'\\r\\n'
        ser1.write(cmd)


    def amps_setpoint_get():
        time.sleep(0.05)
        cmd = b'ISET1?\\r\\n'
        ser1.write(cmd)
        line = ser1.readline()
        amps = float(line.decode('utf8'))
        return amps

    def amps_meas():
        time.sleep(0.05)
        cmd = b'IOUT1?\\r\\n'
        ser1.write(cmd)
        line = ser1.readline()
        amps = float(line.decode('utf8'))
        return amps


    def status_get():
        time.sleep(0.05)
        cmd = b'STATUS?\\r\\n'
        ser1.write(cmd)
        line = ser1.readline()
        status = int(line.decode('utf8'))
        return status
