# -*- coding: utf-8 -*-
"""
Device list
"""

from pyacq import StreamHandler, EmotivMultiSignals


def test1():
    devices = EmotivMultiSignals.get_available_devices()
    if len(devices) > 0:
        for name, info_device in devices.items():
            print name
            print info_device
    else:
        print 'No Devices Found'




if __name__ == '__main__':
    test1()
