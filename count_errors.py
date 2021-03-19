import glob
import xml.etree.ElementTree as ET
from collections import Counter
from xml.dom import minidom 


# XML namespace
ns = {'tei': 'http://www.tei-c.org/ns/1.0' }

def count_errors(file_list):
    wc = 0
    f_count = len(file_list)
    rev_count = 0
    error_count = 0
    for file in file_list:
        try:
            root = ET.parse(file).getroot()
            sentences = root.findall('.//tei:s',ns)
        except:
            print('Bad XML')

        if True:
            for sentence in sentences:

                for token in sentence:
                    if token.tag != "{http://www.tei-c.org/ns/1.0}revision":
                        wc += 1
                
                revisions = sentence.findall('.//tei:revision',ns)
                rev_count += len(revisions)

                original = sentence.findall('.//tei:original',ns)
                for w in original:
                    wc += len(w)
                    

                errors = sentence.findall('.//tei:error',ns)
                error_count += len(errors)
                
    return wc, f_count, rev_count, error_count

def sort_errors(files):
    freq=Counter()
    for filename in files:
        mydoc = minidom.parse(filename)
        items = mydoc.getElementsByTagName('error')
        for item in items:
            freq[item.attributes['xtype'].value]+=1
    return freq

file_list = glob.glob('tei/*.xml')

error_counts = count_errors(file_list)

print('Number of revision:', error_counts[2])
print('Number of errors:', error_counts[3])
print('Number of files:', error_counts[1])
print("Number of words:", error_counts[0])
print("Number of errors per 1000 words:", (error_counts[3]/error_counts[0])*1000)
print("Number of errors per type:", sort_errors(file_list))

