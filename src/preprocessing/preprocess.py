import torch


from pickle import load, dump


from corpus_utils import get_references, read_tokenized_corpuses
from decase import decase_corpuses
#from apply_stanza_processors import retrieve_stanza_outputs
from build_word_vocabs import build_word_vocabs
from build_subword_vocabs import build_subword_vocabs
from apply_vocab import apply_vocab
from corpus import get_tokenized_corpuses
from build_batches import get_batches
from import_configs import read_configs
from pos_concatenate import pos_concatenate_corpuses
from subword_segment import subword_segment_corpuses


# now that finished most expensive preprocessing step, can perform remainder of preprocessing.
#preprocess_phase2
#def preprocess_phase2(path='/content/gdrive/My Drive/NMT/iwslt16_en_de/', num=None, vocab_type="subword_joint"):
    #corpuses = retrieve_stanza_outputs() # dict of corpus names, each mapped to a stanza Document object
    #decase_corpuses(corpuses, path) # overwrites corpuses as dict of corpus names, each mapped to List[List[str]] (list of corpus's decased sentences, each of which is a list of words)
    #if vocab_type in ["subword_ind", "subword_joint", "subword_pos"]:
    #    subword_segment_corpuses(corpuses, path)
    #if vocab_type in ["word_pos", "subword_pos"]:
    #    pos_concatenate_corpuses(corpuses, path)


# converts all preprocessed corpuses into tensors that can be directly
# passed to a model, and saves them to pickle files.
# returns corresponding hyperparameters that can be used to instantiate
# a compatible model.
# preprocess_phase3
# !!!incorporate vocab_threshold in hyperparams file instead.
def construct_model_data(*corpus_names,
        corpus_path='/content/gdrive/My Drive/NMT/iwslt16_en_de/',
        config_path='/content/gdrive/My Drive/NMT/configs/', 
        data_path='/content/gdrive/My Drive/NMT/data/',
        model_name='my_model',
        vocab_threshold=10,
        src_vocab_file='vocab.de',
        trg_vocab_file='vocab.en'):
    
    hyperparams = read_configs(config_path)
    vocab_type = hyperparams["vocab_type"]
    prefix = vocab_type + "_"
    # which variants of preprocessed corpuses to load depends on vocab type
    corpuses, ref_corpuses = get_tokenized_corpuses(*corpus_names, corpus_path, prefix)
        
    # build vocabs
    if vocab_type in ["word_pos", "subword_pos"]:
        vocabs = build_word_vocabs(corpuses, hyperparams)
    elif vocab_type in ["subword_ind", "subword_joint", "subword_pos"]:
        vocabs = build_subword_vocabs(corpus_path, vocab_type, vocab_threshold, src_vocab_file, trg_vocab_file)
    
    # now that know the vocab sizes, can treat them as hyperparameters.
    hyperparams["src_vocab_size"] = len(vocabs["src_word_to_idx"])
    hyperparams["trg_vocab_size"] = len(vocabs["trg_word_to_idx"])
    # not technically hyperparams, but include special indices for convenience:
    hyperparams["sos_idx"]  = vocabs["trg_word_to_idx"]["<sos>"]
    hyperparams["eos_idx"]  = vocabs["trg_word_to_idx"]["<eos>"]

    # convert each corpus of words to corpus of indices,
    # and replace out-of-vocabulary words with unknown token
    # (if using word-level vocabs).
    apply_vocab(corpuses, vocabs, vocab_type)
    
    # package corpuses up into batches of model inputs, along with other necessary
    # data, such as masks for attention mechanism, lengths for efficient
    # packing/unpacking of PackedSequence objects, etc.
    train_batches, dev_batches, test_batches = get_batches(corpuses, train_bsz=hyperparams["train_bsz"], dev_bsz=hyperparams["dev_bsz"], test_bsz=hyperparams["test_bsz"], device=hyperparams["device"])
    
    # can directly be loaded to instantiate and then train a model.
    model_data = {
        "train_batches":train_batches,
        "dev_batches":dev_batches,
        "test_batches":test_batches,
        "idx_to_trg_word":vocabs["idx_to_trg_word"],
        "ref_corpuses":ref_corpuses,
        "hyperparams":hyperparams
    }
    
    dump(model_data, open(f"{data_path}{model_name}.pkl", 'wb'))


def retrieve_model_data(data_path='/content/gdrive/My Drive/NMT/data/', model_name='my_model'):
    return load(open(f"{data_path}{model_name}.pkl", 'rb'))