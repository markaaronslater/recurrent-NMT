from pickle import load, dump

# utility functions for loading corpuses from text files,
# examining corpus contents, etc.

def read_corpuses(*corpus_names, path='/content/gdrive/My Drive/NMT/corpuses/iwslt16_en_de/', prefix='', _start=1, num=None):
    corpuses = {}
    for corpus_name in corpus_names:
        corpuses[corpus_name] = read_corpus(corpus_name, path, prefix, _start, num)
            
    return corpuses


# read lines <_start> thru <start> + <num> of corpus at text file 
# (<_start> uses 1-based idxing to match unix line numbering)
def read_corpus(corpus_name, path='/content/gdrive/My Drive/NMT/corpuses/iwslt16_en_de/', prefix='', _start=1, num=None):
    assert prefix in ['', 'word_', 'subword_joint_', 'subword_ind_']
    with open(path + prefix + corpus_name, mode='rt', encoding='utf-8') as f:
        corpus = f.read().strip().split('\n')
        upper = num if num is not None else len(corpus)
        start = _start-1 # convert to 0-based idxing

    return corpus[start:start+upper]


# reads and white-space splits a pre-tokenized corpus stored in a file.
# returns list of lists of words.
def read_tokenized_corpuses(*corpus_names, path='/content/gdrive/My Drive/NMT/corpuses/iwslt16_en_de/', prefix=''):
    corpuses = read_corpuses(*corpus_names, path=path, prefix=prefix)
    tokenize_corpuses(corpuses)
    
    return corpuses


def tokenize_corpuses(corpuses):
    for corpus_name in corpuses:
        tokenize_corpus(corpuses[corpus_name])


def tokenize_corpus(corpus):
    for i, sent in enumerate(corpus):
        corpus[i] = corpus[i].split()


# load target corpuses in format required by sacreBLEU, for evaluation of predictions.
def get_references(path='/content/gdrive/My Drive/NMT/corpuses/iwslt16_en_de/', overfit=False, dev=True):
    if not overfit:
        # only one set of references, so construct singleton list of lists of sentences.
        if dev:
            return [read_corpus("dev.en", path=path)]
        else:
            return [read_corpus("test.en", path=path)]
    else:
        return [read_corpus("train.en", path=path, num=10)]


# return true if is a source corpus, and false if is a target corpus
def is_src_corpus(corpus_name, src_corpus_suffix="de"):
    return corpus_name[-2:] == src_corpus_suffix


# print out first <num> sentences of each corpus
def print_corpuses(corpuses, num=None):
    for corpus_name in corpuses:
        print(corpus_name)
        print_corpus(corpuses[corpus_name], num)
    

def print_corpus(corpus, num=None):
    upper = num if num is not None else len(corpus)
    for sent in corpus[:upper]:
        print(sent)
    print()


# prints the morphological data associated with each word of each sentence.
# designed for printing output of stanza processors.
def print_processed_corpuses(corpuses, num=None):
    for corpus_name in corpuses:
        print(corpus_name)
        print_processed_corpus(corpuses[corpus_name], num)


# each corpus is a list of Stanza Sentence objects.
def print_processed_corpus(sentences, num=None):
    upper = num if num is not None else len(sentences)
    for i, sent in enumerate(sentences[:upper]):
        print(f"####### sentence {i+1}: #######")
        for word in sent.words: 
            print(f'word: {word.text}\t\tupos: {word.upos}\txpos: {word.xpos}')
        print("###############################")
    print()
    print()