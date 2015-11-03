from cowfish import Cowfish

co = Cowfish("http://54.68.9.194:81/api", "yang", "Xqebo0lhbQ_grN8l9ZlEF1rC_bDIsyqfh74pOgwcNzQ",r'/Users/yaoyu/Dropbox/Yaoyu_SOSLab_Research/Aquarium_cytometry/')

job = co.get_job_log(19372)

print job['rows'][0]['submitted_by']

print co.datadir_from(job)
print co.sample_names_from(job)
print co.inducer_additions_from(job)
samples = co.samples_from(co.datadir_from(job))
print co.samples_from(co.datadir_from(job))
gate = co.gate(ploidy=None, only=None)
print co.sample_summary(samples[0],"FL1-A")
print gate
print co.gated_samples_summary(samples, gate, "FL1-A")
print co.cytometry_results(19372, gate, "FL1-A")
print co.cytometry_results_summary([19372,19376])
