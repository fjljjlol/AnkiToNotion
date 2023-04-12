import csv
from enum import Enum


class TextType(Enum):
    TEXT = 1
    EXTRA = 2


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

    def starting_index_of_substr(self, substr: str) -> []:
        return [i for i in range(len(self.text)) if self.text.startswith(substr, i)]

    # Removes start-end inclusive from self.text
    def remove_range(self, start: int, end: int, text_type: TextType, replace: str = ""):
        if text_type == TextType.TEXT:
            self.text = self.text[:start] + replace + self.text[end:]
        else:
            self.extra = self.extra[:start] + replace + self.extra[end:]

    # Returns list of clozures. Optionally removes them from self.text and replaces them with a string
    def get_clozures(self, remove:bool = False, replace:str = "") -> []:
        starting_indices = self.starting_index_of_substr("`{{")
        closing_indices = self.starting_index_of_substr("}}`")
        closing_indices = [i + 3 for i in closing_indices]

        clozures = []

        for start, end in zip(reversed(starting_indices), reversed(closing_indices)):
            clozures.append(Clozure(self.text[start:end]))
            if remove:
                self.remove_range(start, end, TextType.TEXT, replace)

        return clozures

    def clozure_bolding(self):
        clozures = self.get_clozures(True, "cumclozuregoesherelol")

        for clozure in clozures:
            if "**" in clozure.text:
                clozure.text = clozure.text.replace("**", "")
                clozure.text = "**"+clozure.text +"**"

        for cloz in reversed(clozures):
            self.text = self.text.replace("cumclozuregoesherelol", cloz.text, 1)

        print(self.text)

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
