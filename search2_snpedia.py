import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from mwclient import client
from mwclient import page

def file_read(file_name):
    rsid_list = dict()
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in read_csv:
            if 'rs' in str(row):
                rsid_list[row[0]] = row[3]
    return rsid_list

def search_snpedia(snp):
    result_output = {}
    try:
        site = client.Site('bots.snpedia.com', path='/', retry_timeout = 10)
    except Exception as exc:
        print ("exc 502", exc)
        snp_page = "connection issue"
    else:
        pagehandle = page.Page(site,snp)
        snp_page = pagehandle.text()
    if snp_page != '':
        result_output[snp] = snp_page
    return result_output

def process_executor(snp_list, count):
    result_output = {}
    snp_list_retry = []
    with ProcessPoolExecutor(max_workers=30) as executor:
        processes = executor.map(search_snpedia, snp_list)
        for data in processes:            
            if data:
                print (data)
                if list(data.values())[0] == "connection issue":
                    snp_list_retry.append(list(data.keys())[0])
                else:
                    result_output.update(data)
            count += 1
            print (count)
    return result_output, snp_list_retry, count

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snp_file', type=str, help='Please provide your DNA SNP file')
    args = parser.parse_args()

    file = file_read(args.snp_file)

    snp_list = []
    count = 0
    result_output = {}
    final_result_output = {}

    for rsid, geno in file.items():
        snp_id = str(rsid) + "(" + str(geno)[:1] + ";" + str(geno)[1:] + ")"
        snp_list.append(snp_id)
    
    result_output, snp_list_retry, count = process_executor(snp_list, count)
    final_result_output = result_output
    count_before_retry = count

    while snp_list_retry:
        print ("list to retry is:")
        print (snp_list_retry)
        result_output = {}
        result_output, snp_list_retry, count = process_executor(snp_list_retry, count)
        final_result_output.update(result_output)


    print ("SumUp:")
    print (final_result_output)
    print ("Count before retry is: ", count_before_retry)
    print ("Final count is: ", count)
    
    json_data = json.dumps(final_result_output)

    with open("sample.json", "w", encoding='utf-8') as outfile:
        outfile.write(json_data)

if __name__ == '__main__':
    _main()
