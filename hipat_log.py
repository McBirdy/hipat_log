#!/usr/bin/env python
import subprocess, re, time, datetime
from optparse import OptionParser

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
    
        
def main():
    """ Opens file, uses filter_ntpq method and writes formatted output to file. Rinse and repeat."""
    parser = OptionParser(version="%prog 1.0")
    parser.add_option("-i", "--ip_address", dest="ip_address", default="158.112.116.8", help="Ip address in ntpq -pn query output to log [158.112.116.8]")
    parser.add_option("-o", "--output_file_name", dest="output_name", default="hipat_log.txt", help="Name of output file [hipat_log.txt]")
    (options, args) = parser.parse_args()
    print "Recording {0} in file {1}".format(options.ip_address, options.output_name)
    #print "Is this OK? [y/n]"
    if (raw_input("Is this OK? [y/n]") == "y"):
        pass
    else:
        return
    
    
    while True:
        f = open(options.output_name, 'a')
        ntpq_output = subprocess.check_output(['ntpq', '-pn'])
        regex_results = filter_ntpq(ntpq_output, options.ip_address)
        
        timestamp = str(datetime.datetime.now())[:-7]
        try:
            print_output = "{timestamp} {offset} {jitter}\n".format(timestamp=timestamp, offset=regex_results.group('offset'), jitter=regex_results.group('jitter'))
        except AttributeError:
            print "Ip address not in <ntpq -pn> query results, please check IP."
            return
        
        f.write(print_output)
        f.close()
        
        time.sleep(60)
        
        
    

if __name__ == '__main__':
    main()