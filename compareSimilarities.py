import spacy
import glob
import json
import os

import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize, word_tokenize 
import warnings 
import pickle

warnings.filterwarnings(action = 'ignore') 
import gensim 
from gensim.models import Word2Vec

class GenerateSimilarities:
    ### Constants ###
    FILES_LOC = "..\\spaCyModels\\text\\"
    FILES_TYPE = "*.txt"
    BIBJSON = "..\\spaCyModels\\text\\bibjson.json"
    MODEL = "en_trf_bertbaseuncased_lg"
    TOKEN_FILE = "tokenizd_files_dictionary.p"


    def parse_bibjson(self):
        with open(self.BIBJSON, 'r', encoding="utf-8") as f:
            data = json.load(f)
        return data

    def tokenize_and_vectorize_files(self, nlp_model):
        print("Token dictionary file not found... Tokenizing files, please wait:")
        files_parsed = {}
        files = glob.glob(self.FILES_LOC + self.FILES_TYPE)

        json_dict = self.parse_bibjson()
        files_processed = 0

        for filename in files:
            # find the correseponding title in json
            if files_processed >= 5:
                break
            title = ""
            for file_json in json_dict:
                if file_json['_gddid'] == filename[len(self.FILES_LOC):-4]:
                    title = file_json['title']
                    break
            # If we couldn't find the filename then just skip it
            if title == "":
                continue
            
            f = open(os.path.join(os.getcwd(), filename), mode='r', encoding='utf-8')
            file_text = f.read()
            
            file_failed = False
            try:
                files_parsed[filename] = nlp_model(file_text)
            except Exception as e:
                f.close()
                file_failed = True
                print(str(e))
            finally:
                files_processed += 1
                print("Processed file [", files_processed, "/", (len(files)), "] - ", filename, end="")
                if file_failed:
                    print("   [FAILED]")
                else:
                    print()

        # Save the tokens to a file so we don't have to parse them again            
        pickle.dump(files_parsed, open(self.TOKEN_FILE, "wb"))

        return files_parsed        

    def get_model(self, nlp_model):
        if os.path.isfile(self.TOKEN_FILE):
            return pickle.load( open(self.TOKEN_FILE, "rb"))
        else:
            return self.tokenize_and_vectorize_files(nlp_model)

    def find_most_similar(self, filename, nlp_model, token_dict):
        if not os.path.isfile(filename):
            print(f"Couldn't find file {filename}! Please make sure that the file exists in the directory and is visible")
            return
        
        with open(filename, mode='r', encoding="utf-8") as f:
            text = f.read()
        new_file_tokens = nlp_model(text)

        # ms stands for most similar
        ms_filename = ""
        ms_percentage = 0
        for name, tokens in token_dict.items():
            similarity = tokens.similarity(new_file_tokens)
            if similarity > ms_percentage:
                ms_percentage = similarity
                ms_filename = name
        # Cut off to closest percentage
        ms_percentage = int(ms_percentage * 100)
        print(f"Most similar file to {filename} is {ms_filename}, which is {ms_percentage}% similar")

    def run_similarity_finder(self):
        print("Loading spaCy model...")
        # load the spacy model
        nlp = spacy.load(self.MODEL)

        print("Attempting to load token dictionary...")
        token_dict = self.get_model(nlp)

        print("Token dictionary loaded... ")
        
        while True:
            filename = input("Please enter a filename to compare (q to quit): ")
            if filename == "q" or filename == "Q":
                return
            self.find_most_similar(filename, nlp, token_dict)
        

       
if __name__ == "__main__":
    gs = GenerateSimilarities()
    gs.run_similarity_finder()