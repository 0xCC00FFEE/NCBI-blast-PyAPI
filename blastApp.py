#!/usr/bin/env python3
try:
    from time		import sleep
    from sys	 	import exc_info, argv
    from bs4		import BeautifulSoup as BSoup
    from requests 	import post, get
    import re
except ImportError:
    print("[!] Error: One or more library(ies) wasn't found!")
    exit(-1)

# Defining the Restful API URI and connection parameters
blastURI = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi"
headers  = {"Content-Type":"application/x-www-form-urlencoded"}

# Dictionary with the available databases for each Blast application, along with regex expressions to validate the nucleotide/aa sequence
parser = {
    'blastn':{'regex':r'[^A|C|G|T]', 'db':['nt','refseq_select','refseq_genomes','wgs','est','env_nt','tsa_nt','patnt','pdbnt','refseqgene','vector','gss','dbsts']},
    'blastp':{'regex':r'[J|O|U|X|\W]', 'db':['nr', 'refseq_select', 'refseq_protein', 'landmark', 'swissprot', 'pataa', 'pdb', 'env_nr', 'tsa_nr']},
    'blastx':{'regex':r'[^A|C|G|T]', 'db':['nr', 'refseq_select', 'refseq_protein', 'landmark', 'swissprot', 'pataa', 'pdb', 'env_nr', 'tsa_nr']}
}

def runQuery(application, db, sequence):
    data = "CMD=Put&PROGRAM={application}&DATABASE={db}&QUERY={sequence}".format(application=application, db=db, sequence=sequence)

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

if __name__ == '__main__':
    if len(argv) != 4:
        print("[~] Usage:\n{0} <Amino Acids or Nucleotide Sequence> <Database> <Blast Application>\n".format(argv[0]))
        exit(0)
    seq = argv[1]
    db = argv[2]
    application = argv[3]
    
    # Argument validation
    if application not in parser.keys():
        print('[!] Invalid program')
        exit(0)
    if db not in parser[application]['db']:
        print('[!] Invalid database')
        exit(0)
    if re.findall(parser[application]['regex'], seq):
        print('[!] Invalid sequence for the selected application')
        exit(0)

    runQuery(application, db, seq)