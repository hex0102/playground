import random
import numpy as np
#random.seed(37)
NUM_INPUTs = 4
NUM_OUTPUTs = 4
BUFF_DEPTH = 1
MAX_Q_SIZE = 128
SIM_CYCLES = 10000


N_FIFOs = NUM_INPUTs*NUM_OUTPUTs
mInputQ = [[] for i in range(NUM_INPUTs)]
mInternalFIFOs = [[] for i in range(N_FIFOs)]
mLastGranted = [0]*NUM_OUTPUTs

# setup the counters
mReqCounter = [0]*NUM_INPUTs
mReqCounterPerOutput = np.zeros(N_FIFOs)
mFIFOUtil = np.zeros(N_FIFOs)

def round_robin_grant(last_grant_idx, target_id):
    for input_idx in range(last_grant_idx+1, NUM_INPUTs):
        FIFO_idx = NUM_OUTPUTs*input_idx + target_id
        if(len(mInternalFIFOs[FIFO_idx]) > 0):
            return input_idx
    
    for input_idx in range(0, last_grant_idx + 1):
        FIFO_idx = NUM_OUTPUTs*input_idx + target_id
        if(len(mInternalFIFOs[FIFO_idx]) > 0):     
            return input_idx
    return -1        

for t in range(SIM_CYCLES):
    # tick the mux
    #   step 1: round robin arbitration 
    #   step 2: select and drain 
    for i in range(NUM_OUTPUTs):
        last_grant_idx = mLastGranted[i]
        current_grant_idx = round_robin_grant(last_grant_idx, i)
        #print(last_grant_idx)
        if(current_grant_idx != -1):
            returned_entry = mInternalFIFOs[current_grant_idx*NUM_OUTPUTs + i].pop(0)
            mLastGranted[i] = current_grant_idx
        
    # tick the demux
    for i in range(NUM_INPUTs):
        if(len(mInputQ[i]) != 0):
            incoming_packet = mInputQ[i][0]
            src_id = incoming_packet[0]
            target_id = incoming_packet[1]
            assert i == src_id, "input idx mismatch"
            fifo_id = src_id * NUM_OUTPUTs + target_id
            if(len(mInternalFIFOs[fifo_id]) < BUFF_DEPTH):
                mInternalFIFOs[fifo_id].append(incoming_packet)
                mInputQ[i].pop(0)

    # feed the input
    for i in range(NUM_INPUTs):
        if(len(mInputQ[i]) < MAX_Q_SIZE):
            packet_tuple = (i, random.randint(0, NUM_OUTPUTs-1))
            mInputQ[i].append(packet_tuple)
            mReqCounterPerOutput[i*NUM_OUTPUTs + packet_tuple[1]] += 1
            mReqCounter[i] += 1

    # Measure FIFO utilization
    for i in range(N_FIFOs):
        mFIFOUtil[i]+=len(mInternalFIFOs[i])

print("----Packet Statistics----")
print(mReqCounter)
print(mReqCounterPerOutput)
print("----System Statistics----")
print(mFIFOUtil/(BUFF_DEPTH*SIM_CYCLES))