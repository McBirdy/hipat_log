#!/usr/bin/env python
import subprocess, re, time, datetime, shelve, os
from optparse import OptionParser
from timeout import timeout
from serial import Serial

"""Will be used to log relevant HiPAT output on a machine."""

def filter_ntpq(ntpq_output, ip_address):
    """Filters the ntpq_output and returns a dictionary with the items.
    
    ntpq_output: string containing the raw ntpq output
    ip_address: string containing the ip address to search for in the ntpq_output
    
    returns: regex_results as a regex result, keyword must be used to access fields
    """
    regex = (   '(?P<ip_address>{0})\s+'# ip_address to get info from
                '(?P<refid>\S+)\s+'     # refid 
                '(?P<st>\S+)\s+'        # stratum
                '(?P<t>\S+)\s+'         # type of server
                '(?P<when>\S+)\s+'      # when, time since last update
                '(?P<poll>\S+)\s+'      # poll, how often it is polled
                '(?P<reach>\S+)\s+'     # how reliable the server is
                '(?P<delay>\S+)\s+'     # time in ms to the server
                '(?P<offset>\S+)\s+'    # offset to server in ms
                '(?P<jitter>\S+)\s+'    # jitter of the server
    ).format(ip_address)
    regex_results = re.search(regex, ntpq_output, re.MULTILINE)    # search for the line from the ntpq output
    return regex_results
    
def daily_recording(options):
    """Will perform a daily recording of the ntpq output and calculate the delta drift compared to the previous recording.
    
    options: dict containing the input arguments to the program
    returns: none, only updates the output file
    """
    
    f = open(options.output_name, 'a')  # Output file
    ntpq_output = subprocess.check_output(['ntpq', '-pn'])  # Get ntpq -pn output
    regex_results = filter_ntpq(ntpq_output, options.ip_address)    # filter by ip_address specified in options
    db = shelve.open('/mnt/tmpfs/shelvefile', 'c')  # the shelvefile contains the total number of freq_adj steps
    
    # If a recording has already been performed the last_offset is found in the output file
    # If no recording has been made a new file is created
    f = open(options.output_name, 'r+')
    try:
        last = ''
        for last in f:
            pass
        last_offset = re.search(r'\s([\d\.]+)\s+\S+$', last).group(1)   # Find the last offset in the file
    except AttributeError:
        last_offset = 0
    
    # Calculate the delta_offset between the previous offset - the current offset
    delta_offset = float(regex_results.group('offset')) - float(last_offset)
    timestamp = str(datetime.datetime.now())[:-7]   # Get a timestamp without the milliseconds 
    # Print the results to the output file
    try:
        print_output = "{timestamp} {steps} {offset} {delta_offset}\n".format(timestamp=timestamp, steps=db['freq_adj'][1], offset=regex_results.group('offset'), delta_offset=delta_offset)
    except AttributeError:
        print "Ip address not in <ntpq -pn> query results, please check IP."
        return
    
    f.write(print_output)
    f.close()
    return

    
        
def main():
    """ Opens file, uses filter_ntpq method and writes formatted output to file. Rinse and repeat."""
    parser = OptionParser(version="%prog 1.1")
    parser.add_option("-i", "--ip_address", dest="ip_address", default="158.112.116.8", help="Ip address in ntpq -pn query output to log [158.112.116.8]")
    parser.add_option("-o", "--output_file_name", dest="output_name", default="hipat_log.txt", help="Name of output file [hipat_log.txt]")
    parser.add_option("-n", "--no_confirmation", dest="no_confirmation", default=False, help="Don't show the confirmation dialog [False]")
    (options, args) = parser.parse_args()
    print "Recording {0} in file {1}".format(options.ip_address, os.path.abspath(options.output_name))
    if not options.no_confirmation:
        if (raw_input("Is this OK? [y/n]") == "y"):
            pass
        else:
            return
        
    f = open(options.output_name, 'a')
        
    # A check for total_number_of_lines is performed
    number_of_lines = 0 
    with open(options.output_name) as f:
        number_of_lines = sum(1 for _ in f)
    
    f.close()
    # Initial data collection is performed. 4 initial recordings are needed.
    if number_of_lines < 3:
        daily_recording(options)
        return
    elif number_of_lines == 3:
        daily_recording(options)
        ser = Crtc()
        steps = -200
        status = ser.freq_adj(steps)
        if status == "ACK":
            f = open(options.output_name, 'a')
            f.write("Freq_adj successfull {0} steps adjusted. \n".format(steps))
            f.close()
    elif number_of_lines <= 8:
        daily_recording(options)
    elif number_of_lines == 9:
        offset_before = []
        offset_after = []
        file = open(options.output_name, 'r+')
        for line_number in range(1,9):
            last = file.readline()
            if line_number <=4:
                offset_diff = re.search(r'\s+([\d\.]+)$', last).group(1)
                offset_before.append(float(offset_diff))
                continue
            elif line_number == 5:
                continue
            elif line_number <= 8:
                offset_diff = re.search(r'\s+([\d\.]+)$', last).group(1)
                offset_after.append(float(offset_diff))
                continue
        avg_offset_diff_before = sum(offset_before)/len(offset_before)
        avg_offset_diff_after = sum(offset_after)/len(offset_after)
        file.write("Average diff before: {0} Average diff after: {1}\n".format(avg_offset_diff_before, avg_offset_diff_after))
        file.close()
        
        
            
        
        

ser_buffer = ''
class Crtc():
    
    def __init__(self):
        self.ser = Serial("/dev/ttyU0", 4800, timeout=3)
        self.ser.close()
        
    def send(self, text, response='PSRFTXT,(ACK)'):
        """Function used to write text to the serial port. A response from the CRTC is always expected, and if none is specified it will return 1.
        
        text: text to send.
        response: expected response.
        returns: answer string if OK, 1 if no response was received.
        """
        #first the text is written, one letter at the time
        self.ser.open()
        for letter in text:
            time.sleep(0.3)     #0.3 seconds sleep turns out to be the best
            self.ser.write(letter)
          
        #If response is specified to be None, we skip the receive check
        if response == None:
            self.ser.close()
            return 1
        #then we wait for the response
        try:
            answer = self.receive(response)    
            return answer
        except:
            self.ser.write('1111111111')    #the CRTC can hang while expecting more input
            self.ser.close()
            return 2
            
    @timeout(3) #this function will timeout after 3 seconds
    def receive(self, regex):
        """Function used to extract a received answer from the serial port. User must provide a regex if a certain type of message is to be received.
        If it times out a TimeoutError is raised.
        
        regex: regular expression indicating what message it expects to receive back.
        returns: string of match
        """
        global ser_buffer
        #self.ser.open()    #it is opened by the send process.
        while True:
            ser_buffer = ser_buffer + self.ser.read(self.ser.inWaiting()) #fills the buffer
            if '\n' in ser_buffer:  #if a complete line is received
                lines = ser_buffer.split('\n')
                if lines[-2]:   #Access the complete line
                    match = re.search(regex, lines[-2])
                    if match:   #if regex matches
                        ser_buffer = lines[-1]
                        self.ser.close()
                        return match.group(1)   #return match and exit
                ser_buffer = lines[-1]  #if lines[-2] doesn't exist we keep lines[-1]
                
    def freq_adj(self, steps):
        """Will perform the frequency adjustment. This is a barebones implementation of that found in the crtc.py in the HiPAT program.
    
        steps: number of steps to send to crtc.
        returns: None
        """
        steps = int(round(steps, -1))    #round steps to closest 10
        thousands, rest = divmod(abs(steps), 1000)   #number of thousand steps
        tens, rest = divmod(rest, 10)   #number of ten steps
    
        if steps > 0:  #adjust frequency up
            frequency_adjustment = [[thousands, 'o'],[tens, 'x']]
        elif steps < 0:    #adjust frequency down
            frequency_adjustment = [[thousands, 'i'],[tens, 'z']]
            steps = steps * -1  #negative adjustment was performed
        
        for amount in frequency_adjustment: #first treat thousands, then do tens.
            for step in range(int(amount[0])):  #use send multiple times.
                status = self.send(amount[1])    #amount[1] is the letter to be sent to the crtc.
        
        return status
        
        
        
    
    
        
        
        
    

if __name__ == '__main__':
    main()