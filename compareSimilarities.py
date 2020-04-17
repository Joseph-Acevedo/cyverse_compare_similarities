import spacy
import glob
import sys
import os

import pandas as pd
import numpy as np

import pickle


class GenerateSimilarities:
    ### Constants ###
    FILES_LOC = ""
    FILES_TYPE = "*.txt"
    BIBJSON = "..\\spaCyModels\\text\\bibjson.json"
    MODEL = "en_trf_bertbaseuncased_lg"
    TOKEN_FILE = "tokenizd_files_dictionary.p"
    FILE_TO_READ = ""

    def __init__(self, folder_loc, file_loc):
        self.FILES_LOC = folder_loc
        self.FILE_TO_READ = file_loc


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
        pickle.dump(files_parsed, open(self.FILES_LOC + self.TOKEN_FILE, "wb"))

        return files_parsed        

    def get_model(self, nlp_model):
        if os.path.isfile(self.FILES_LOC + self.TOKEN_FILE):
            return pickle.load( open(self.FILES_LOC + self.TOKEN_FILE, "rb"))
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
        
        filename = self.FILE_TO_READ
        self.find_most_similar(filename, nlp, token_dict)
        

       
if __name__ == "__main__":
    sys.stdout = open('/iplant/home/josephacevedo/test_data/output.txt', 'w')

    file_loc = "/iplant/home/josephacevedo/test_data/54b43271e138239d868510dc.txt"
    folder_loc = "/iplant/home/josephacevedo/test_data/"

    gs = GenerateSimilarities(folder_loc, file_loc)
    gs.run_similarity_finder()