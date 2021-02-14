#!/usr/bin/env python3
try:
    from time		import sleep
    from sys	 	import exc_info, argv
    from bs4		import BeautifulSoup as BSoup
    from requests 	import post, get
except ImportError:
    print("[!] Error: One or more library(ies) wasn't found!")
    exit(-1)

if len(argv) != 2:
    print("[~] Usage:\n{0} <Amino Acids Sequence>\n".format(argv[0]))
    exit(0)

# Defining the Restful API URI and connection parameters
blastURI = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi"
headers  = {"Content-Type":"application/x-www-form-urlencoded"}
# protDBs  = ['nr', 'refseq_select', 'refseq_protein', 'landmark', 'swissprot', 'pataa', 'pdb', 'env_nr', 'tsa_nr']
data     = "CMD=Put&PROGRAM=blastx&DATABASE=swissprot&QUERY={0}".format(argv[1])

try:
    req = post(blastURI, headers=headers, data=data)
except (Exception) as exc:
    exc_type, exc_obj, exc_tb = exc_info()
    print("[!]\nException: {0}\nMessage: {1}\nLine Number: {2}".format( \
         type(exc), exc, exc_tb.tb_lineno))
    exit(-1)

if req.status_code != 200:
    print("[!] [{0}]\n{1}".format(req.status_code, req.text))
    exit(0)

# Get request ID for results polling later
try:
    blastReqID = BSoup(req.text, 'lxml').findAll('input', {'type':'text'})[0]['value']
except:
    print("[!] Couldn't find the request ID value!\n")
    exit(0)

# Poll for results
blastPollURI = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get"+ \
               "&FORMAT_OBJECT=SearchInfo&RID={0}".format(blastReqID)
while True:
    sleep(5)
    req = get(blastPollURI)
    if req.text.find('Status=READY') != -1:
        break

if req.text.find('ThereAreHits=yes') == -1:
    print("[!] No results returned from Blast DB!")
    exit(0)

# Retrieve results
blastResURI = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get"+ \
              "&FORMAT_TYPE=Text&RID={0}".format(blastReqID)

# Write results to file
req = get(blastResURI)
with open('./results.txt', 'w+') as f:
    f.write(req.text)

print("[~] Results stored in file 'results.txt'")



