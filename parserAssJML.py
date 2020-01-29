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
        if code[line].find("assignable") >= 0 and code[line].find("@") >= 0:

            properties = code[line][code[line].find("assignable") + 10:].split(",")

            line += 1
            while code[line].find("assignable") >= 0:
                if code[line].find("assignable_redundantly") == -1:
                    properties += code[line][code[line].find("assignable") + 10:].split(",")
                line += 1

            # check for 'nothing'. If so, there is no need to look for it in the
            # ensure part

            # retrieve the ensure part
            # right after the assignable clause (ignore 'assignable_redundantly')

            if len(properties) == 1 and properties[0].find("nothing") >= 0:
                print("assignable \\nothing")
            elif len(properties) == 1 and properties[0].find("not_specified") >= 0:
                print("assignable \\not_specified")
            elif len(properties) == 1 and (properties[0].find("this.*") >= 0 or properties[0].find("everything") >= 0):
                # it lets assigned everything
                result.append([1, 1])
            else:
                result.append([len(properties), 0])
                if code[line].find("modifies") > 0:
                    line += 1
                ensure = ""
                if code[line].find("ensures") >= 0:
                    while code[line].find("ensures") >= 0:
                        ensure += code[line] + "\n"
                        while code[line].find(";") == -1 or code[line].find("forall") >= 0 or code[line].find("exists") >= 0:
                            line += 1
                            ensure += code[line] + "\n"
                        line += 1

                    # ignore 'old' and 'not_modified'
                    ensure = re.sub(r'\\old\(\w+\)', "", ensure)
                    # ensure = re.sub(r'\\not_modified\(\w+\)', "", ensure)
                else:
                    print("W: Assignable without an ensure: ")
                    print(properties)
                    print(code[line])

                print("ensure: ")
                print(ensure)
                # for each property, check if it is in the ensure part
                for pp in properties:
                    p = pp.strip().replace(";", "").replace("\\", "")
                    if ensure.find(p) >= 0:
                        result[-1][1] += 1
                        print("found: ", end='')
                    # checking datagroups
                    elif name in jml_datagroup and p in jml_datagroup[name]:
                        result[-1][1] += 1
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

    # testing
    l = ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/AbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/AbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteNonNegativeIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleNonNegativeIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/EmptyNewObjectIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatNonNegativeIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IndefiniteIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IndefiniteIteratorUtilities.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntNonNegativeIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IteratorAbstractAdapter.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LimitedTestSuite.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongNonNegativeIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/NonNullIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortAbstractFilteringIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortAbstractFilteringStrategyDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortCompositeIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortCompositeStrategy.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortNonNegativeIteratorDecorator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortStrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/StrategyType.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_AbstractFilteringIteratorDecorator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_AbstractFilteringStrategyDecorator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_CompositeIterator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_CompositeStrategy.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_NonNegativeIteratorDecorator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_StrategyType.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLBag.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLBag.sh', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLBagEnumerator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLByte.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLChar.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLDouble.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEnumerationToIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsBag.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsBagEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsSequenceEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsSetEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToEqualsRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToEqualsRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToObjectRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToObjectRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToValueRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToValueRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLFiniteInteger.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLFloat.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLInteger.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLLong.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectBag.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectBagEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectSequenceEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectSetEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToEqualsRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToEqualsRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToObjectRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToObjectRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToValueRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToValueRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLRelationEnumerator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLRelationImageEnumerator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLSequence.sh', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLSequenceEnumerator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLSet.sh', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLSetEnumerator.java-generic', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLShort.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLString.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueBag.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueBagEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueSequenceEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueSetEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToEqualsRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToEqualsRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToObjectRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToObjectRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToValueRelationEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToValueRelationImageEnumerator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/resolve/NaturalNumber.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/digraph/SearchableDigraph.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/digraph/SearchableNode.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/dirobserver/DirObserver.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/jmlkluwer/PriorityQueue.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/jmlrefman/Heavyweight.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/jmlrefman/Invariant.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/jmlrefman/Lightweight.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/iterator/Iterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/iterator/RestartableIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/DLList.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/E_SLList.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/ListIterator.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/ListIterator.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/SLList.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/node/DLNode.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/node/DLNode.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list2/OneWayList.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list2/TwoWayIterator.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list2/TwoWayIterator.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list2/TwoWayIterator.refines-jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list2/TwoWayList.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list3/OneWayList.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list3/TwoWayIterator.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list3/TwoWayIterator.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list3/TwoWayIterator.refines-jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list3/TwoWayList.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node/OneWayNode.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node/TwoWayNode.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node/TwoWayNode.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node2/DualLink.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node2/Link.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node2/TwoWayNode.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node2/TwoWayNode.jml-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/misc/Proof.java-refined', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/prelimdesign/PlusAccount.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/prelimdesign/USMoney.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/reader/BlankReader.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/reader/BufferedReader.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/reader/Reader.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/sets/IntegerSetAsTree.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/stacks/BoundedStack.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/stacks/BoundedStackImplementation.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/stacks/BoundedStackInterface.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/stacks/BoundedStackInterface.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/stacks/UnboundedStackAsArrayList.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/table/TableImplementation.java', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/DataInput.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/File.refines-java', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/InputStream.refines-java', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/OutputStream.refines-java', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/PrintStream.refines-java', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Class.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Error.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/InternalError.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Number.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Object.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Package.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Runnable.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/String.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/StringBuffer.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/System.jml', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/net/URI.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/net/URL.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/sql/Date.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/sql/Time.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/AbstractList.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/ArrayList.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/BitSet.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Calendar.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Collection.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Date.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Enumeration.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/GregorianCalendar.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/HashMap.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/HashSet.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Hashtable.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Iterator.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/LinkedList.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/List.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/ListIterator.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Map.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Set.spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Stack.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/TreeSet.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/util/Vector.refines-spec', 'http://www.eecs.ucf.edu/~leavens/JML-release/specs/javax/servlet/ServletRequest.refines-spec']
    ind = 174 # not checked yet
    scrape_info = {
        l[ind]:
            [l[ind]]
        }

    #scrape_info = {'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharCompositeStrategy.java':
    #     ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharCompositeStrategy.java']
    #     }

    result = []
    report = []
    for i in scrape_info:
        urls = scrape_info[i]
        for url in urls:
            if url in ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanCompositeIterator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanCompositeIterator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/BooleanAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/AbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortAbstractFilteringStrategyDecorator.java',
                'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_AbstractFilteringStrategyDecorator.java-generic'
                       ]:
                # inner classes
                continue
            elif url in ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLBag.java-generic',
                         'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsBag.java',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectBag.java',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/jmlrefman/Heavyweight.java',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/jmlrefman/Lightweight.java',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list2/TwoWayIterator.refines-jml',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list3/TwoWayIterator.refines-jml',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Error.jml',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/Object.jml',
                        'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/System.jml'
                         ]:
                # unusual JML constructs
                continue
            elif url in ['http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/misc/Proof.java-refined' #exercise
                         ]:
                continue
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
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteAbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ByteCompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharAbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CharCompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/CompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleAbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/DoubleCompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatAbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/FloatCompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntAbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/IntCompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongAbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/LongCompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortAbstractFilteringIteratorDecorator.java':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/ShortCompositeIterator.java':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_AbstractFilteringIteratorDecorator.java-generic':
    {
        'objectState': ['rawElems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/jmlunit/strategies/_ValueType_CompositeIterator.java-generic':
    {
        'currentIterator': ['iters']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEnumerationToIterator.java':
    {
        'moreElements': ['theEnumeration']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLFiniteInteger.java':
    {
        'sign': ['is_infinite']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueBag.java':
    {
        'the_list': ['objectState']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/jmlkluwer/PriorityQueue.java':
    {
        'levels.theCollection': ['levels']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list1/node/DLNode.jml':
    {
        'nxtNode.prevNode': ['nxtNode']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list2/TwoWayIterator.jml':
    {
        'currElem': ['theList'],
        'uniteratedElems': ['theList'],
        'iteratedElems': ['theList']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/list3/TwoWayIterator.jml':
    {
        'currElem': ['theList'],
        'uniteratedElems': ['theList'],
        'iteratedElems': ['theList']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node/OneWayNode.jml-refined':
    {
        'entries': ['allButFirst']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node/TwoWayNode.jml':
    {
        'nxtNode.prevNode': ['nxtNode']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node/TwoWayNode.jml-refined':
    {
        'entries': ['prevEntries']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node2/DualLink.jml-refined':
    {
        'entries': ['dualNode']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node2/Link.jml-refined':
    {
        'entries': ['node']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/list/node2/TwoWayNode.jml':
    {
        'nxtNode.prevNode': ['nxtNode']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/reader/BufferedReader.java':
    {
        'state': ['cur']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/sets/IntegerSetAsTree.java':
    {
        'theSet': ['isEmpty', 'rootValue', 'left', 'right']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/stacks/BoundedStackInterface.java':
    {
        'size': ['theStack']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/stacks/UnboundedStackAsArrayList.java':
    {
        'theStack': ['elems']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/table/TableImplementation.java':
    {
        'entries': ['table']
    },
'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/lang/StringBuffer.jml':
    {
        'dst[dstBegin .. dstBegin+srcEnd-srcBegin]': ['dst']
    }
}

# the analysis ignores the following queries for different reasons
# i) the query is set up in JML: //@ set owner = null;
ignore = {
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLFloat.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLByte.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLChar.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLDouble.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEnumerationToIterator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToEqualsRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToEqualsRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToObjectRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToObjectRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToValueRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLEqualsToValueRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLInteger.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLLong.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToEqualsRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToEqualsRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToObjectRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToObjectRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToValueRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLObjectToValueRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLRelationEnumerator.java-generic':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLRelationImageEnumerator.java-generic':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLShort.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLString.java':['owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueBag.java':['elementType', 'containsNull', 'owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToEqualsRelationEnumerator.java':['elementType', 'returnsNull', 'owner'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToEqualsRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToObjectRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToObjectRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToValueRelationEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/JMLValueToValueRelationImageEnumerator.java':['elementType', 'returnsNull'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/models/resolve/NaturalNumber.java':['owner']
}


jml_datagroup = {
    'http://www.eecs.ucf.edu/~leavens/JML-release/org/jmlspecs/samples/dirobserver/DirObserver.java': ['obsState'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/DataInput.refines-spec': ['input'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/File.refines-java': ['fileSystem'],
    'http://www.eecs.ucf.edu/~leavens/JML-release/specs/java/io/InputStream.refines-java': ['objectState']
}

def c(l):
    for i in l:
        if i[0] > i[1]:
            return False
    return True

print(get_JavaJML_code())

# read_info(c.split("\n"), "PlusAccount.jml")
