import os
import time
from .index import Index
from .index_config import IndexConfig
from .boolean_query import BooleanQuery

class ReplClient:
    '''Read-Eval-Print-Loop client for the index.'''
    def __init__(self, working_dir = None):
        if working_dir:
            self._working_dir = working_dir
        else:
            self._working_dir = os.getcwd()
        self.index = None
        self._actions = {
            'createIndex': CreateIndexAction,
            'boolean': BooleanQueryAction
        }

        self._startREPL()


    def _startREPL(self):
        usrInput = ""
        while(usrInput != "exit"):
            usrInput = input("> ")
            if not usrInput:
                continue
            try:
                action = self._parseInput(usrInput)
                action.execute()
            except Exception as e:
                print("Error: " + str(e))
        print("Exiting...")

    def _parseInput(self, usrInput):
        split = usrInput.split()
        command = split[0]
        arguments = split[1:] if len(split) > 1 else []
        if command in self._actions:
            actionFactory = self._actions[command]
            return actionFactory(self, arguments)
        else:
            raise ValueError("<" + command + "> unknown command.")


class Action:
    def execute(self):
        raise NotImplementedError("Wrong action.")


class CreateIndexAction(Action):
    def __init__(self, client, arguments):
        self._client = client
        if len(arguments) < 1 or len(arguments) > 2:
            raise ValueError(CreateIndexAction.help())
        self._data_files = arguments[0].split(";")
        self._stop_words_file = arguments[2] if len(arguments) == 2 else ""

    def execute(self):
        indexConfig = IndexConfig(self._stop_words_file)
        print("Indexing files...")
        t_start = time.time()
        self._client.index = Index(self._data_files, indexConfig)
        print("Index has been created in " + str(time.time() - t_start) + " seconds.")

    @staticmethod
    def help():
        return '''Wrong use.
        Example: createIndex data_file1;data_file2 stop_word_file'''


class BooleanQueryAction(Action):
    def __init__(self, client, arguments):
        if not arguments:
            raise ValueError(BooleanQueryAction.help())
        if not client.index:
            raise ValueError("Create or load an index first.")
        queryText = "".join(arguments)
        self._query = BooleanQuery(queryText)
        self._query.setIndex(client.index)

    def execute(self):
        t_start = time.time()
        docs = self._query.execute()
        duration = time.time() - t_start
        print("Query executed in " + str(duration) + " seconds and returnd " + str(len(docs)) + " results.")
        print(docs)

    @staticmethod
    def help():
        return '''Wrong use.
        Example: boolean (word1 * !word2) + word3'''