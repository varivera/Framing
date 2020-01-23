# Retrieves information from the web (JML code)

# getting information from the web
import requests
# parsing html docs
from bs4 import BeautifulSoup
# measuring time
import time


def check(lst, e):
    """
    checks whether 'e' is a substring of any element of 'lst'
    """
    for elem in lst:
        if e.find(elem) >= 0:
            return True
    return False


def retrieve(URL, headers, result):
    """
    Store in 'result' a list of all Java and JML files found in URL. It does also
    check the inner links (folders)
    :param URL: parent URL
    :param headers: headers of the browser (open a browser and type 'my user agent')
    :param result: dictionary storing Java and JML urls
    """
    if URL in result:
        # no need to check again (avoid infinite loop)
        pass
    else:
        result[URL] = []
        print("Analysing " + URL)
        page = requests.get(URL, headers=headers)

        soup = BeautifulSoup(page.content, 'html.parser')

        # list of files (including folders)
        lst = soup.find_all(name="a")

        for link_name in lst:
            url_code = URL + link_name.attrs['href']

            # analyse only know extensions
            ext = [".java", ".jml", ".sh", ".spec", ".refines-java", ".refines-jml", ".refines-spec"]
            if check(ext, link_name.attrs['href']):
                page_code = requests.get(url_code, headers=headers)
                soup = BeautifulSoup(page_code.content, 'html.parser')
                soup.prettify()
                result[URL].append(url_code)
                # parser (parserAssJML.py)
            elif link_name.attrs['href'][-1] == "/":
                # it is a directory. Go recursively (unless Parent Directory).
                if 'Parent Directory' in link_name.contents:
                    pass
                else:
                    retrieve(url_code, headers, result)
            else:
                # check other extensions (except known)
                known = ['.class', '.html', '.stamp', 'Makefile', '?', 'README', 'Make.CommonDefs', '.properties', 'compare-expected']
                if not check(known, link_name.attrs['href']):
                    print("new ext: "+ url_code)


# list of JML samples (from the official site)
sample = ['http://www.eecs.ucf.edu/~leavens/JML-release/org/', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/']
# sample = ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/dbc/']
headers = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
result = {}

t1 = time.time()
for URL in sample:
    retrieve(URL, headers, result)
t2 = time.time()
print(result)
print(round(t2-t1), end=" secs")
