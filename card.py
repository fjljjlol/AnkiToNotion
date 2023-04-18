import csv
from enum import Enum
import os
import shutil


class TextType(Enum):
    TEXT = 1
    EXTRA = 2
    ALL = 3


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

    def replace(self, text: str, repl: str = "", ttype: TextType = TextType.ALL):
        if ttype == TextType.ALL or ttype == TextType.TEXT:
            self.text = self.text.replace(text, repl)

        if ttype == TextType.ALL or ttype == TextType.EXTRA:
            self.extra = self.extra.replace(text, repl)

    def starting_index_of_substr(self, substr: str, ttype: TextType) -> []:
        if ttype == TextType.TEXT:
            return [i for i in range(len(self.text)) if self.text.startswith(substr, i)]
        else:
            return [i for i in range(len(self.extra)) if self.extra.startswith(substr, i)]

    # Removes start-end inclusive from self.text
    def remove_range(self, start: int, end: int, text_type: TextType, replace: str = ""):
        if text_type == TextType.TEXT:
            self.text = self.text[:start] + replace + self.text[end:]
        else:
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

    # creates images if they do not exist. Does this by copying the image passed in.
    def get_images(self, default: str):
        indices = self.starting_index_of_substr("src=", TextType.EXTRA)

        images = []

        for i in indices:
            rest = self.extra[i + 5:]
            images.append(rest[:rest.index("\"")])

        for i in images:
            exists = os.path.isfile(i)

            if not exists:
                shutil.copy(default, i)

    def do_extra_special(self):
        self.extra = self.extra.replace("<div style=\"font-weight: bold; \">", "")

    def do_special(self):
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


def get_cards(file: str) -> []:
    cards = []
    first = True
    with open(file, errors='replace') as file:
        tsv_file = csv.reader(file, delimiter="\t")

        # printing data line by line
        for line in tsv_file:
            if first:
                first = False
                continue
            line[3] = line[3].replace("�", " ")
            line[4] = line[4].replace("�", " ")
            cards.append(Card(line[3], line[4]))

    return cards
