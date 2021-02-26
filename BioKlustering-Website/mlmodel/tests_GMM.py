#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import packages
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pdz
import numpy as np
import pandas as pd

from pandas import Series, DataFrame
import Bio
from Bio import SeqIO,AlignIO

import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.mixture import GaussianMixture as GMM

from sklearn.manifold import TSNE
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


# In[9]:


# methods

def parseFasta(data):
    d = {fasta.id : str(fasta.seq) for fasta in SeqIO.parse(data, "fasta")}
    pd.DataFrame([d])
    s = pd.Series(d, name='Sequence')
    s.index.name = 'ID'
    s.reset_index()
    return pd.DataFrame(s)

def get_kmer_table(path,k_min,k_max):
    genes,gene_len = read_fasta(path)
    count_vect = CountVectorizer(analyzer='char', ngram_range=(k_min, k_max))
    X = count_vect.fit_transform(genes)
    chars = count_vect.get_feature_names()
    kmers = X.toarray()
    kmer_freq = []
    for i in range(len(genes)):
        kmer_freq.append(kmers[i] / gene_len[i])
    input = pd.DataFrame(kmer_freq, columns=chars)
    return input

def get_gene_sequences(filename):
    genes = []
    for record in SeqIO.parse(filename, "fasta"):
        genes.append(str(record.seq))
    return genes

# genes: a list of gene sequences, which can directly be generated from get_gene_sequences().
def get_gene_len(genes):
    gene_len = []

    for i in range(len(genes)):
        gene_len.append(len(genes[i]))
    return gene_len

#read single fasta file containing all the gene sequences
def read_fasta(path):
    virus = parseFasta(path)
    virus = virus.drop_duplicates(keep="last")
    genes = list(virus['Sequence'])
    gene_seq = get_gene_sequences(path)
    gene_len = get_gene_len(gene_seq)
    return gene_seq,gene_len

def get_predictions_default(path,k_min,k_max,num_class,cov_type):
    seed  = np.random.seed(None)
    ran_state = np.random.get_state()
    kmer_table = get_kmer_table(path, k_min, k_max)
    gmm = GMM(n_components=num_class,covariance_type=cov_type,random_state = seed).fit(kmer_table)
    labels = gmm.predict(kmer_table)
    return labels,ran_state

def get_predictions_from_state(path,k_min,k_max,num_class,cov_type,state):
    kmer_table = get_kmer_table(path, k_min, k_max)
    gmm = GMM(n_components=num_class,covariance_type=cov_type,random_state = np.random.set_state(state)).fit(kmer_table)
    labels = gmm.predict(kmer_table)
    return labels

def get_predictions(path,k_min,k_max,num_class,cov_type, seed):
    kmer_table = get_kmer_table(path, k_min, k_max)
    gmm = GMM(n_components=num_class,covariance_type=cov_type,random_state = seed).fit(kmer_table)
    gmm.init_params = 'random'
    labels = gmm.predict(kmer_table)
    return labels

def cal_accuracy(labels, predictions):
    err = 0
    total_len = len(labels)
    for i in range(len(labels)):
        if (labels[i] == -1):
            total_len = total_len-1
            continue
        if (labels[i] != predictions[i]):
            err += 1
            
    return 1-err/(total_len)

def get_predictions_semi(path,k_min,k_max,num_class,cov_type,seed,labels):
    targets = []
    kmer_table = get_kmer_table(path, k_min, k_max)
    finalDf = pd.concat([kmer_table, pd.Series(labels)], axis = 1)
    gmm = GMM(n_components=num_class,covariance_type=cov_type,random_state = seed)
    gmm.init_params = 'random'
    for i in range(num_class):
        if (i in list(finalDf.Labels)):
            targets.append(i)
    if (len(targets)==num_class):
        #print("Yes")
        gmm.means_init = np.array([kmer_table[finalDf.Labels == i].mean(axis=0) for i in targets])
    gmm.fit(kmer_table)
    predictions = gmm.predict(kmer_table)
    return predictions

def model_selection(path,labels,num_class):
    best_accu = 0
    best_prediction = []
    cov_type = ['full','diag','tied','spherical']
    k_min = [2,3,4,5]
    k_max = [2,3,4,5]
    for cov in cov_type:
        for k1 in k_min:
            for k2 in k_max:
                if (k2 >= k1):
                    prediction = get_predictions_semi(path,k1,k2,num_class,cov,0,labels)
                    accu = cal_accuracy(labels,prediction)
                    if accu > best_accu: 
                        best_accu = accu
                        best_kmin = k1
                        best_kmax = k2
                        best_cov = cov
                        best_prediction = prediction
    #print('Best model has the following parameters:')
   # print('minimum length of kmer: ', best_kmin)
    #print('maximum length of kmer: ', best_kmax)
    #print('covariance type: ', best_cov)
    #print('It has an accuracy regard to known labels of ',best_accu)
    return best_prediction


# In[14]:


def test_GMM_Unsup(genes,gene_len):
        """
        Test that if unsupervised GMM method works
        """
        k_min = 2 
        k_max = 6 
        num_class = 2 
        cov_type = 'full' 
        seed = 0
        
        count_vect = CountVectorizer(analyzer='char', ngram_range=(k_min, k_max))
        X = count_vect.fit_transform(genes)
        chars = count_vect.get_feature_names()
        kmers = X.toarray()
        kmer_freq = []
        for i in range(len(genes)):
            kmer_freq.append(kmers[i] / gene_len[i])
        kmer_table = pd.DataFrame(kmer_freq, columns=chars)
        
        gmm = GMM(n_components=num_class,covariance_type=cov_type,random_state = seed).fit(kmer_table)
        gmm.init_params = 'random'
        labels = gmm.predict(kmer_table)
        
        assert all(labels == [0,0,1,0])

def test_GMM_Unsup2(test_file_1):
    k_min = 2 
    k_max = 6 
    num_class = 2 
    cov_type = 'full' 
    seed = 0
    labels = get_predictions(test_file_1,k_min,k_max,num_class,cov_type,seed)
    assert all(labels == [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0,
       1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1,
       1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1,
       1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0,
       1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1,
       1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1])
    
def test_GMM_Semi(test_file_1,test_file_2):
    num_class = 2
    labels_50 = pd.read_csv(test_file_2)
    labels_50 = pd.Series(labels_50['Labels'])
    labels = model_selection(test_file_1,labels_50,num_class)
    assert all(labels == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
       1, 1])
    
def test_GMM_Semi2(test_file_1,test_file_3):
    num_class = 2
    labels_50 = pd.read_csv(test_file_3)
    labels_50 = pd.Series(labels_50['Labels'])
    labels = model_selection(test_file_1,labels_50,num_class)
    assert all(labels == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
       0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
       1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1,
       1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0,
       1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0,
       0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0,
       0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0,
       1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0,
       0, 1])


# In[11]:


test_file_1 = "../datasets/combined_Bat_Cat_flu.fa" #need to be changed to filepath in github
test_file_2 = '../datasets/labels_fifty_percent.csv' #need to be changed to filepath in github
test_file_3 = '../datasets/labels_ten_percent.csv' #need to be changed to filepath in github
genes = ['ATGGATCGCATAAAAGAACTACTAGAGATGACAAAAAATTCCCGCATGAGGGAAATTTTATCGACAACAAGTGTTGACCACATGGCAGTAATCAGAAAATACACAAGTGGGAGACAAGAGAAAAACCCAGCACTAAGAATGAAATGGATGATGGCAATGAAATTTCCAATAAGTGCATCAGCCAAAATAAAAGAACTAATACCAGAAAAGGATGAAGATGGAAACATATTGTGGACAAATACAAAAGATGCTGGGAGTAACAGATTACTTGTTTCACCAAATGCAGTAACTTGGTGGAATAGGGCTGGACCAATATCAGAAGTTGTACATTACCCTAAAGTCTACAAAATGTACTTTGATAGGCTTGATCGCTTGCAAAATGGAACATATGGGCCAGTGAAATTTTACAACCAAATGAAAATAAGAAAAAGAGTTGATATAAATCCAGGGCACAAGGACTTGACATCAAAAGAAGCTCAGGACGTAATAATGGAAGTTGTCTTTCCAAATGAAGTAGGAGCAAGAACATTGTCATCAGATGCACAATTAGCGATCACCAAGGAGAAAAAACAAGAGCTGCAGAACTGCAAAATCTCTCCAATTATGGTTGCATACATGCTTGAAAGGGAATTAGTACGAAAAACAAGGTTCCTGCCAGTTGCAGGGGCAACCTCAAGCACTCATGTTGAAGTTTTACACCTAACCCAAGGCACGTGTTGGGAACAACAATACACACCAGGAGGTGAAGCAGAAAATGATGACATGGACCAAACCTTAATAATTGCTGCTAGAAACATTGTAAGAAGATCAATTGTTGCAATTGATCCTCTAGCATCCTTGATATCTATGTGCCATACTACAAACATATCTGCTGAACCACTCACTGAAATACTGAAGGCGAACCCAACAGACGAACAAGCTGTAAATATCTGTAAGGCAGCTCTTGGAATTAAAATAAACAATAGTTTTAGCTTTGGAGGCTATAACTTTAAGAAAATAAAAGGGAATTCAAAAAGAAGTGAGCAACAAGTGTTAACTGGAAACCTTCAAACATTAACATTAACAATTTTTGAAGGTTATGAAGAATTCAATGTATCTGGAAAAAGAGCATCTGCAGTATTGAAGAAAGGAACACAAAGGCTCATACAAGCAATCATTGGTGGGAGAACTATTGAAGATATATTAAATCTAATGATAACATTGATGGTCTTCTCTCAAGAGGATAAAATGATAAAATCAGTAAGAGGGGATTTGAATTTTCTCAACAGAGCAAACCAGCGATTGCACCCCATGTATCAATTATTGAGACATTTTCAAAAGGATTCTGGAGTCCTTCTAAGGAACTGGGGAATGGAAGACATAGATCCAGTAATGGGAATTATGGGAATACTACCGGATGGAACAATAAACAAGAATAACACACTGGTTGGGATAAGAATAAGTCAAGGGGGAGTTGATGAATATTCTTTCAATGAAAGGATAAGGGTGTCAATTGACAAATACCTAAGAGTCAAAAATGAGAAAGGAGAATTACTAATAAGTCCAGAAGAAGTAAGTGAAGCACAAGGACAAGAAAAATTGCCAATAAACTACAATTCATCCCTAATGTGGGAAGTAAATGGTCCAGAATCGATACTAACAAACACTTATCATTGGATACTGAAAAATTGGGAAGTCTTAAAAACCCAATGGATGACTACACCTAACATTCTATATAATAAAATGGAATTTGAACCTTTTCAGACTTTAATACCCAAAGGAAATAGAGCCGCATACAGTGGTTTTACTAGAACTTTATTCCAACAAATGAGAGATGTAGAAGGGACCTTTGACAGCATTCAAATAATAAAGCTCTTACCATTTGCAGCACACCCACCGTCTGCTGGCCGAAATCAATTCAGTTCCTTTACCATTAACATAAGAGGTGCACCACTTAGGCTTCTAATAAGAGGGAACTCACAAATTTTCAATTACAATAAAATGGAAAATAGTATCATCATATTAGGGAAAAATGTAGGAAAACTAGACGAATCAATAATAACAGAAACTAACACTATTGAGTCAGCAGTGTTAAGAGGTTTCTTAATTCTTGGGAAAGCCAACAGCAAATATGGACCTGTATTGACTATCGCAGAGCTGGATAAATTAGGAAGGGGAGAAAAAGCAAATGTCCTAATAGGGCAAGGAGATACAGTGTTGGTCATGAAACGGAAAAGGGACTCCAGTATACTTACTGATAGCCAGACAGCCATCAAAAGGATTCGTTTGGAGGAATCAAAATAA',
 'ATGGACGTTAATCCGATGCTAATATTTCTAAAGGTTCCAGTGCAAAATGCAATTAGTACTACATTCCCATATACAGGGGACCCTCCTTATAGCCATGGAACAGGTACCGGGTACACTATGGACACTGTTATAAGAACTCATGAATATTCAAATAAAGGAATTTGGGTTACGAATAGTGAAACATCAGCCATTCAATTGAACCCAATTGATGGACCATTACCAGAGGACAATGAACCTAGTGGATATGCTCAGACAGACTGTGTGTTAGAATTGATTGAAAAATTAGGAGAGTCACACCCGGGACTTTTTAATATTGCATGCCAAGAAACAATTGATTCGATTCAGCAAACCAGAGTTGATAAACTAACTCAAGGAAGACAAACCTACGACTGGACTCTGAATAGAAATCAACCTGCTGCAACAGCACTTGCAAACACTATAGAAGTGTTCAGAAAAAATGGCTATACTGCAAATGAGTCAGGTAGACTAATAGACTTTCTAAAGGATGTACTAATCTCTTTTGAGAAAGAATCAATGGAAATTGTAACTCATTATCAAAAGAAAAAGAGAATAAGAGATAATCATACCAAAAGGATGGTCACTCAAAGAACTATAGGGAAAAGAAAAACAAAATTAAGCAGAAAGTCATATTTGATAAGAGCCCTGACTCTCAATACAATGACCAAGGATGCAGAGAGAGGAAAATTAAAGCGCCGTGCTATAGCCACACCAGGAATGCAAATAAGGGGGTTTGTATATTTTGTAGAATTACTTGCAAGAAATATCTGTGAAAGATTAGAACAATCAGGATTACCTGTCGGTGGTAATGAAAAGAAAGCTAAATTAGCAAATGTTATTAAGAAAATGATGGCCAAATCAAGTGATGAGGAACTTTCTTATACAATTACTGGAGACAACACAAAATGGAATGAAAACCAAAATCCAAGGATCTTTCTAGCTATGATTCTCAAAATAACAGAAGGTCAACCTGAGTGGTTCAGAGACCTATTAGCTGTCGCTCCAATAATGTTTTCTAACAAAGTTGCAAGACTTGGACGGGGATACATGTTTGAAAGCAAGTCAATGAAAGTTAGAACCCAAATACCTGCAGAAGAACTGAACACTATAAGCTTAAAATATTTCAATGAAGAAACAAAAAAGAAAATTGAAAAGGTGAGAAATCTTATGATCGATGGGACAGCATCACTGAGCCCAGGAATGATGATGGGCATGTTCAACATGCTAAGCACTGTTTTAGGAGTTAGCGTTTTAAATATCGGTCAAAAACAAATGTTAAAAACCACATACTGGTGGGATGGACTACAGTCTTCCGATGATTTTGCTCTAATAGTTAATGGACATTTTAAAAATGATATACAGCAAGGTGTAAATCATTTCTATAGAATCTGCAAATTGGTAGGGATAAACATGTCTCAAAAGAAATCCTACATTAACAAAACAGGAACTTTTGAATTCACAAGTTTTTTCTATAGATATGGTTTTGTGGCCAATTTTTCTATGGAACTGCCCTCCTTTGGTGTTGCAGGAAACAATGAGTCTGCTGACATGAGTATAGGCACAACAGTTATAAAAACAAACATGATAAATAATGATCTAGGTCCTGCAACAGCTCAAATGGCTATCCAGCTCTTTATAAAGGATTACAGATACACTTATAGATGCCATCGAGGAGATACTAATTTAGAAACAAGAAGAACCAAAAGTTTAAAGAGACTGTGGACGGAAACAATATCCAAATCTGGATTATTAGTATCAGATGGTGGTCCTAATCCTTACAATTTAAGGAATTTACATATACCTGAAGTATGTCTCAAATGGCATTTAATGGACCCAGAATACAGAGGGAGACTGTGTAATCCAAACAACCCATTTGTGCACCACATGGAAGTTGAAAGCACGAATCTTGCAGTAATAATGCCAGCCCATGGACCAGCAAAATCAATGGAGTATGATGCTGTAGCTACAACTCATTCATGGACACCTAAAAGGAATAGATCAATTTTAAACACCAATCAAAGAGGAATATTGGAAGATGAACGAATCTACCAAAAGTGCTGCCAAATATTTGAAAAATTCTTCCCAAGTTCAAGTTATAGGAGACCTATTGGAATGGCAAGCATGTTGGATGCCATGTTATCAAGGGCCAAAATTGATGCTAGGATAGATCTAGAGTCAGGTAGATTAAGCAATCAAGATTTCTCAGAGATAATGAATATCTGTAAAGCAATCGAAAATTTGAAACGCAGATAA',
 'ATGGAGAATTTCATAAGAGCAAACTTCAATCCAATGATTCTGGAGAGAGCAGAAAAAAGCATGAAAGAGTATGGAGAAAGCCCCCAAAATGAAGGGAACAAGTTTGCTGCTATATCTACTCATCTTGAAGTATGTTTCATGTATTCTGATTTTCATTTTATCGATCTAGAAGGAAATGCAATAATCAAAGAATCAGAAGATGATAATGCAATGTTAAAACATAGATTTGAAATCATTGAAGGCCAGGAAAGAAATGTTGCCTGGACTATTGTAAATTCAATATGCAACATGACCAATATAGATAAACCAAGATACCTTCCAGATCTTTATGACTACAAAACTAATAAATTCATTGAAATTGGAGTAACTAGAAGACGGGTTGAAGATTATTATTATGAAAAGGCTAACAAATTAAAGGATGGAAATGTTTATATCCATATCTTTTCATTTGACGGCGAAGAAATGTCAACAAATGATGAATACATTCTTGATGAAGAAAGTAGGGCAAGAATCAAAACAAGACTCTTTGTTCTGCGTCAAGAAATGGCATCAGCAGGGCTATGGGATTCCTTTCGTCAATCAGAAAAGGGTGAAGAAACAGTTGAAGAGGAATTCAAATTTCCACCCACATTCAAGAAATTGGCGGACCAAAGTCTTCCACCATCATTCAAGGACTATAATCAATTCAAAATATATGTGTCCTCTTTCAAATCGAATGGAAACATTGAAGCTAAATTAGGAGCCATGAGTGAAAAAGTGTCAGCCACAATTGAAGAATTCAACCCCAAAGACATAACTGAATTAAAAATGCCAAAAGGTAAACCATGTACACAAAGGAGCAAATTTCTGCTAATGGACTCAATGAAATTATCAATATTAAATCCATCTCATGAAGGTGAAGGAATTCCTATGAAAGATGCAACAGCATGTATGGAAACCTTTTGGGGATGGAAAAAACCAAATATAATTAAAAAACATGACAAGGGTGTAAATACTAATTATCTAATGATTTGGGAACAATTATTTGATGCTCTCAAAGAGAATGAAAACAAATATCTTAATTTGAAAAAAACTAATCATCTAAAGTGGGGGTTAGGAGAAGGACAAGCTCCTGAAAAAATGGATTTTGAAGATTGTAAGGACATTCCTGATTTATTCCAATACAAAAGTGATCCACCAGAACCCAGACAACTAGCAAGTTGGATTCAAAGTGAATTCAACAAAGCATCAGAGCTAACAAGCTCAAACTGGATTGAATTTGATGAATTAGGAGAGGATGTAGCTCCTATAGAGCATATAGCAAGTAGAAGGCGAAACTTTTTCACTGCAGAGGTCTCACAATGTAGAGCCTCAGAATACATAATGAAAGCTGTATATATAAATACAGCACTTTTAAACTCGTCCTGTACAGCTATGGAGGAATATCAAGTAATACCAATAATTACAAAATGTAGAGACATCTCTGGGCAAAGGAAAACAAACCTATATGGATTTATTATCAAGGGAAGATCCCATCTAAGAAATGACACAGATGTCGTGAATTTCATATCATTGGAGTTTTCATTGACTGACCCAAGGAATGAACCACATAAATGGGAAAAATATTGTGTTCTAGAAATTGGTGATATGGAAATAAAAACATCAATAAGCACAGTAATGAAACCGGTTTACTTATATGTTAGGACTAATGGAACATCCAAAATAAAAATGAAATGGGGGATGGAAATGAGAAGATGTTTATTGCAATCTCTCCAACAAGTGGAAAGTATGATAGAAGCAGAATCTGCTGTTAAAGAAAAAGACATGACGGAAACATTCTTCAGAAATAAAGAGAACGAATGGCCTATTGGAGAAAGCCCAAAAGGAATAGAGAAAGGCACCATTGGAAAAGTGTGCAGAGTTCTTCTAGCCAAATCAGTTTTCAACAGCATATATGCTTCCGCTCAATTGGAAGGTTTTTCAGCAGAATCTAGAAAACTTTTATTGTTAATACAAGCATATAGAGATAATTTAGATCCTGGAACATTTGATCTTAAGGGGCTATATGAGGCAATTGAGGAATGTATCATTAATGATCCCTGGGTCCTTTTAAATGCATCATGGTTCAACTCCTTCCTTAGAGCAGTACAAGGAAGCTTGTAA',
 'ATGATTACAATACTTATCTTGGTACTTCCTATTGTTGTAGGTGACCAGATATGCATTGGCTATCACTCAAATAATTCAACACAGACAGTGAATACTCTCCTCGAATCAAATGTACCAGTGACTTCCTCTCACAGCATCCTAGAAAAAGAACACAATGGTTTACTTTGCAAGCTAAAAGGGAAAGCACCCTTAGACCTTATTGACTGCTCTCTTCCTGCATGGCTTATGGGAAACCCAAAATGTGATGAACTTTTAACAGCAAGTGAATGGGCCTACATAAAAGAAGACCCAGAGCCTGAAAATGGGATATGTTTTCCAGGAGATTTTGATTCTTTAGAGGATCTAATTTTGTTGGTTTCCAACACTGATCATTTCAGAAAAGAAAAAATAATAGACATGACCAGATTCTCCGATGTGACTACAAACAATGTGGACAGTGCATGCCCATATGACACGAATGGTGCTTCCTTTTACAGAAATTTAAACTGGGTGCAACAAACCAAAGGCAAGCAACTGATTTTTCATTACCAGAACTCTGAAAACAACCCACTCCTAATAATTTGGGGAGTACACCAAACATCTAATGCTGCAGAACAAAACACTTACTATGGCTCACAAACTGGCTCAACAACCATCACCATTGGGGAAGAAACGAACACTTATCCATTAGTGATAAGTGAAAGTTCTATTCTTAACGGTCACTCTGATAGAATAAATTACTTTTGGGGAGTTGTCAATCCTAATCAGAATCTTTCAATTGTCAGTACAGGAAATTTCATCTGGCCAGAATACGGGTACTTTTTCCAAAAAACAACCAATATAAGTGGGATAATAAAGTCAAGTGAAAAGATAAGCGATTGCGACACAATCTGCCAAACAAAAATTGGGGCAATAAATAGCACACTGCCTTTTCAAAATATCCATCAAAATGCGATTGGAGATTGCCCTAAATATGTGAAAGCCCAAGAACTTGTTCTTGCAACTGGATTAAGGAACAATCCAATAAAAGAAACAAGAGGGCTTTTTGGTGCAATCGCAGGCTTCATCGAGGGAGGATGGCAAGGATTGATTGATGGTTGGTATGGGTATCACCACCAGAACTCGGAAGGTTCAGGCTATGCTGCTGACAAAGAAGCAACCCAGAAGGCTGTTGATGCGATAACCACAAAAGTAAATAACATAATAGACAAAATGAACACGCAATTTGAATCAACTGCCAAAGAGTTCAACAAAATTGAAATGAGAATAAAACATCTCAGTGACAGAGTTGATGATGGATTCTTGGATGTTTGGAGTTACAATGCTGAATTACTTGTTTTGCTGGAAAATGAAAGAACCCTGGACTTCCATGATGCAAATGTCAACAATTTGTATCAAAAAGTAAAAGTCCAGCTGAAAGACAATGCAATTGATATGGGAAACGGCTGTTTCAAGATTCTACACAAATGCAACAACACATGTATGGATGATATTAAAAATGGAACATACAATTATTATGAATACAGAAAGGAGAGCCACTTGGAAAAACAAAAAATTGACGGTGTGAAGCTATCAGAAAACAGTTCATATAAAATAATGATCATTTACTCAACAGTGGCAAGCTCAGTAGTGCTTGGCTTGATTATACTAGCCGCAATTGAATGGGGCTGTTTTAAAGGAAACCTGCAATGCAGAATATGTATTTGA']
gene_len = [2283,2271,2142,1686]

test_GMM_Unsup(genes,gene_len)
test_GMM_Unsup2(test_file_1)    
test_GMM_Semi(test_file_1,test_file_2)
test_GMM_Semi2(test_file_1,test_file_3)
print("Everything passed")


# In[ ]:




