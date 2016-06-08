from cowfish import Cowfish
co = Cowfish("http://aquarium_url/api", "user_name", 'your_api_key',r'/path/to/your_folder')

df_singlets = co.cytometry_results_summary([20454,20472,20475,20476],ploidy="haploid", only='singlets')
print df_singlets
df_all = co.cytometry_results_summary([20454,20472,20475])
print df_all
