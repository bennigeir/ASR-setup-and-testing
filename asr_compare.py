import re, glob, os
from os import path
import random
import re

import xml.etree.ElementTree as ET

from collections import namedtuple

from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

from Bio.Seq import Seq
from Bio.pairwise2 import format_alignment
from Bio import pairwise2

import tokenizer
from tokenizer import split_into_sentences
from tokenizer import tokenize
from tokenizer import TOK
from tokenizer.definitions import PUNCTUATION_REGEX

# XML namespace
ns = {'tei': 'http://www.tei-c.org/ns/1.0' }

basedir='C:/Users/Benedikt/Documents/GitHub/ASR-setup-and-testing/txt'
outputdir='C:/Users/Benedikt/Documents/GitHub/ASR-setup-and-testing/tei'

original_file = 'sentences.original.txt'
output_file = 'sentences.output.txt'

original_path2 = '{}/{}'.format(basedir, original_file)
output_path2 = '{}/{}'.format(basedir, output_file)


Revision = namedtuple('Revision', ['original','output'])

def align2(sequence1, sequence2):
    #alignments = pairwise2.align.localms(sequence1.split(), sequence2.split(), 2,-1,-0.5,-0.1, gap_char=["-"])
    alignments = pairwise2.align.localms(sequence1, sequence2, 2, -1, -1, -1, gap_char=['^'])

    a = alignments[0]
    
    return zip(a[0], a[1])

def align(sequence1, sequence2):

    # This is encoded because the aligner uses the dasy as a gap element
    sequence1 = ['<DASH />' if word == '-' else word for word in sequence1]
    sequence2 = ['<DASH />' if word == '-' else word for word in sequence2]

    # Create sequences to be aligned.
    a = Sequence(sequence1)
    b = Sequence(sequence2)

    #print(22)

    # Create a vocabulary and encode the sequences.
    v = Vocabulary()
    aEncoded = v.encodeSequence(a)
    bEncoded = v.encodeSequence(b)

    #print(33)

    # Create a scoring and align the sequences using global aligner.
    scoring = SimpleScoring(2, -1)
    aligner = GlobalSequenceAligner(scoring, -2)

    #print(99)

    score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)

    #print(34)

    # Create alignment object and return it
    alignment = v.decodeSequenceAlignment(encodeds[0])
    return alignment

def all_tokens(text):
    ret = []
    tokens = tokenize(text)
    for token in tokens:
        if not token.txt:
            ret.append(TOK.descr[token.kind].replace(' ','_'))
        else:
            ret.append(token.txt)
    return ret


def tei_token(token):
    if token in ['BEGIN_SENT','END_SENT', '^']:
        return ''
    elif re.match(PUNCTUATION_REGEX, token):
        if token.startswith('Z') and token.endswith('Z'):
            token = token.strip('Z')
            return '<c><hi>{}</hi></c>'.format(token)
        return '<c>{}</c>'.format(token)
    else:
        # italic tokens handled
        if token.startswith('Z') and token.endswith('Z'):
            token = token.strip('Z')
            return '<w><hi>{}</hi></w>'.format(token)
        # superscript handled
        elif token.startswith('SUP') and token.endswith('SUP'):
            token = token.strip('SUP')
            return '<w><sup>{}</sup></w>'.format(token)
        # subscript handled
        elif token.startswith('SUB') and token.endswith('SUB'):
            token = token.strip('SUB')
            return '<w><sub>{}</sub></w>'.format(token)
        return '<w>{}</w>'.format(token)

def error_tei(original_text, output_text):
    # list of xml-elements to be joined and returned
    ret = ['<?xml version="1.0" encoding="utf-8"?>']
    ret.append('<TEI xmlns="http://www.tei-c.org/ns/1.0">')
    ret.append('<teiHeader></teiHeader>')

    original_tokens = all_tokens(original_text)
    output_tokens = all_tokens(output_text)

    #print(2)

    a = align2(original_tokens,
              output_tokens)
    

    #print(3)

    in_error = False
    collect_original = []
    collect_output = []
    sentence_id = 1
    revision_id = 1

    ret.append('<text><body><p n="1">')
    for original, output in a:

        # here, the original and the output text match
        if original == output:

            if in_error:
                ret.append('    <original>{}</original>'.format(''.join(collect_original)))
                ret.append('    <output>{}</output>'.format(''.join(collect_output)))

                ret.append('      <errors>')
                ret.append('        <error xtype="xxx" eid="0" />'.format(''.join(collect_output)))
                ret.append('      </errors>')


                ret.append('  </revision>')

                collect_original = []
                collect_output = []
                in_error=False

            if original == 'BEGIN_SENT':
                ret.append('<s n="{}">'.format(sentence_id))
                sentence_id = sentence_id + 1
            elif original == 'END_SENT':
                ret.append('</s>')
            else:
                if original == '&':
                    original = '&amp;'
                elif original == '<':
                    original = '&lt;'
                elif original == '>':
                    original = '&gt;'
                elif original == "'":
                    original = '&apos;'
                elif original == '"':
                    original = '&quot;'
                ret.append('  {}'.format(tei_token(original)))

        # else, we are in a mismatch region
        else: 
            if not in_error:
                ret.append('  <revision id="{}">'.format(revision_id))
                revision_id = revision_id + 1
                in_error=True

            collect_original.append(tei_token(original))
            collect_output.append(tei_token(output))
    
    ret.append('</p></body></text>') 
    ret.append('</TEI>')
    return '\n'.join(ret).replace('<DASH />','-')


def collect_filenames(directory):
    os.chdir(directory)
    original_files = glob.glob("*.original.txt")

    ret = []
    for original in original_files:
        output = '{}.output.txt'.format(original[:-13])
        if path.exists(output):
            ret.append( Revision(original, output) )
        else:
            print(output)
            print('Missing corrections for file {}!'.format(original))
            raise Exception
    return ret


# the program

# go through revised files, all the *.original.txt ones.
revisions = collect_filenames(basedir)

for revision in revisions:  # doc textarnir

    with open(revision.original, encoding='utf-8') as f:
        original_texts = f.read().split(';;')

    with open(revision.output, encoding='utf-8') as f:
        output_texts = f.read().split(';;')

    if not len(original_texts) == len(original_texts):
        print('mismatch between text versions')
        raise Exception


    texts = [Revision(*text) for text in zip(original_texts, output_texts)]

    for idx, text in enumerate(texts):
        outfile = '{}/{}-t{}.xml'.format(outputdir,
                                         revision.original.split('.')[0], 
                                         idx)
        print(outfile)
        teidoc = error_tei(*text)

        try:
            root = ET.fromstring(teidoc)
        except:
            print('Bad XML')

        with open(outfile, 'w', encoding='utf-8') as f:
            f.write(teidoc)
