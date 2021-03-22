#!/usr/bin/env python3

import argparse
import nltk

parser = argparse.ArgumentParser(description='takes 2 texts and calculates average word error rate')
parser.add_argument('reference', help='path to reference (original/correct) text')
parser.add_argument('hypothesis', help='path to hypothesis (ASR transcription output) text')
parser.add_argument('-v', "--verbose", help="print each sentence's word error rate",
                    action="store_true")
args = parser.parse_args()

with open(args.reference) as f, open(args.hypothesis) as g:
    ref = f.readlines()
    hyp = g.readlines()

score = 0
i = 1
for ref_sent, hyp_sent in zip(ref, hyp):
    dist = 1 - (nltk.edit_distance(ref_sent.split(), hyp_sent.split()) / len(ref_sent.split()))
    if args.verbose == True:
        print('Sentence', i, 'distance:', dist)
    score += dist
    i += 1
print('Average word error rate:', score/len(ref))
