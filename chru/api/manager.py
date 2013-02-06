# -*- coding: utf-8 -*-

from chru.version import __supported__

import json
import pysqlw

class cli:
    """ A really nasty and horrible CLI implementation
        of an API key manager. I should probably improve
        it some day, but it'll work for now.
    """

    def __init__(self, settings):
        self.settings = json.load(settings)
        if not "_version" in self.settings \
                or self.settings["_version"] not in __supported__:
            raise ValueError("The given settings file is not supported.")
        settings.close()

    def sqlw(self):
        return pysqlw.pysqlw(db_type="sqlite", db_path=self.settings["sql_path"])

    def menu(self):
        items = [(1, "List API keys"),
                 (2, "Add a new key"),
                 (3, "Delete a key")]
        print "What do you want to do? (Ctrl-C to exit)"

        for k, v in items:
            print str(k) + '.', v

        try:
            option = int(raw_input("# "))
        except ValueError as e:
            print "That's not a number... Try again."
            return self.menu()

        for k, v in items:
            if option == k:
                return option

        print "That's no good, try again.."
        return self.menu()

    def api_list(self):
        rows = self.sqlw().get(self.settings["_schema"]["api"])
        print ""
        if len(rows) > 0:
            print "List of API keys:"
            for row in rows:
                print "#{0}: {1} ({2} {3})".format(row["id"], row["key"], row["name"], row["email"])
        else:
            print "No API keys were found! :("

    def api_add(self):
        print "\nPlease provide info about API key owner:"
        correct_info = False
        owner = False
        email = False
        key = self.make_random()
        while not correct_info:
            owner = str(raw_input(" name: "))
            email = str(raw_input("email: "))
            print ":: {0} ({1})\n".format(owner, email)
            correct = str(raw_input("Is this correct? [Y/n] ")).lower()
            correct_info = correct in ("", "y", "ye", "yes", "yup", "correct-a-mundo")
        data = {
            "key": key,
            "name": owner,
            "email": email
        }
        if self.sqlw().insert(self.settings["_schema"]["api"], data):
            print "Successfully added API key!"
            print ":: ", key

    def api_delete(self):
        print "\nWhat number is the key? (As provided by the listing): ('q' to go back)"
        num = False
        while not num:
            try:
                n = raw_input("># ")
                if n.lower() in ("q", "quit"):
                    return
                num = int(n)
            except ValueError as e:
                print "That isn't a number, try again."
        if len(self.sqlw().where("id", num).get(self.settings["_schema"]["api"])) != 1:
            print "That API key doesn't seem to exist, sorry."
            return

        if self.sqlw().where("id", num).delete(self.settings["_schema"]["api"]):
            print "Successfully deleted API key #{0}!".format(num)
        else:
            print "Unable to delete API key. :("


    def make_random(self, length=32):
        import string, random
        parts = string.uppercase + string.lowercase + string.digits
        return "".join(random.choice(parts) for x in range(length))

    def main(self):
        funcs = {
            1: self.api_list,
            2: self.api_add,
            3: self.api_delete
        }
        try:
            while True:
                option = self.menu()
                funcs[option]()
                print ""
        except KeyboardInterrupt as e:
            print ""
            print "Goodbye!"

class dump:
    def __init__(self, settings):
        self.settings = json.load(settings)
        if not "_version" in self.settings \
                or self.settings["_version"] not in __supported__:
            raise ValueError("The given settings file is not supported.")
        settings.close()

    def sqlw(self):
        return pysqlw.pysqlw(db_type="sqlite", db_path=self.settings["sql_path"])

    def dump(self):
        rows = self.sqlw().get(self.settings["_schema"]["api"])
        data = { "keys": [] }
        for row in rows:
            data["keys"].append(row)
        print data