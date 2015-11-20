from cowfish import Cowfish
co = Cowfish("http://54.68.9.194:81/api", "yang", "Xqebo0lhbQ_grN8l9ZlEF1rC_bDIsyqfh74pOgwcNzQ",r'/Users/yaoyu/Dropbox/Yaoyu_SOSLab_Research/Aquarium_cytometry/')

df_singlets = co.cytometry_results_summary([20454,20472,20475,20476],ploidy="haploid", only='singlets')
print df_singlets
df_all = co.cytometry_results_summary([20454,20472,20475])
print df_all
