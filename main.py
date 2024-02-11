# -----------------  BladeRF communication with Python 3.7 ----------------------------------------
# -----------------  Developed by: Farzan Farhangian ----------------------------------------------
# -----------------  Email: farzan.farhangian@lassena.etsmtl.ca -----------------------------------
# ----------------- Based on: https://github.com/Nuand/bladeRF/wiki -------------------------------
import bladerf
import sys
import numpy as np
from scipy.io import loadmat
from bladerf import _bladerf
import argparse
import csv
import struct
import sys
from   pathlib import Path
###############################################################################3
def chunked_read( fobj, chunk_bytes = 4*1024 ):
    while True:
        data = fobj.read(chunk_bytes)
        if( not data ):
            break
        else:
            yield data
###############################################################################
def bin2csv( binfile = None, csvfile = None, chunk_bytes = 4*1024 ):
    with open(binfile, 'rb') as b:
        with open(csvfile, 'w') as c:
            csvwriter = csv.writer(c, delimiter=',')
            count = 0
            for data in chunked_read(b, chunk_bytes = chunk_bytes):
                count += len(data)
                for i in range(0, len(data), 4):
                    sig_i, = struct.unpack('<h', data[i:i+2])
                    sig_q, = struct.unpack('<h', data[i+2:i+4])
                    csvwriter.writerow( [sig_i, sig_q] )
    print( "Processed", str(count//2//2), "samples." )

##################################################################################
d = bladerf.BladeRF()
rx = d.Channel(bladerf.CHANNEL_RX(0))
info=d.get_devinfo()
print(info)
d.set_sample_rate(0, int(2000000))                        # enter your sampling rate in Hz
fs = d.get_sample_rate(0)
print("Sampling rate: {:d} Hz".format(fs))
d.set_frequency(0, int(137500000))                        # enter your center frequency in Hz
f=d.get_frequency(0)
print("Frequency: {:d} Hz".format(f))
#d.get_loopback_modes()
#d.get_rx_mux()
rx.frequency = 137500000  # enter your center frequency in Hz
rx.sample_rate = 2000000  # enter your sampling rate in Hz
rx.gain = 1               # enter your gain
d.sync_config(layout=_bladerf.ChannelLayout.RX_X1,
                  fmt=_bladerf.Format.SC16_Q11,
                  num_buffers=16,
                  buffer_size=8192,
                  num_transfers=8,
                  stream_timeout=3500)
rx.enable = True
bytes_per_sample = 4
buf = bytearray(1024*bytes_per_sample)
num_samples_read = 0
num_samples = 200                 # enter number of samples you want to receive
try:
    while True:
        if num_samples > 0 and num_samples_read == num_samples:
            break
        elif num_samples > 0:
            num = min(len(buf)//bytes_per_sample,
                        num_samples-num_samples_read)
        else:
            num = len(buf)//bytes_per_sample

        # Read into buffer
        d.sync_rx(buf, num)
        num_samples_read += num

        # Write to file
        f= open("samples_bin.bin", "wb")
        f.write(buf[:num*bytes_per_sample])
        f.close()
        d.close()
except KeyboardInterrupt:
    pass
# the bin and csv files will be saved in your directory automatically
bin2csv("samples_bin.bin", "samples_scv.csv", chunk_bytes = 4*1024)