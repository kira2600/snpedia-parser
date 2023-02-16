import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from pyquery import PyQuery as pq

def file_read(file_name):
    with open(file_name, encoding='utf-8') as json_file:
        json_content = json_file.read()

    return json.loads(json_content)

def filter_json(json_content):

    count = 0

    list_for_exclude = ['summary=common in clinvar','summary=common in complete genomics', 'summary=common genotype', '#REDIRECT', 'summary=common on affy axiom data', 'summary=normal', 'summary=common/normal']
    for key, value in json_content.copy().items():
        for exclude_element in list_for_exclude:
            if exclude_element in value:
                del json_content[key]
        count += 1

    print (json_content)
    print (count)
    return json_content

def page_generator(final_json):
    doc = pq("<html><body><table></table></body></html>")
    table = doc("table")
    for key, value in final_json.items():
        table.append("<tr><td>{}</td><td>{}</td></tr>".format(key, value))

    # Write the HTML to a file
    with open("snp_result.html", "w") as file:
        file.write(str(doc)) 

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snp_file', type=str, help='Please provide your DNA SNP file')
    args = parser.parse_args()

    final_json = filter_json(file_read(args.snp_file))
    
    page_generator(final_json)

if __name__ == '__main__':
    _main()
