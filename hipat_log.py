#!/usr/bin/python
import subprocess, re, time, datetime
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
    
    while True:
        f = open('hipat_log.txt', 'a')
        ntpq_output = subprocess.check_output(['ntpq', '-pn'])
        regex_results = filter_ntpq(ntpq_output, "17.72.148.52")
        
        timestamp = str(datetime.datetime.now())[:-7]
        print_output = "{timestamp} {offset} {jitter}\n".format(timestamp=timestamp, offset=regex_results.group('offset'), jitter=regex_results.group('jitter'))
        
        f.write(print_output)
        f.close()
        
        time.sleep(60)
        
        
    

if __name__ == '__main__':
    main()