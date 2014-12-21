import numpy
from obspy.core import Trace,Stream,UTCDateTime
import Queue
from threading import Thread

from Adafruit_ADS1x15 import ADS1x15
sps = 16        #samples per second
adc = ADS1x15(ic=0x01)  #create class identifing model used

#this is how after how many samples a block is saved
block_length=128

#iterator for writing files
block_id=0

#this is needed for saving in mseed so must be passed globably 
global starttime
global block_id

#define the queue from the function queue in the library queue
q = Queue.Queue()


def read_data(block_length):
	starttime=UTCDateTime()
	for x in range (block_length):
		
		#loop continues for block length
	        sample = adc.readADCDifferential23(256, sps)*1000
		
		#'timenow' not essential at the moment and isn't stored
	       	timenow=UTCDateTime()
	       	print sample,timenow
		q.put(sample)



#this is the worker thread
def save_data():
	while True:
		if q.qsize() >= block_length:
			data=numpy.zeros([block_length],dtype=numpy.int16)

			for x in range (block_length):	
				sample = q.get()
				data[x]=sample
				q.task_done()
			
			stats = {'network': 'UK', 'station': 'PHYS', 'location': '00',
	        		 'channel': 'BHZ', 'npts': block_length, 'sampling_rate': 20,
			         'mseed': {'dataquality': 'D'},'starttime': starttime}
			
			stream =Stream([Trace(data=data, header=stats)])
			stream.write('mseed/MSEED' + str(block_id) + '.mseed',format='MSEED',encoding='INT16',reclen=512)
			block_id += 1



thread = Thread(target=save_data)
thread.start()

for x in range(5):
	read_data(block_length)
