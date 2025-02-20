"""
This script is what created the dataset pickled.

1) You need to download this file and put it in the same directory as this file.
https://github.com/moses-smt/mosesdecoder/raw/master/scripts/tokenizer/tokenizer.perl . Give it execution permission.

2) Get the dataset from http://ai.stanford.edu/~amaas/data/sentiment/ and extract it in the current directory.

3) Then run this script.
"""


#dataset_path='/Tmp/bastienf/aclImdb/'
dataset_path = '/home/abhishek/Desktop/nlp_project/lstm/try5/';

import numpy
import cPickle as pkl

from collections import OrderedDict

import glob
import os

from subprocess import Popen, PIPE

# tokenizer.perl is from Moses: https://github.com/moses-smt/mosesdecoder/tree/master/scripts/tokenizer
tokenizer_cmd = ['./tokenizer.perl', '-l', 'en', '-q', '-']

authors = ['AaronPressman', 'AlanCrosby', 'AlexanderSmith', 'ToddNissen', 'WilliamKazer'];

def tokenize(sentences):

	print 'Tokenizing..',
	text = "\n".join(sentences)
	tokenizer = Popen(tokenizer_cmd, stdin=PIPE, stdout=PIPE)
	tok_text, _ = tokenizer.communicate(text)
	toks = tok_text.split('\n')[:-1]
	print 'Done'

	return toks


def build_dict(path):
	sentences = []
	currdir = os.getcwd()
	print 'PATH USED FOR DICT', '%s/AaronPressman/' % path
	
	for author in authors:
		os.chdir(path + author + '/')
		for ff in glob.glob("*.txt"):
			with open(ff, 'r') as f:
				sentences.append(f.readline().strip())
	
	os.chdir(currdir)
	
	sentences = tokenize(sentences)
	print 'Building dictionary..',
	wordcount = dict()
	for ss in sentences:
		words = ss.strip().lower().split()
		for w in words:
			if w not in wordcount:
				wordcount[w] = 1
			else:
				wordcount[w] += 1

	counts = wordcount.values()
	keys = wordcount.keys()

	sorted_idx = numpy.argsort(counts)[::-1]

	worddict = dict()

	for idx, ss in enumerate(sorted_idx):
		worddict[keys[ss]] = idx+2  # leave 0 and 1 (UNK)

	print numpy.sum(counts), ' total words ', len(keys), ' unique words'

	return worddict


def grab_data(path, dictionary):
	sentences = []
	currdir = os.getcwd()
	os.chdir(path)
	for ff in glob.glob("*.txt"):
		with open(ff, 'r') as f:
			sentences.append(f.readline().strip())
	os.chdir(currdir)
	sentences = tokenize(sentences)

	seqs = [None] * len(sentences)
	for idx, ss in enumerate(sentences):
		words = ss.strip().lower().split()
		seqs[idx] = [dictionary[w] if w in dictionary else 1 for w in words]

	return seqs


def main():
	# Get the dataset from http://ai.stanford.edu/~amaas/data/sentiment/
	path = dataset_path
	print 'PATH', os.path.join(path, 'train/')
	dictionary = build_dict(os.path.join(path, 'train/'))

	train_x = [];
	train_y = [];
	for i, author in enumerate(authors):
		train_x_plus = grab_data(path + 'train/' + author, dictionary);
		train_x = train_x + train_x_plus;
		train_y = train_y + [i]*len(train_x_plus);

	test_x = [];
	test_y = [];
	for i, author in enumerate(authors):
		test_x_plus = grab_data(path + 'test/' + author, dictionary);
		test_x = test_x + test_x_plus;
		test_y = test_y + [i]*len(test_x_plus);

	f = open('authors5.pkl', 'wb')
	pkl.dump((train_x, train_y), f, -1)
	pkl.dump((test_x, test_y), f, -1)
	f.close()

	f = open('authors5.dict.pkl', 'wb')
	pkl.dump(dictionary, f, -1)
	f.close()

if __name__ == '__main__':
	main()
