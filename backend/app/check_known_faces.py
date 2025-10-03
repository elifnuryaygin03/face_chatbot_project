import pickle

with open("../data/known_faces.pkl", "rb") as f:
    known_faces = pickle.load(f)

print(known_faces)