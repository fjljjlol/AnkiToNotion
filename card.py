import csv
from enum import Enum
import os
import shutil


class TextType(Enum):
    TEXT = 1
    EXTRA = 2
    OPTIONAL = 3
    ALL = 4
    NONE = 5


class Clozure:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


class Card:
    def __init__(self, text: str, extra: str):
        self.text = text
        self.extra = extra
        self.optionals = dict()

    def __repr__(self):
        opt = ""
        for name, o in self.optionals.items():
            opt += "\n"+name+": " + o
        return "Main: " + self.text + "\nExtra: " + self.extra + opt

    def has_optionals(self):
        return len(self.optionals) != 0

    def replace(self, text: str, repl: str = "", ttype: TextType = TextType.ALL):
        if ttype == TextType.ALL or ttype == TextType.TEXT:
            self.text = self.text.replace(text, repl)

        if ttype == TextType.ALL or ttype == TextType.EXTRA:
            self.extra = self.extra.replace(text, repl)

        if ttype == TextType.ALL or ttype == TextType.OPTIONAL:
            for name, val in self.optionals.items():
                self.optionals[name] = val.replace(text, repl)

    def starting_index_of_substr(self, substr: str, ttype: TextType, alt_input: str = "") -> []:
        if ttype == TextType.TEXT:
            return [i for i in range(len(self.text)) if self.text.startswith(substr, i)]
        if ttype == TextType.EXTRA:
            return [i for i in range(len(self.extra)) if self.extra.startswith(substr, i)]
        if ttype == TextType.NONE:
            return [i for i in range(len(alt_input)) if alt_input.startswith(substr, i)]

    # Removes start-end inclusive from self.text
    def remove_range(self, start: int, end: int, text_type: TextType, replace: str = ""):
        if text_type == TextType.TEXT:
            self.text = self.text[:start] + replace + self.text[end:]
        if text_type==TextType.EXTRA:
            self.extra = self.extra[:start] + replace + self.extra[end:]

    # Returns list of clozures. Optionally removes them from self.text and replaces them with a string
    def get_clozures(self, remove: bool = False, replace: str = "") -> []:
        starting_indices = self.starting_index_of_substr("`{{", TextType.TEXT)
        closing_indices = self.starting_index_of_substr("}}`", TextType.TEXT)
        closing_indices = [i + 3 for i in closing_indices]

        clozures = []

        for start, end in zip(reversed(starting_indices), reversed(closing_indices)):
            clozures.append(Clozure(self.text[start:end]))
            if remove:
                self.remove_range(start, end, TextType.TEXT, replace)

        return clozures

    def __get_images_helper(self, default: str, text: str):
        indices = self.starting_index_of_substr("src=", TextType.NONE, text)

        images = []

        for i in indices:
            rest = text[i + 5:]
            images.append(rest[:rest.index("\"")])

        for i in images:
            exists = os.path.isfile(i)

            if not exists:
                shutil.copy(default, i)

    # creates images if they do not exist. Does this by copying the image passed in.
    def get_images(self, default: str, ttype: TextType = TextType.ALL):
        if ttype == TextType.ALL or ttype == TextType.TEXT:
            self.__get_images_helper(default, self.text)

        if ttype == TextType.ALL or ttype == TextType.EXTRA:
            self.__get_images_helper(default, self.extra)

        if ttype == TextType.ALL or ttype == TextType.OPTIONAL:
            for name, val in self.optionals.items():
                self.__get_images_helper(default, val)


    def does_contain_only_images(self, text:str, debug: bool = False):
        text = text.replace("<br />", "")
        text = text.replace("<br/>", "")
        text = text.replace("<br>", "")
        text = text.replace("<i>", "")
        text = text.replace("</i>", "")

        if debug:
            # print(text)
            print()

        if text[0:4] == "<img" or text[0:4] == "<br " or text[0:4] == " <im" or text[0:3] == "<b>" or text[
                                                                                                          0:3] == "<u>":
            text = text[text.find(">") + 1:]
            # if everything breaks, the bug is here (because img text img and the loop bellow will corrupt everything)

            while text.find("<img") != -1:
                text = text[text.find(">") + 1:]

            text = text.replace(" ", "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("</span>", "")

            while text.find("<ahref") != -1:
                text = text[text.find(">") + 1:]
                text = text[text.find(">") + 1:]

            while text.find("<a href") != -1:
                text = text[text.find(">") + 1:]
                text = text[text.find(">") + 1:]

            if debug:
                # print("inside")
                print(text)
                print()

            return len(text) == 0

        return False

    def perform_only_image_detection(self, ttype: TextType = TextType.ALL, debug: bool = False):
        if ttype == TextType.TEXT or ttype==TextType.ALL:
            if self.does_contain_only_images(self.text, debug):
                self.text = "Text <br>" + self.text
        if ttype == TextType.EXTRA or ttype==TextType.ALL:
            if self.does_contain_only_images(self.extra, debug):
                self.extra = "Extra <br>" + self.extra
        if ttype== TextType.OPTIONAL or ttype==TextType.ALL:
            for name, optional in self.optionals.items():
                if self.does_contain_only_images(optional, debug):
                    self.optionals[name] = name + " <br>" + optional


    def do_extra_special(self):
        self.extra = self.extra.replace("<div style=\"font-weight: bold; \">", "")
        self.extra = self.extra.replace("<div style=\"display: inline !important;\">","")

    def do_text_special(self):
        self.text = self.text.replace("<div style=\"centerbox\"><div class=\"mnemonics\">", "")

    def clozure_bolding(self):
        clozures = self.get_clozures(True, "cumclozuregoesherelol")

        for clozure in clozures:
            if "**" in clozure.text:
                clozure.text = clozure.text.replace("**", "")
                clozure.text = "<b>" + clozure.text + "</b>"

            if "<b>" in clozure.text:
                clozure.text = clozure.text.replace("<b>", "")
                clozure.text = clozure.text.replace("</b>", "")
                clozure.text = "<b>" + clozure.text + "</b>"

            if "</i>" in clozure.text and "<i>" not in clozure.text:
                clozure.text = clozure.text.replace("</i>", "")
                clozure.text = clozure.text + "</i>"

            if "</b>" in clozure.text and "<b>" not in clozure.text:
                clozure.text = clozure.text.replace("</b>", "")
                clozure.text = clozure.text + "</b>"

        for cloz in reversed(clozures):
            self.text = self.text.replace("cumclozuregoesherelol", cloz.text, 1)

    """
    Also just removes underlined things
    """
    def initial_pruning(self):
        self.replace("\"\"", "\"")

        if len(self.extra) != 0:
            if self.extra[0] == "\"":
                self.extra = self.extra[1:]
            if self.extra[~0] == "\"":
                self.extra = self.extra[:-1]

        if len(self.text) != 0:
            if self.text[0] == "\"":
                self.text = self.text[1:]
            if self.text[~0] == "\"":
                self.text = self.text[:-1]

        for name, val in self.optionals.items():
            if len(val)==0:
                continue
            if val[0] == "\"":
                self.optionals[name] = val[1:]
                val = val[1:]
            if val[~0] == "\"":
                self.optionals[name] = val[:-1]

        self.replace("<div>", "")
        self.replace("</div>", "")
        if "<u>" in self.text:
            self.replace("<u>", "")
            self.replace("</u>", "")
            self.text=self.text.replace(" ","&nbsp;")
            self.text = self.text.replace("<br&nbsp;/>", "<br />")
        self.replace("</i> ", "</i>&nbsp;")
        self.replace(" <i>", "&nbsp;<i>")
        self.replace("</b> ", "</b>&nbsp;")
        self.replace(" <b>", "&nbsp;<b>")


def get_cards(file: str, optionals: [] = None) -> []:
    if optionals is None:
        optionals = []


    optionalsDict = dict()
    cards = []
    first = True
    with open(file, errors='replace') as file:
        tsv_file = csv.reader(file, delimiter="\t")

        # printing data line by line
        for line in tsv_file:
            if first:
                first = False
                for idx, s in enumerate(line):
                    if s in optionals:
                        optionalsDict[s] = idx
                continue
            line[3] = line[3].replace("�", " ")
            line[4] = line[4].replace("�", " ")
            c = Card(line[3], line[4])
            for name, line_number in optionalsDict.items():
                c.optionals[name] = line[line_number]
            cards.append(c)
    return cards
