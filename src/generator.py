import itertools

def generateStrings(maxLength):
  # In this project we assume that we consider only strings made of lower case letters
  # We could add upper case letters but the number of strings/generated payloads would be really high
  chars = "abcdefghijklmnopqrstuvwxyz"
  generatedPayloads = []
  for length in range(maxLength):
    subPayloads = []
    for item in itertools.product(chars, repeat=length+1):
      subPayloads.append("".join(item))
    generatedPayloads = generatedPayloads + subPayloads
  return generatedPayloads
