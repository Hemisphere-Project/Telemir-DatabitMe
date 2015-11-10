# -*- coding: utf-8 -*-
"""
Transmit Stream Example
"""

from pyacq import StreamHandler, FakeMultiSignals
from TeleMir.analyses import TransmitFeatures

import zmq
import msgpack
import time
import multiprocessing as mp

def test_recv_loop(port, stop_recv):
    print 'start receiver loop' , port
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE,'')
    socket.connect("tcp://localhost:{}".format(port))
    while stop_recv.value==0:
        message = socket.recv()
        pos = msgpack.loads(message)
        print 'On port {} read pos is {}'.format(port, pos)
    print 'stop receiver'



def run_test():
    streamhandler = StreamHandler()
    
    ## Configure and start acquisition stream
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure( #name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =128.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    dev.initialize()
    dev.start()
    
    ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure( name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 21,
                                nb_pts = 128,
                                sampling_rate =62.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0])  # Could take multistreams ?
    fout.start()
    
    
    ## Create and starts recevers with multuprocessing for stream in and stream out
    stream_in = dev.streams[0]
    stream_out = fout.streams[0]
    stop_recv = mp.Value('i', 0)
    process_in = mp.Process(target= test_recv_loop, args = (stream_in['port'],stop_recv))
    process_out = mp.Process(target= test_recv_loop, args = (stream_out['port'],stop_recv))

    process_in.start()
    process_out.start()
    
    
    time.sleep(0.5)
    stop_recv.value = 1
    
    ## Stop and release devices
    fout.stop()
    fout.close()   
    dev.stop()
    dev.close()
    print 'fout and dev devises closed'
    
    process_in.join(1)  # join method blocante
    print 'process in clear'
    process_out.join(1)
    print 'process out clear'



if __name__ == '__main__':
    run_test()
