"""
This script reads all java and jml codes that where previously retrieved using scraper.py. This script checks whether
all properties listed in the JML assignable clause are mentioned (outside the old keyword) in the JML ensures clause.
The main idea is to have an informal review about how frame conditions can be managed in practice. The hypothesis
is that the postcondition of a routine gives information of what the routine is allowed to change.

The script is not a proper parser as there is no need for it. The script simple finds the line where the
keyword 'assignable' is and retrieves all properties that are separated by commas. Then, it checks if those
properties are being mentioned in the next 'ensure' part.

In JML, model queries are possible. This is being handled manually via dictionary 'model_query'.
"""
import re
# getting information from the web
import requests
# parsing html docs
from bs4 import BeautifulSoup


def read_info(code, name):
    """
        extracts from code all properties listed in the
         JML assignable clauses and checks whether they are mentioned in the
         postcondition of the routine.
         :param code: java or jml code (string)
         :param name: url of the name of the file being checked, needed for model queries  (string)
        :return:
    """
    line = 0
    print (model_queries)
    while line < len(code):

        # check for assignable clause. If exists, retrieve all properties, check
        # the ensure part and print all information, including routine's name
        if code[line].find("assignable") >= 0:
            properties = code[line][code[line].find("assignable") + 10:].split(",")

            # retrieve the ensure part
            line += 1  # right after the assignable clause (ignore 'assignable_redundantly')
            # TODO: check code with more than one ensure part
            if code[line].find("assignable_redundantly") > 0:
                line += 1
            if code[line].find("ensures") >= 0:
                ensure = code[line]
                while code[line].find(";") == -1:
                    line += 1
                    ensure += "\n"+code[line]
                # ignore 'old' and 'not_modified'
                ensure = re.sub(r'\\old\(\w+\)', "", ensure)
                ensure = re.sub(r'\\not_modified\(\w+\)', "", ensure)
            else:
                print("W: Assignable without an ensure: ")
                print(properties)
                print(code[line])

            print("ensure: ")
            print(ensure)
            # for each property, check if it is in the ensure part
            for pp in properties:
                p = pp.strip().replace(";", "")
                if ensure.find(p) >= 0:
                    print("found: ", end='')
                elif name in model_queries and p in model_queries[name]: # checking model queries
                    mq_find = False
                    for mq in model_queries[name][p]:
                        if ensure.find(mq) >= 0:
                            mq_find = True
                            break
                    if mq_find:
                        print("MQ found:", end = '')
                    else:
                        print("no found:", end = '')
                else:
                    print("CHECK!", end = '')
                print(p)
        elif code[line].find("@*/") >= 0:
            line += 1
            print(code[line])
        line += 1



def get_JavaJML_code():
    """
    JavaJML code is taking from the official JML web-side
    """
    f = open("venv/sources/resultScraper", "r")
    d = eval(f.readline())
    f.close()
    # test:
    #1. 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlexec/samples/ArcType.jml'
    #2. 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlexec/samples/Digraph.jml'
    #3. 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLFloat.java'

    url = 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlexec/samples/Digraph.jml'
    headers = {
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')
    assert len(soup.contents) == 1
    read_info(soup.contents[0].split("\n"), url)


model_queries = {

}

get_JavaJML_code()

# read_info(c.split("\n"), "PlusAccount.jml")
