#!/usr/bin/env python
import os
import json
import pandas
import shutil
import atomman.lammps as lmp


config_lst, file_name_lst, name_lst, species_lst = [], [], [], []
potential_folder = 'NISTiprpy'
pyiron_pot_path = 'pyiron-resources/lammps/potentials/'
prev_data_frame = pandas.read_csv(os.path.join(pyiron_pot_path, 'potentials_lammps.csv'))
for f in os.listdir(potential_folder): 
    if '.json' in f: 
        with open(os.path.join(potential_folder, f), 'r') as potfile: 
            pot_json = potfile.readlines()
        try:
            pot_json_str = ''.join(pot_json)
            potential = lmp.Potential(pot_json_str)
            if potential.id not in prev_data_frame['Name']:
                potential.load(pot_json_str, pot_dir=potential_folder)
                config_lst.append([l + '\n' for l in potential.pair_info().replace('NISTiprpy/', '').split('\n') 
                                   if any([s in l for s in ['pair_style', 'pair_coeff']])])
                species_lst.append(potential.symbols)
                pot_spec_folder = os.path.join(potential_folder, os.path.splitext(f)[0])
                file_name_lst.append([os.path.join(pot_spec_folder, pot) 
                                      for pot in os.listdir(pot_spec_folder)])
                name_lst.append(potential.id)
                print(f, ' added')
        except json.decoder.JSONDecodeError:
            print(f, ' failed')

model_lst = ['NISTiprpy'] * len(name_lst)
new_data_frame = pandas.DataFrame({'Config': config_lst, 
                                   'Filename': file_name_lst, 
                                   'Model': model_lst, 
                                   'Name': name_lst, 
                                   'Species': species_lst})
merged_data_frame = pandas.concat([prev_data_frame, new_data_frame], sort=False).reset_index(drop=True)
merged_data_frame = merged_data_frame.loc[:, ~merged_data_frame.columns.str.contains('^Unnamed')]
merged_data_frame.to_csv(os.path.join(pyiron_pot_path, 'potentials_lammps.csv'))
os.makedirs('pyiron-resources/lammps/potentials/' + potential_folder, exist_ok=True)
for filelst in file_name_lst:
    for f in filelst: 
        os.makedirs(os.path.dirname(os.path.join(pyiron_pot_path, f)), exist_ok=True)
        shutil.copy(f, os.path.join(pyiron_pot_path, f))
