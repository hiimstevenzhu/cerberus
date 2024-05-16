from keyword_search import keyword_identification as ki

txt = "Hello my name is John I am a student at the University of Toronto I am studying computer science Sir stop sir we do not want to hurt you"
txt2 = "Put your hands up Sir stop sir we do not want to hurt you we want you to stop moving Do not move Test Test Test You and I"
clusterName = "red"

txt3 = "Hello. My name is John. I am a student at the University of Toronto. I am studying, computer science. Sir stop sir. We do not want to hurt you"
txt4 = "Sir stop Sir. Sir Stop Sir. Testing testing, my name is Steven."

keywords = ["Sir stop", "stop sir", "Sir stop Sir", "I", "you", "am"]
updKeywords = ["Test", "a", 'do not move', 'don\'t move', 'put your hands up']

ki.insertCluster(keywords, clusterName)
ki.printCluster(clusterName)

ki.matchKeywords(txt3, clusterName)

