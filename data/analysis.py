import os, sys
import pandas as pd
import numpy
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib as jl
import load_functions

def construct_features(path, name, pos, neg, hmm_pos, hmm_neg, mutation_position, features, row, obj, mut):
	#df = pd.read_table('/net/netfile2/ag-russell/bq_gsingh/gpcr/update/aln_psiblast/selected_features.txt', sep = '\t', index_col = 0)
	#df = pd.read_table('/net/home.isilon/ag-russell/bq_gsingh/gpcr/systematic/set_no_class_B_no_stringency/selected_features/selected_features.txt', sep = '\t', index_col = 0)
	df = pd.read_csv(path+'/data/selected_features.txt', sep = '\t', index_col = 0)
	map_position = {}
	#for x, y in df[['MSA_Pos', 'Domain_Pos']].as_matrix().tolist():
	for x, y in df[['MSA_Pos', 'Domain_Pos']].values:
		map_position[str(x)] = str(y.replace('(', '|').replace(')', ''))
	#print map_position

	mutation = mut
	dom_position = {}

	for f in features:
		remarks = []

		if 'pos' in f:
			if pos[name].has_key(str(f[:-3])) == True:
				if pos[name][str(f[:-3])]['position'] == mutation_position:
					AA = mutation[-1]
					dom_position[map_position[str(f[:-3])]] = f
				else:
					AA = pos[name][str(f[:-3])]['aa']

				if AA != '-':
					row.append(1)
				else:
					row.append(0)
			else:
				row.append(0)

		elif 'neg' in f:
			if neg[name].has_key(str(f[:-3])) == True:
				if neg[name][str(f[:-3])]['position'] == mutation_position:
					AA = mutation[-1]
					dom_position[map_position[str(f[:-3])]] = f
				else:
					AA = neg[name][str(f[:-3])]['aa']

				if AA != '-':
					row.append(1)
				else:
					row.append(0)
			else:
				row.append(0)

		if 'bip' in f:
			if pos[name].has_key(str(f[:-3])) == True:
				if pos[name][str(f[:-3])]['position'] == mutation_position:
					AA = mutation[-1]
					dom_position[map_position[str(f[:-3])]] = f
				else:
					AA = pos[name][str(f[:-3])]['aa']

				if AA != '-':
					row.append(float(hmm_pos[str(f[:-3])][AA.upper()]))
				else:
					row.append(float(load_functions.find_max_bits(hmm_pos, f)))
			else:
				row.append(float(load_functions.find_max_bits(hmm_pos, f)))

		elif 'bin' in f:
			if neg[name].has_key(str(f[:-3])) == True:
				if neg[name][str(f[:-3])]['position'] == mutation_position:
					AA = mutation[-1]
					dom_position[map_position[str(f[:-3])]] = f
				else:
					AA = neg[name][str(f[:-3])]['aa']

				if AA != '-':
					row.append(float(hmm_neg[str(f[:-3])][AA.upper()]))
				else:
					row.append(float(load_functions.find_max_bits(hmm_neg, f)))
			else:
				row.append(float(load_functions.find_max_bits(hmm_neg, f)))

		elif 'TILL' in f:
			if mutation_position >= obj[name].til_start and mutation_position <= obj[name].til_end:
				sequence = ''
				if obj[name].til != '':
					sequence = list(obj[name].til.replace('-', ''))
					#print sequence, mutation, obj[name].til_start, obj[name].til_end, name, 'til'
					sequence[mutation_position - obj[name].til_start] = mutation[-1]
					sequence = "".join(sequence)
				dom_position['TILL'] = f
			else:
				sequence = obj[name].til
			row.append(len(sequence))

		elif 'CTLL' in f:
			if mutation_position >= obj[name].ctl_start:
				sequence = ''
				if obj[name].ctl != '':
					sequence = list(obj[name].ctl.replace('-', ''))
					#print sequence, mutation, obj[name].ctl_start, name, 'ctl'
					sequence[mutation_position - obj[name].ctl_start] = mutation[-1]
					sequence = "".join(sequence)
				dom_position['CTLL'] = f
			else:
				sequence = obj[name].ctl
			row.append(len(sequence))

		elif '_CTL' in f:
			if mutation_position >= obj[name].ctl_start:
				sequence = ''
				if obj[name].ctl != '':
					sequence = list(obj[name].ctl.replace('-', ''))
					sequence[mutation_position - obj[name].ctl_start] = mutation[-1]
					sequence = "".join(sequence)
					dom_position[f] = f
			else:
				sequence = obj[name].ctl
			row.append(sequence.count(f.split('_')[0]))

		elif '_TIL' in f:
			if mutation_position >= obj[name].til_start and mutation_position <= obj[name].til_end:
				sequence = ''
				if obj[name].til != '':
					sequence = list(obj[name].til.replace('-', ''))
					#print sequence, mutation, obj[name].til_start, obj[name].til_end, name, 'til'
					sequence[mutation_position - obj[name].til_start] = mutation[-1]
					sequence = "".join(sequence)
				dom_position[f] = f
			else:
				sequence = obj[name].til
			row.append(sequence.count(f.split('_')[0]))

	#sys.exit()
	return row, dom_position

def read_aln(path, pos, neg, hmm_pos, hmm_neg, features, gprotein, gpcr, obj):
	data = []
	done_features = []
	AA = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']
	if pos.has_key(gpcr) == True and neg.has_key(gpcr) == True:
		for feature in features:
			if 'bip' in feature or 'bin' in feature:
				#print feature
				if feature[:-3] not in done_features:
					if pos[gpcr].has_key(feature[:-3]) == True and neg[gpcr].has_key(feature[:-3]) == True:
						#print feature
						mutation_position = pos[gpcr][feature[:-3]]['position']
						for mut in AA:
							row = []
							row.append(str(gpcr))
							row.append(feature[:-3])
							row.append(str(mutation_position))
							row.append(str(pos[gpcr][feature[:-3]]['aa']))
							row.append(str(mut))
							row, dom_position = construct_features(path, gpcr, pos, neg, hmm_pos, hmm_neg, mutation_position, features, row, obj, mut)
							'''
							for pi in dom_position:
								if obj[gpcr].mutation[mut]['position'].has_key(pi) == False:
									obj[gpcr].mutation[mut]['position'][pi] = {}
									obj[gpcr].mutation[mut]['position'][pi][dom_position[pi]] = []
									obj[gpcr].mutation[mut]['position'][pi][dom_position[pi]].append(str(gprotein))
								else:
									if obj[gpcr].mutation[mut]['position'][pi].has_key(str(dom_position[pi])) == False:
										obj[gpcr].mutation[mut]['position'][pi][dom_position[pi]] = []
										obj[gpcr].mutation[mut]['position'][pi][dom_position[pi]].append(str(gprotein))
									else:
										obj[gpcr].mutation[mut]['position'][pi][dom_position[pi]].append(str(gprotein))
										obj[gpcr].mutation[mut]['position'][pi][dom_position[pi]] = list(set(obj[gpcr].mutation[mut]['position'][pi][dom_position[pi]]))
							'''
							data.append(row)
					done_features.append(feature[:-3])
	#print numpy.array(data)
	#sys.exit()
	#print numpy.array(data[:, 2:])
	return numpy.array(data)

def extract_model(path, gprotein):
	#for files in os.listdir('/net/netfile2/ag-russell/bq_gsingh/gpcr/update_2/output_VI/'):
	#for files in os.listdir('/net/home.isilon/ag-russell/bq_gsingh/gpcr/systematic/set_no_class_B_no_stringency/output/'):
	for files in os.listdir(path+'/data/output/'):
		if gprotein in files and 'model' in files:
			model = jl.load(files)
			break
	return model

def k_fold(file):
	df = pd.read_csv(file, lineterminator = '\n', sep = '\t')
	col = list(df.columns.values)
	df[col[1:-1]] = df[col[1:-1]].astype(float)
	min_max_scaler_all = MinMaxScaler()
	min_max_scaler_all.fit_transform(df[col[1:-1]])
	return min_max_scaler_all

def main(path, pos, neg, hmm_pos, hmm_neg, features, gprotein, gpcr_list, obj):
	l = 'GPCR\tALN_POS\tSEQ_POS\tWT\tVAR\tPROB\n'
	for gpcr in gpcr_list:
		data = read_aln(path, pos, neg, hmm_pos, hmm_neg, features, gprotein, gpcr, obj)
		#print data[:, 3:]
		feature_matrix = data[:, 5:]
		model = extract_model(path, gprotein)
		#min_max = k_fold('/net/netfile2/ag-russell/bq_gsingh/gpcr/update/feature_files/'+str(gprotein)+'_train.txt')
		#min_max = k_fold('/net/home.isilon/ag-russell/bq_gsingh/gpcr/systematic/set_no_class_B_no_stringency/feature_files/'+str(gprotein)+'_train.txt')
		min_max = k_fold(path+'/data/feature_files/'+str(gprotein)+'_train.txt')
		feature_matrix = min_max.transform(numpy.array(feature_matrix))
		Y = model.predict(feature_matrix)
		Y_prob = model.predict_proba(feature_matrix)

		for (name, aln_position, mut_position, aa, mut), y in zip(data[:, :5], Y_prob):
			#obj[name].mutation[mut][gprotein] = round(y[1], 3)
			#print name, aln_position, mut_position, aa, mut, round(y[1], 3)
			l += str(name) + '\t' + str(aln_position) + '\t' + str(mut_position) + '\t' + str(aa) + '\t' + str(mut) + '\t' + str(round(y[1], 3)) + '\n'

	return l
	#print 'Completed.'
