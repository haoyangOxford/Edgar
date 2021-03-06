from edgar import *


def main():

	menu_key2 = 'accounting polic'
	menu_key1 = 'notes to'
	search_key = [ 'deliverable arrangement',
			'deliverable revenue arrangement',
			'element arrangement',
			'elements arrangement',
			'vsoe',
			]
	print('search keywords:', ','.join(s for s in search_key) )

	''' load company_filing DataBase '''
	company_list_dir = '/'.join(master_index.index_save_dir.split('/')[0:-2]) + '/'
	company_list_fname = company_list_dir + 'db_company_filing.pkl'
	if os.path.isfile(company_list_fname) == True:
		print('loading master_index from database')
		with open(company_list_fname, "rb") as f:
			company_list_db = pickle.load(f)
	else:
		company_list_db = pd.DataFrame(columns = company_list.columns)

	#company_list = company_list_db[ company_list_db['cik'] == '320193' ]
	#company_list = company_list_db[ company_list_db['accession'] == '0001193125-09-214859' ] 
	#company_list = company_list_db.iloc[-5000:]
	company_list = company_list_db
	#print(company_list)

	''' total number of companies which have Interactive URL'''
	count1 = 0
	''' total number of companies which content the keywords'''
	count2 = 0
	''' initialize the search_result pd dataframe '''
	search_result =  pd.DataFrame(columns = company_list.columns.values)
	search_result['interactive_url'] = ''
	for ii,key in enumerate(search_key):
		search_result[key+'_freq'] = ''
		search_result[key+'_content'] = ''

	''' loop through the company_list and perform keyword search'''
	for i  in range(len(company_list)):
		company = company_list.iloc[i]
		#print(company.cik + '\t' + company.company_name + '\t' + company.date_filed)

		### if interactiveURLXBRL doesn't exist
		if len( company.url_IntActDict ) == 0:
			input_url = company.url_html
			web = webDownloader([], input_url)
			page = web.read() #web.readlines()
			text = remove_tags(page)
			key_freq = []
			content = []
			key_freq, content  = single_search_task0(text, search_key)
			if sum(key_freq)>0: 
				new_entry = company
				for kk, key in enumerate(search_key):
					new_entry[key+'_freq'] = key_freq[kk]
					new_entry[key+'_content'] = content[kk]
				search_result = search_result.append(new_entry, ignore_index=True)
				count2 = count2 + 1
				print(str(count2) +' keyword found '+ company.company_name + '\t' + company.date_filed)

		### if interactiveURLXBRL exists
		else:
			###company.url_IntActDict is a dict converted to string
			### use eval() to convert back to dict
			url_IntActDict = eval(company.url_IntActDict)
			for cat1_key in url_IntActDict.keys():
				for cat2_key in url_IntActDict[cat1_key]:
					if (menu_key1 in cat1_key.lower()) and (menu_key2 in cat2_key.lower()):
						count1 = count1 +1
						#print(company.company_name, cat1_key, cat2_key)
						###read file content from given URL
						input_url = url_IntActDict[cat1_key][cat2_key]
						web = webDownloader([], input_url)
						page = web.read()
						text = remove_tags(page)
						###perform search, returns number of keywords found and content containing keyword
						key_freq = []
						content = []
						key_freq, content  = single_search_task0(text, search_key)

						if sum(key_freq)>0: ### output result if key_word found
							### output result to search_result
							new_entry = company
							new_entry['interactive_url'] = "https://www.sec.gov"+input_url
							for kk, key in enumerate(search_key):
								new_entry[key+'_freq'] = key_freq[kk]
								new_entry[key+'_content'] = content[kk]
							search_result = search_result.append(new_entry, ignore_index=True)
							count2 = count2 + 1
							print(str(count2)+' keyword found '+company.company_name+'\t'+ cat2_key)


	print(count1, count2)

	''' output seaerch_result to file '''
	search_result_fname = '/home/haoyang/Dropbox/JeanHao/Edgar/' + 'search_result_'+ time.strftime("%Y%m%d")+ '.csv'
	search_result = search_result.set_index([range(0,len(search_result))])
	print(search_result)

	search_result.to_csv(search_result_fname, sep='\t',encoding = 'utf-8')
	print('saved to file:', search_result_fname)



def single_search_task0(text, search_key):
	Nline = len(text)
	content = ['' for k in search_key]
	key_freq = np.zeros(len(search_key))
	chunksize = np.uint16(len(text)/20)
	for ii in range(0,len(text),chunksize):
		line = text[ii:(ii+chunksize)]
		for kk, key in enumerate(search_key):
			if key in line.lower():
				key_freq[kk] = key_freq[kk] + 1
				content[kk] = content[kk]  + line + '......' 
	return key_freq, content



if __name__ == '__main__':
	main()
