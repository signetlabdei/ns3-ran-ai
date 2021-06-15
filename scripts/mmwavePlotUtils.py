import sem

"""
    Read RxPacketTrace.txt trace file and return a list containing the 
    parsed values. Can be used as input for the function 
    get_results_as_dataframe provided by sem.
    Args:
        result (str): the content of RxPacketTrace.txt as a string
"""
@sem.utils.yields_multiple_results
@sem.utils.output_labels(['UL/DL', 'Time [s]', 'OFDM symbols', 'Cell ID', 'RNTI', 
                          'CC ID', 'TB size [bytes]', 'MCS', 'SINR [dB]'])
@sem.utils.only_load_some_files(r'.*RxPacketTrace.txt')
def read_rxPacketTrace (result):    
    data = [] 
    lines = result['output']['RxPacketTrace.txt'].splitlines()
    for line in lines [1:]:
        values = line.split ("\t")
        row = [values [0], # mode (UL/DL)
               float (values [1]), # Time [s]
               int (values [6]), # OFDM symbols
               int (values [7]), # Cell ID
               int (values [8]), # RNTI
               int (values [9]), # CC ID
               int (values [10]), # TB size [bytes]
               int (values [11]), # MCS
               float (values [13])] # SINR [dB]
        data += [row]
    return data

def read_pdcpAndRlcStats (values):
    start = float (values [0])
    end = float (values [1])
    numTxPdus = int (values [6])
    txBytes = int (values [7])
    numRxPdus = int (values [8])
    rxBytes = int (values [9])
    
    
    row = [start, # start [s]
           end, # end [s]
           int (values [2]), # Cell ID
           int (values [3]), # IMSI
           int (values [4]), # RNTI
           int (values [5]), # LCID
           int (values [6]), # num tx PDUs
           txBytes, # tx bytes
           int (values [8]), # num rx PDUs
           rxBytes, # rx bytes
           float (values [10]), # delay [s]
           float (values [11]), # delay std dev
           float (values [12]), # delay min
           float (values [13]), # delay max
           txBytes * 8 / (end - start), # avg goodput [bps]
           rxBytes * 8 / (end - start), # avg throughput [bps]
           numRxPdus / numTxPdus # avg prr
          ]
    return row

pdcpAndRlcLabels = ['start [s]', 'end [s]', 'Cell ID', 'IMSI', 'RNTI', 
                   'LCID', 'num tx PDUs', 'tx bytes', 'num rx PDUs', 
                   'rx bytes', 'delay [s]', 'delay std dev', 'delay min',
                   'delay max', 'avg goodput [bps]', 'avg throughput [bps]', 
                   'avg prr']
                   
"""
    Read DlPdcpStats.txt trace file and return a list containing the 
    parsed values. Can be used as input for the function 
    get_results_as_dataframe provided by sem.
    Note: this function works only if the trace file contains aggregated 
          statistics, ensure that the attribute 
          ns3::MmWaveBearerStatsCalculator::AggregatedStats is set to True
    Args:
        result (str): the content of DlPdcpStats.txt as a string
"""    
@sem.utils.yields_multiple_results
@sem.utils.output_labels(pdcpAndRlcLabels)
@sem.utils.only_load_some_files(r'.*DlPdcpStats.txt')
def read_dlPdcpStatsTrace (result):    
    data = [] 
    lines = result['output']['DlPdcpStats.txt'].splitlines()
    for line in lines [1:]:
        values = line.split ("\t")
        row = read_pdcpAndRlcStats (values)
        data += [row]
    return data

"""
    Read UlPdcpStats.txt trace file and return a list containing the 
    parsed values. Can be used as input for the function 
    get_results_as_dataframe provided by sem.
    Note: this function works only if the trace file contains aggregated 
          statistics, ensure that the attribute 
          ns3::MmWaveBearerStatsCalculator::AggregatedStats is set to True
    Args:
        result (str): the content of UlPdcpStats.txt as a string
"""    
@sem.utils.yields_multiple_results
@sem.utils.output_labels(pdcpAndRlcLabels)
@sem.utils.only_load_some_files(r'.*UlPdcpStats.txt')
def read_ulPdcpStatsTrace (result):    
    data = [] 
    lines = result['output']['UlPdcpStats.txt'].splitlines()
    for line in lines [1:]:
        values = line.split ("\t")
        row = read_pdcpAndRlcStats (values)
        data += [row]
    return data

"""
    Read DlRlcStats.txt trace file and return a list containing the 
    parsed values. Can be used as input for the function 
    get_results_as_dataframe provided by sem.
    Note: this function works only if the trace file contains aggregated 
          statistics, ensure that the attribute 
          ns3::MmWaveBearerStatsCalculator::AggregatedStats is set to True
    Args:
        result (str): the content of DlRlcStats.txt as a string
"""    
@sem.utils.yields_multiple_results
@sem.utils.output_labels(pdcpAndRlcLabels)
@sem.utils.only_load_some_files(r'.*DlRlcStats.txt')
def read_dlRlcStatsTrace (result):    
    data = [] 
    lines = result['output']['DlRlcStats.txt'].splitlines()
    for line in lines [1:]:
        values = line.split ("\t")
        row = read_pdcpAndRlcStats (values)
        data += [row]
    return data

"""
    Read UlRlcStats.txt trace file and return a list containing the 
    parsed values. Can be used as input for the function 
    get_results_as_dataframe provided by sem.
    Note: this function works only if the trace file contains aggregated 
          statistics, ensure that the attribute 
          ns3::MmWaveBearerStatsCalculator::AggregatedStats is set to True
    Args:
        result (str): the content of UlRlcStats.txt as a string
"""    
@sem.utils.yields_multiple_results
@sem.utils.output_labels(pdcpAndRlcLabels)
@sem.utils.only_load_some_files(r'.*UlRlcStats.txt')
def read_ulRlcStatsTrace (result):    
    data = [] 
    lines = result['output']['UlRlcStats.txt'].splitlines()
    for line in lines [1:]:
        values = line.split ("\t")
        row = read_pdcpAndRlcStats (values)
        data += [row]
    return data
