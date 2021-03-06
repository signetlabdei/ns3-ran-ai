import sem
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt

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
    
"""
    Read AppStats.txt trace file and return a list containing the 
    parsed values. Can be used as input for the function 
    get_results_as_dataframe provided by sem.
    Args:
        result (str): the content of AppStats.txt as a string
"""
@sem.utils.yields_multiple_results
@sem.utils.output_labels(['start [s]', 'end [s]', 'NodeId', 'nTxBursts', 'TxBytes', 
                          'nRxBursts', 'RxBytes', 'delay [s]', 'stdDev', 'min', 
                          'max', 'avg prr', 'avg throughput [bps]'])
@sem.utils.only_load_some_files(r'.*AppStats.txt')
def read_appStatsTrace (result):    
    data = [] 
    lines = result['output']['AppStats.txt'].splitlines()
    for line in lines [1:]:
        values = line.split ("\t")
        start = float (values [0])
        end = float (values [1])
        nTxBursts = int (values [3]) 
        nRxBursts = int (values [5])
        rxBytes = int (values [6])
        row = [start, # start [s]
               end, # end [s]
               int (values [2]), # NodeId
               nTxBursts, # nTxBursts
               int (values [4]), # TxBytes
               nRxBursts, # nRxBursts
               rxBytes, # RxBytes
               float (values [7])/1e9, # delay [ns]
               float (values [8]), # stdDev
               float (values [9]), # min
               float (values [10]), # max
               nRxBursts / nTxBursts, # avg prr
               rxBytes * 8 / (end - start)] # avg throughput [bps]
        data += [row]
    return data
    
"""
    Read RxPacketTrace.txt trace file, parse it using a sampling time of 100 ms 
    and return a list containing the sampled values. 
    Can be used as input for the function get_results_as_dataframe provided by sem.
    Args:
        result (str): the content of RxPacketTrace.txt as a string
"""
@sem.utils.yields_multiple_results
@sem.utils.output_labels(['Time [s]', 'OFDM symbols', 'Cell ID', 'RNTI', 
                          'CC ID', 'TB size [bytes]', 'MCS', 'SINR [dB]', 'UL/DL'])
@sem.utils.only_load_some_files(r'.*RxPacketTrace.txt')
def sample_rxPacketTrace (result):    
    data = []
    df = pd.read_csv (StringIO (result ['output']['RxPacketTrace.txt']), 
                      delimiter = "\t", index_col=False, 
                      usecols = [0, 1, 6, 7, 8, 9, 10, 11, 13], 
                      names = ['UL/DL', 'Time [s]', 'OFDM symbols', 'Cell ID', 
                               'RNTI', 'CC ID', 'TB size [bytes]', 'MCS', 'SINR [dB]'], 
                      dtype = {'mode' : 'object', 
                               'Time [s]' : 'float', 
                               'OFDM symbols' : 'int', 
                               'Cell ID' : 'int', 
                               'RNTI' : 'int', 
                               'CC ID' : 'int', 
                               'TB size [bytes]' : 'int', 
                               'MCS' : 'int', 
                               'SINR [dB]' : 'float'}, 
                      engine='python', header=0)
    
    grouper = df.groupby (['Cell ID', 'RNTI', 'CC ID', 'UL/DL'])
    sampledDf = pd.DataFrame ()
    for name, group in grouper: 
        group ['Time [s]'] = pd.to_timedelta (group ['Time [s]'], unit='s')
        group.set_index ('Time [s]', inplace=True)
        
        numeric = group.select_dtypes('number').columns
        non_num = group.columns.difference(numeric)
        d = {**{x: 'mean' for x in numeric}, **{x: 'first' for x in non_num}}

        group = group.resample ("100ms").agg (d)
        group.reset_index (inplace=True)
        sampledDf = sampledDf.append (group, ignore_index=True)
    
    return sampledDf.values.tolist ()

"""
    Read RxPacketTrace.txt trace file, parse it using a sampling time of 100 ms 
    and return the number of OFDM symbols used in each time period. 
    Can be used as input for the function get_results_as_dataframe provided by sem.
    Args:
        result (str): the content of RxPacketTrace.txt as a string
"""
@sem.utils.yields_multiple_results
@sem.utils.output_labels(['Time [s]', 'OFDM symbols', 'Cell ID', 'RNTI', 
                          'CC ID'])
@sem.utils.only_load_some_files(r'.*RxPacketTrace.txt')
def calc_ofdm_sym (result):    
    data = []
    df = pd.read_csv (StringIO (result ['output']['RxPacketTrace.txt']), 
                      delimiter = "\t", index_col=False, 
                      usecols = [0, 1, 6, 7, 8, 9], 
                      names = ['UL/DL', 'Time [s]', 'OFDM symbols', 'Cell ID', 
                               'RNTI', 'CC ID'], 
                      dtype = {'mode' : 'object', 
                               'Time [s]' : 'float', 
                               'OFDM symbols' : 'int', 
                               'Cell ID' : 'int', 
                               'RNTI' : 'int', 
                               'CC ID' : 'int'}, 
                      engine='python', header=0)
    
    # Group the results, each group corresponds to a single user
    grouper = df.groupby (['Cell ID', 'RNTI', 'CC ID'])
    sampledDf = pd.DataFrame ()
    
    # For each user, resample the results and compute the number of OFDM symbols
    # that have been used
    for name, group in grouper: 
        group ['Time [s]'] = pd.to_timedelta (group ['Time [s]'], unit='s')
        group.set_index ('Time [s]', inplace=True)
        
        # Resample and aggregate the results using a sampling period of 100 ms
        # In each sampling period, compute the overall number of OFDM symbols 
        # that have been used 
        d = {'OFDM symbols': 'sum', 'Cell ID': 'first', 'RNTI': 'first', 'CC ID': 'first'}
        group = group.resample ("100ms").agg (d)
        group.reset_index (inplace=True)
        sampledDf = sampledDf.append (group, ignore_index=True)
    return sampledDf.values.tolist ()

"""
    Read RanAiStats.txt trace file and return a list containing the 
    parsed values. Can be used as input for the function 
    get_results_as_dataframe provided by sem.
    Args:
        result (str): the content of RanAiStats.txt as a string
"""
@sem.utils.yields_multiple_results
@sem.utils.output_labels(['Time [s]',
                          'IMSI',
                          'MCS',
                          'OFDM symbols',
                          'SINR [dB]',
                          'RLC tx pcks',
                          'RLC tx bytes',
                          'RLC rx pcks',
                          'RLC rx bytes',
                          'RLC avg delay',
                          'RLC std delay',
                          'RLC min delay',
                          'RLC max delay',
                          'PDCP tx pcks',
                          'PDCP tx bytes',
                          'PDCP rx pcks',
                          'PDCP rx bytes',
                          'PDCP avg delay',
                          'PDCP std delay',
                          'PDCP min delay',
                          'PDCP max delay',
                          'APP tx pcks',
                          'APP tx bytes',
                          'APP rx pcks',
                          'APP rx bytes',
                          'APP avg delay',
                          'APP std delay',
                          'APP min delay',
                          'APP max delay'
                          ])
@sem.utils.only_load_some_files(r'.*RanAiStats.txt')
def read_ran_ai(result):
    data = []
    lines = result['output']['RanAiStats.txt'].splitlines()

    for line in lines[1:]:
        values = line.split("\t")
        row = [float(values[0]),
               int(values[1]),
               float(values[2]),
               float(values[3]),
               float(values[4]),
               float(values[5]),
               float(values[6]),
               float(values[7]),
               float(values[8]),
               float(values[9]),
               float(values[10]),
               float(values[11]),
               float(values[12]),
               float(values[13]),
               float(values[14]),
               float(values[15]),
               float(values[16]),
               float(values[17]),
               float(values[18]),
               float(values[19]),
               float(values[20]),
               float(values[21]),
               float(values[22]),
               float(values[23]),
               float(values[24]),
               float(values[25]),
               float(values[26]),
               float(values[27]),
               float(values[28])
               ]
        data += [row]
    return data
