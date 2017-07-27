# Hybrid Recommender
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from recommender.recommender import Recommender

with open('hybrid/hybrid_config.json') as config_file:    
    config = json.load(config_file)

# RECOMMENDER 1
rec1 = Recommender(config["rec1"]["default"])
for rule in config["rec1"]["examples"]:
    rec1.addRule(rule[0],rule[1])

# RECOMMENDER 2
rec2 = Recommender(config["rec2"]["default"])
for rule in config["rec2"]["examples"]:
    rec2.addRule(rule[0],rule[1])

# RECOMMENDER 3
rec3 = Recommender(config["rec3"]["default"])
for rule in config["rec3"]["examples"]:
    rec3.addRule(rule[0],rule[1])

def calcRecommendations(weights,context):
  rm_1 = rec1.recommend(context)
  rm_2 = rec2.recommend(context)
  rm_3 = rec3.recommend(context)  

  reliability_flags = getReliabilityFlags(context)
  selected_weights = np.array(reliability_flags) * weights
  balanced_weights = balanceWeights(selected_weights)
  
  hybrid = rm_1*balanced_weights[0] + rm_2*balanced_weights[1]+ rm_3*balanced_weights[2]
  
  return (rm_1,rm_2,rm_3,hybrid,reliability_flags)

def balanceWeights(weights):
  total_weight = sum(weights)
  weights = (np.array(weights)/(total_weight*1.0)).tolist()
  
  return weights

def getReliabilityFlags(context):
  usage_flags = [1,1,1]
  if context[0] == 0:
    usage_flags[0] = 0
  if context[3] == 0 or context[4] == 0 or context[5] == 0:
    usage_flags[1] = 0
  if context[2] == 0 or context[6] == 0 or context[7] == 0:
    usage_flags[2] = 0
  
  return usage_flags

def getNotes(rec_vector):
  genre_string = getNote4Genre(rec_vector) 
  bpm = rec_vector[12]*133,
  mood = getNote4Mood(rec_vector)

  return (genre_string, bpm[0], mood)
  
def getNote4Genre(rec_vector):
  genre_string = ""
  for i in range(0, 12):
    if (rec_vector[i] > 0.66):
      genre_string+= config["genres"][i]+", "
    elif (rec_vector[i] > 0.33):
      genre_string+= "Some "+config["genres"][i]+", "
    elif (rec_vector[i] > 0):
      genre_string+= "A bit of "+config["genres"][i]+", "
  
  return genre_string

def getNote4Mood(rec_vector):
  valence = rec_vector[13]
  arousal = rec_vector[14]

  moods = pd.read_csv("hybrid/moods.csv")

  moods["similarity"] = cosine_similarity(
    moods[["valence","arousal"]],
    [[valence,arousal]])

  sorted_by_similarity = moods.sort("similarity", ascending = 0)
  top_1 = sorted_by_similarity.head(n=1)
  top_1_as_list = top_1["mood"].tolist()[0]

  return top_1_as_list



