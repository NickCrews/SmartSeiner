import time
from RFM69 import Radio, FREQ_915MHZ

from struct import unpack
from binascii import unhexlify

NETWORK_ID = 1
THIS_NODE_ID = 1
OTHER_NODE_ID = 2

def bytes2floats(byte_arr):
    assert len(byte_arr)%4 == 0
    byte_arr = bytearray(byte_arr)
    result = []
    for i in range(0, len(byte_arr), 4):
        f = unpack('<f', byte_arr[i:i+4])[0]
        result.append(f)
    return result

def main():
    with Radio(FREQ_915MHZ,
               THIS_NODE_ID,
               NETWORK_ID,
               isHighPower=False,
               verbose=False) as radio:
        print ("node {} ready!!".format(THIS_NODE_ID))

        #set bitrate to 1.2kbps from library default of 55kbps
        # The minimum RSSI value that gets through goes down,
        # Demonstrating that it is more robust
        radio._writeReg(0x03, 0x68)
        radio._writeReg(0x04, 0x2B)

        # enable pre-amp on receiver, increasing sensitivty and range
        # to verfiy, place Tx and RX in non moving locations, and print RSSI
        # values with this used and without it. There should be a 2-4 dB
        # benefit from using the pre-amp
        # lowpowerlab.com/forum/rf-range-antennas-rfm69-library/rfm69hw-range-test!/
        # radio._writeReg(0x58, 0x2D)

        while True:
            ##print("termp is", radio.read_temperature())
            #regs = radio.read_registers()
            #for addr, data in regs:
            #   print( str(addr) + '\t' + str(data))
            # Every 10 seconds get packets
            # Process packets
            packets = radio.get_packets()
            if packets:
                # print("received a message!!!")
                for packet in packets:
                    print (packet.RSSI, bytes2floats(packet.data))
                # print("no packet received :(")

            # Every 5 seconds send a message
##            if tx_counter > 5:
##                tx_counter=0
##
##                # Send
##                print ("Sending")
##                if radio.send(2, "TEST", attempts=3, waitTime=100):
##                    print ("Acknowledgement received")
##                else:
##                    print ("No Acknowledgement")


            #print("Listening...", len(radio.packets), radio.mode_name)
            delay = .05
            time.sleep(delay)

if __name__ == '__main__':
    main()
