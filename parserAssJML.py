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
        :return: a list of lists. The number of elements in the list corresponds to the number
            of methods in 'code' that contains an assignable clause. Each element is a list of two elements:
                [number of assignable properties, number of properties being mentioned in the postcondition]
    """
    line = 0
    result = []
    while line < len(code):

        # check for assignable clause. If exists, retrieve all properties, check
        # the ensure part and print all information, including routine's name
        if code[line].find("assignable") >= 0:
            properties = code[line][code[line].find("assignable") + 10:].split(",")

            # check for 'nothing'. If so, there is no need to look for it in the
            # ensure part

            # retrieve the ensure part
            line += 1  # right after the assignable clause (ignore 'assignable_redundantly')

            if len(properties) == 1 and properties[0].find("nothing") >= 0:
                print("assignable \\nothing")
            else:
                result.append([len(properties), 0])
                if code[line].find("assignable_redundantly") > 0:
                    line += 1
                ensure = ""
                if code[line].find("ensures") >= 0:
                    while code[line].find("ensures") >= 0 or code[line].find(";") >= 0:
                        ensure += code[line] + "\n"
                        line += 1
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
                        result[-1][1] += 1
                        print("found: ", end='')
                    # checking model queries
                    elif name in model_queries and p in model_queries[name]:
                        mq_find = False
                        for mq in model_queries[name][p]:
                            if ensure.find(mq) >= 0:
                                mq_find = True
                                break
                        if mq_find:
                            print("MQ found:", end = '')
                            result[-1][1] += 1
                        else:
                            print("no found:", end = '')
                    elif name in ignore and p in ignore[name]:
                        print("Query ignore:", end = '')
                        result[-1][1] += 1
                    else:
                        print("CHECK!: ", end = '')
                    print(p)
        # name of the method
        elif code[line].find("@*/") >= 0:
            line += 1
            print(code[line])
            # assert c(result)
        line += 1
    return result


def get_JavaJML_code():
    """
    JavaJML code is taking from the official JML web-side
    """
    result_scraper_file = open("venv/sources/resultScraper", "r")
    scrape_info = eval(result_scraper_file.readline())
    result_scraper_file.close()
    #urls = ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlexec/samples/ArcType.jml',
    #        'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlexec/samples/Digraph.jml',
    #        'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLFloat.java'
    #        ]
    scrape_info = {'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/AbstractFilteringStrategyDecorator.java':
         ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/AbstractFilteringStrategyDecorator.java']
         }
    result = []
    report = []
    for i in scrape_info:
        urls = scrape_info[i]

        for url in urls:
            print("Evaluating: " + url)
            headers = {
                "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
            page = requests.get(url, headers=headers)

            soup = BeautifulSoup(page.content, 'html.parser')
            # fix some of the results
            # fixes are related to getting the information from the web. An alternative would be to download the
            # the file and evaluate (decided not to do it as the number of files is not big)
            try:
                inter_results = read_info(soup.contents[0].split("\n"), url)
            except:
                try:
                    inter_results = read_info(soup.contents[1].string.split("\n"), url)
                except:
                    try:
                        inter_results = read_info(soup.contents[1].contents[0].split("\n"), url)
                    except:
                        try:
                            inter_results = [[0, 0]]
                        except:
                            # assert len(soup.contents) == 1
                            assert False

            print(url)
            print(inter_results)
            if not c(inter_results):
                report.append(url)
            result += inter_results
    print("No mentions:")
    print(report)
    return result

# model queries are variable representation from abstraction to concrete. These queries as
# represented in JML via 'represents'
model_queries = {
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/AbstractExtensibleStrategyDecorator.java':
    {'addedData': ['defaultData'],
     'objectState': ['defaultData']},
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/AbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    }
}

# the analysis ignores the following queries for different reasons
# i) the query is set up in JML: //@ set owner = null;
ignore = {
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLFloat.java':['owner']
}




def c(l):
    for i in l:
        if i[0] > i[1]:
            return False
    return True

print(get_JavaJML_code())

# read_info(c.split("\n"), "PlusAccount.jml")
