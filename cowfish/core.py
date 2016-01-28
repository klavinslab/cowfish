from aquariumapi import AquariumAPI
import zipfile
import pandas as pd
from FlowCytometryTools import FCMeasurement
from FlowCytometryTools import ThresholdGate, PolyGate
import os
import urllib

# Goal is to create an Aquarium cytometry results processing package
# Cowfish is to provide a collection of useful methods for processing Aquarium cytometry results

class Cowfish(object):
    def __init__(self, url, login, key, directory_path):
        self.url = url
        self.login = login
        self.key = key
        self.directory_path = directory_path

    # return pandas dataframe for job_ids
    # def summary(job_ids, ploidy=None, only=None, channel="FL1-A"):

    # return job log as job for job_id
    def get_job_log(self, job_id):
        api = AquariumAPI(self.url, self.login, self.key)
        job = api.find('job', { "id": job_id })
        return job

    def download_from(self, job, zipfile_path):
        """Download cytometry results zip file from job"""
        api = AquariumAPI(self.url, self.login, self.key)
        file_id = job['rows'][0]['backtrace'][-1]['rval']['io_hash']['results'][0]['id']
        file_url = api.find('url_for_upload', {'id': file_id})['rows'][0]
        file_url = api.url.strip('/api') + file_url
        urllib.urlretrieve(file_url, zipfile_path)

    def datadir_from(self, job):
        """Unzip downloaded data file in directory_path and return unzipped file datadir"""
        file_name = job['rows'][0]['backtrace'][-5]['content'][-1]['upload']['var']
        zipfile_path = self.directory_path + file_name + '.zip'
        unzipfile_path = self.directory_path + file_name
        if not os.path.exists(zipfile_path):
            self.download_from(job, zipfile_path)
        with zipfile.ZipFile(zipfile_path, "r") as z:
            z.extractall(self.directory_path)
        file_path = z.infolist()[0].filename.split('/')[0]
        datadir = self.directory_path + file_path
        return datadir

    # return sample_names parsed from job log
    def sample_names_from(self, job):
        sample_names = []
        if 'transfer' in job['rows'][0]['backtrace'][7]['content'][1]:
            content = job['rows'][0]['backtrace'][7]['content'][1]
        elif 'transfer' in job['rows'][0]['backtrace'][9]['content'][1]:
            content = job['rows'][0]['backtrace'][9]['content'][1]
        for step in content['transfer']['routing']:
            sample_names.append(step['sample_name'])
        return sample_names

    # return inducer_additions from job log
    def inducer_additions_from(self, job):
        inducer_additions = [None]
        if 'inducer_additions' in  job['rows'][0]['backtrace'][0]['arguments']['io_hash']:
            inducer_additions = job['rows'][0]['backtrace'][0]['arguments']['io_hash']['inducer_additions']
        return inducer_additions


    # a method to process all fcs files in a datadir and return an array of FCMeasurement objects
    def samples_from(self, datadir):
        samples = []
        for filename in os.listdir(datadir):
            if filename.endswith(".fcs"):
                filename = datadir + '/' + filename
                samples.append(FCMeasurement(ID=filename, datafile=filename))
        return samples

    # return pandas dataframe from FCMeasurement object
    # first_sample_time is to record the first sample time in the job
    def sample_summary(self, sample, channel, first_sample_date_time):
        data = sample.data
        fl_mean = data[channel].mean()
        fl_median = data[channel].median()
        fl_sd = data[channel].median()
        events = sample.shape[0]
        vol = int(sample.meta['$VOL'])/1000.0
        conc = events/vol
        atime = int(sample.meta['#ACQUISITIONTIMEMILLI'])/1000.0
        time_index = pd.DatetimeIndex([sample.meta['$DATE'] + ' ' + sample.meta['$BTIM'][0:-3]], dtype='datetime64[ns]')
        if time_index < first_sample_date_time:
            time_index = time_index + pd.DateOffset(1)
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

    # return which gate to use in data processing
    def gate(self, ploidy=None, only=None):
        # yeast gate info
        yeast_gate = PolyGate([(4e5, 1e4), (1e7, 1e4), (1e7, 23e5), (4e5, 6e4)], ('FSC-A', 'SSC-A'), region='in', name='poly gate')
        haploid_singlet_gate = PolyGate([(5e5, 8e5), (0.8e6, 1.05e6), (1.15e6, 1.5e6), (1e6, 1.8e6), (5e5, 1e6)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')
        haploid_doublet_gate = PolyGate([(6.5e5, 5.75e5), (1.15e6, 9e5), (1.5e6,1.3e6), (1.4e6, 1.4e6), (1.2e6, 1.5e6), (5e5, 5e5)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')
        diploid_singlet_gate = PolyGate([(7.5e5, 9e5), (13e5, 16e5), (18e5, 26e5), (15e5, 30e5), (6e5, 15e5)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')
        diploid_doublet_gate = PolyGate([(10e5, 8e5), (17e5, 12.5e5), (23e5,17e5), (22e5, 20e5), (20e5, 22e5), (8e5, 8.5e5)], ('FSC-A', 'FSC-H'), region='in', name='poly gate')
        yeast_app_gate = yeast_gate
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

    def gated_samples_summary(self, samples, gate, channel):
        df = pd.DataFrame()
        first_sample_date_time = pd.DatetimeIndex([samples[0].meta['$DATE'] + ' ' + samples[0].meta['$BTIM'][0:-3]], dtype='datetime64[ns]')
        for sample in samples:
            gated_sample = sample.gate(gate)
            df = df.append(self.sample_summary(gated_sample, channel, first_sample_date_time))
        return df

    def sample_ids(self, sample_names):
        api = AquariumAPI(self.url, self.login, self.key)
        sample_ids = []
        for sample_name in sample_names:
            sample = api.find('sample', { 'sample': {'name': sample_name} } )
            sample_ids.append(sample['rows'][0]['id'])
        return sample_ids

    def short_names(self, sample_names):
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

    # a method to return pandas dataframe from job_id data with gate and channel
    def cytometry_results(self, job_id, gate, channel):
        job = self.get_job_log(job_id)
        sample_names = self.sample_names_from(job)
        inducer_additions = self.inducer_additions_from(job)
        samples = self.samples_from(self.datadir_from(job))
        df = self.gated_samples_summary(samples, gate, channel)
        df['sample_name'] = pd.Series(self.short_names(sample_names), index=df.index)
        if len(inducer_additions) < len(samples):
            inducer_additions += [None] * (len(samples) - len(inducer_additions))
        if inducer_additions == None:
            inducer_additions = [None] * df.shape[0]
        try:
            df['treatment'] = pd.Series(inducer_additions, index=df.index)
        except ValueError:
            print 'valueError'
        df['job_id'] = pd.Series([job_id] * df.shape[0], index=df.index)
        df['sample_id'] = pd.Series(self.sample_ids(sample_names), index=df.index)
        return df

    # return data frame for a list of job_ids
    def cytometry_results_summary(self, job_ids, ploidy=None, only=None, channel="FL1-A"):
        yeast_app_gate = self.gate(ploidy=ploidy, only=only)
        df = pd.DataFrame()
        for job_id in job_ids:
            df = df.append(self.cytometry_results(job_id, yeast_app_gate, channel))
        df['time'] = (df.index - df.index.min()).astype('timedelta64[s]')/3600.0
        return df.sort_index()
