"""
This script reads all java and jml files from a folder and checks whether all properties listed
in the JML assignable clause are mentioned (outside the old keyword) in the JML ensures clause. The main
idea is to have an informal review about how frame conditions can be managed in practice. The hypothesis
is that the postcondition of a routine gives information of what the routine is allowed to change.

The script is not a proper parser as the there is no need for it. The script simple finds a line where the
keyword 'assignable' is and retrieves all properties that are separated by commas. Then, it checks if those
properties are being mentioned in the next 'ensure' part.

In JML, model queries are possible. This is being handled manually
"""
import re


def read_file(path, name):
    """
        opens and reads the file 'name' and extracts all properties listed in the
         JML assignable clauses and checks whether they are mentioned in the
         postcondition of the routine.
         :param path: path of the file
         :param name: name of the file (file should have extension .java or .jml)
            the type is String
        :return:
    """
    f = open(path+name, "r")
    line = f.readline()
    while line:

        # check for assignable clause. If exists, retrieve all properties, check
        # the ensure part and print all information, including routine's name
        if line.find("assignable") >= 0:
            properties = line[line.find("assignable") + 10:].split(",")

            # retrieve the ensure part
            line = f.readline()  # right after the assignable clause (ignore 'assignable_redundantly')
            if line.find("assignable_redundantly") > 0:
                line = f.readline()
            if line.find("ensures") >= 0:
                ensure = line
                while line.find(";") == -1:
                    line = f.readline()
                    ensure += line
                # ignore 'old' and 'not_modified'
                ensure = re.sub(r'\\old\(\w+\)', "", ensure)
                ensure = re.sub(r'\\not_modified\(\w+\)', "", ensure)
            else:
                print("W: Assignable without an ensure: ")
                print(properties)
                print(line)

            print("ensure: ")
            print(ensure)
            # for each property, check if it is in the ensure part
            for pp in properties:
                p = pp.strip().replace(";", "")
                if ensure.find(p) >= 0:
                    print("found: ", end = '')
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
        line = f.readline()
    f.close()


model_queries = {
    "PlusAccount.jml": {
        "credit": ["savings", "checking"]
    }
}

read_file("venv/sources/","PlusAccount.jml")
