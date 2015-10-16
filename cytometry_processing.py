# Goal of this script is to process cytometry results, add strain name and inducer conditions to each well.
from aquarium import AquariumAPI
from FlowCytometryTools import FCPlate
from FlowCytometryTools import FCMeasurement
from FlowCytometryTools import ThresholdGate, PolyGate
import os, FlowCytometryTools
from pylab import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import zipfile

# the directory where you download all the cytometry data zip file
masterdir = r'/Users/yaoyu/Dropbox/Yaoyu_SOSLab_Research/Aquarium_cytometry/'

# API related url and authentication info
# url = 'http://54.68.9.194:81/api' #port 81 for production
api = AquariumAPI("http://54.68.9.194:81/api", "yang", "Xqebo0lhbQ_grN8l9ZlEF1rC_bDIsyqfh74pOgwcNzQ")

# yeast gate info
yeast_gate = PolyGate([(4e5, 1e4), (1e7, 1e4), (1e7, 23e5), (4e5, 6e4)], ('FSC-A', 'SSC-A'), region='in', name='poly gate')
haploid_singlet_gate = PolyGate([(5e5, 8e5), (0.8e6, 1.05e6), (1.15e6, 1.5e6), (1e6, 1.8e6), (5e5, 1e6)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')
haploid_doublet_gate = PolyGate([(6.5e5, 5.75e5), (1.15e6, 9e5), (1.5e6,1.3e6), (1.4e6, 1.4e6), (1.2e6, 1.5e6), (5e5, 5e5)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')
diploid_singlet_gate = PolyGate([(7.5e5, 9e5), (13e5, 16e5), (18e5, 26e5), (15e5, 30e5), (6e5, 15e5)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')
diploid_doublet_gate = PolyGate([(10e5, 8e5), (17e5, 12.5e5), (23e5,17e5), (22e5, 20e5), (20e5, 22e5), (8e5, 8.5e5)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')


def sample_ids(sample_names):
    sample_ids = []
    for sample_name in sample_names:
        sample = api.find('sample', { 'sample': {'name': sample_name} } )
        sample_ids.append(sample['rows'][0]['id'])
    return sample_ids

def short_names(sample_names):
    short_names = []
    for sample_name in sample_names:
        short_name = []
        if len(sample_name.split(', ')) > 1:
            for name in sample_name.split(', '):
                subname = name.split(' ')[0]
                short_name.append('-'.join(subname.split('-')[1:]))
            short_names.append(', '.join(short_name))
        else:
            short_names.append(sample_name)
    return short_names

def sample_summary(sample, channel):
    data = sample.data
    fl_mean = data[channel].mean()
    fl_median = data[channel].median()
    fl_sd = data[channel].median()
    events = sample.shape[0]
    vol = int(sample.meta['$VOL'])/1000.0
    conc = events/vol
    atime = int(sample.meta['#ACQUISITIONTIMEMILLI'])/1000.0
    time_index = pd.DatetimeIndex([sample.meta['$DATE'] + ' ' + sample.meta['$BTIM'][0:-3]], dtype='datetime64[ns]')
    well_name = sample.meta['$FIL'][0:-4]
    df = pd.DataFrame({ 'fl_mean': fl_mean,
                        'fl_median': fl_median,
                        'fl_sd': fl_sd,
                        'events': events,
                        'vol': vol,
                        'conc': conc,
                        'atime': atime,
                        'well_name': well_name}, index = time_index)
    return df

def gated_samples_summary(samples, gate, channel):
    df = pd.DataFrame()
    for sample in samples:
        gated_sample = sample.gate(gate)
        df = df.append(sample_summary(gated_sample, channel))
    return df

# return data frame for job_ids
def data_summary(job_ids, ploidy=None, only=None, channel="FL1-A"):
    yeast_app_gate = gate(ploidy=ploidy, only=only)
    df = pd.DataFrame()
    for job_id in job_ids:
        df = df.append(data_gate_processing(job_id, yeast_app_gate, channel))
    return df.sort_index()

# return which gate to use in data processing
def gate(ploidy=None, only=None):
    yeast_app_gate = None
    if ploidy == "haploid":
        if only == None:
            yeast_app_gate = yeast_gate
        elif only == "singlets":
            yeast_app_gate = yeast_gate & haploid_singlet_gate
        elif only == "doublets":
            yeast_app_gate = yeast_gate & haploid_doublet_gate
        else:
            print "only needs to be singlets or doublets or None"
    elif ploidy == "diploid":
        if only == None:
            yeast_app_gate = yeast_gate
        elif only == "singlets":
            yeast_app_gate = yeast_gate & diploid_singlet_gate
        elif only == "doublets":
            yeast_app_gate = yeast_gate & diploid_doublet_gate
        else:
            print "only needs to be singlets or doublets or None"
    return yeast_app_gate

def samples_from(datadir):
    samples = []
    for filename in os.listdir(datadir):
        if filename.endswith(".fcs"):
            filename = datadir + '/' + filename
            samples.append(FCMeasurement(ID=filename, datafile=filename))
    return samples

# return job_log for job_id
def job_log(job_id):
    job = api.find('job', { "id": job_id })
    return job

# unzip data and return datadir
def datadir_from_job(job):
    file_name = job['rows'][0]['backtrace'][-5]['content'][-1]['upload']['var']
    with zipfile.ZipFile(masterdir + file_name + '.zip', "r") as z:
        z.extractall(masterdir)
    file_path = z.infolist()[0].filename.split('/')[0]
    datadir = masterdir + file_path
    return datadir

# return sample_names parsed from job log
def sample_names_from(job):
    sample_names = []
    if 'transfer' in job['rows'][0]['backtrace'][7]['content'][1]:
        content = job['rows'][0]['backtrace'][7]['content'][1]
    elif 'transfer' in job['rows'][0]['backtrace'][9]['content'][1]:
        content = job['rows'][0]['backtrace'][9]['content'][1]
    for step in content['transfer']['routing']:
        sample_names.append(step['sample_name'])
    return sample_names

# return inducer_additions from job log
def inducer_additions_from(job):
    inducer_additions = None
    if 'inducer_additions' in  job['rows'][0]['backtrace'][0]['arguments']['io_hash']:
        inducer_additions = job['rows'][0]['backtrace'][0]['arguments']['io_hash']['inducer_additions']
    return inducer_additions

# a function to return dataframe from job_id data with gate and channel
def data_gate_processing(job_id, gate, channel):
    job = job_log(job_id)
    sample_names = sample_names_from(job)
    inducer_additions = inducer_additions_from(job)
    samples = samples_from(datadir_from_job(job))
    df = gated_samples_summary(samples, gate, channel)
    df['sample_name'] = pd.Series(short_names(sample_names), index=df.index)
    if inducer_additions == None:
        inducer_additions = [None] * df.shape[0]
    try:
        df['treatment'] = pd.Series(inducer_additions, index=df.index)
    except ValueError:
        print 'valueError'
    df['job_id'] = pd.Series([job_id] * df.shape[0], index=df.index)
    df['sample_id'] = pd.Series(sample_ids(sample_names), index=df.index)
    return df
#
# df = data_gate_processing(17900, yeast_gate, 'FL1-A')
# dfs = data_summary([17900,17896,17959],ploidy="haploid", only='singlets')

# # give an example plot of gating
# sample = samples[0]
# gated_sample = sample.gate(yeast_gate)
# gated_sample.plot(('FSC-A', 'FSC-H'), gates=[yeast_gate], kind='scatter', color='red', alpha=0.9);
