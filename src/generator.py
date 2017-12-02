import itertools

def generateStrings(maxLength):
  # In this project we assume that we consider only strings made of lower case letters
  # We could add upper case letters but the number of strings/generated payloads would be really high
  chars = "abcdefghijklmnopqrstuvwxyz"
  generatedPayloads = []
  for item in itertools.product(chars, repeat=maxLength):
    generatedPayloads.append("".join(item))
  return generatedPayloads

# Following in this file, we could have so other kind of generators in order to continue the analysis on kayak.com
