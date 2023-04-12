import pypandoc
from card import *
from user import *
import yaml

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)[user]

cards = get_cards(config['tsv'])


# 1 cleanse the text
# print("Cleansing Text")
for card in cards:
    card.text = card.text.replace("\"\"", "\"")
    if card.text[0] == "\"":
        card.text = card.text[1:]
    if card.text[~0] == "\"":
        card.text = card.text[:-1]
    card.text = card.text.replace("<div>", "")
    card.text = card.text.replace("</div>", "")
    card.text = "<div>" + card.text + "</div>"
    card.text = card.text.replace("{{", "`{{")
    card.text = card.text.replace("}}", "}}`")

    card.text = card.text.replace("<div style=\"centerbox\"><div class=\"mnemonics\">", "")

    #TODO do the same thing to card.exta
    divs = len([i for i in range(len(card.text)) if card.text.startswith("<div", i)])
    closedivs = len([i for i in range(len(card.text)) if card.text.startswith("</div", i)])
    for i in range(0, divs-closedivs):
        card.text+="</div>"

    # divs = [i for i in range(len(card.text)) if card.text.startswith("<div", i)]
    # break tag after div tag deletion
    # for div in divs:
    #     close = card.text.find(">", div) + 1
    #
    #     if(card.text[close:close+4]=="<br>"):
    #         card.text = card.text[:close] + card.text[close+4:]

    #Cloze cleansing
    card.clozure_bolding()





    #print(card.text)

    # print(card.text)
    # print(card.extra)
    # print()

# used to ensure first always has extra text
isFirst = True

# print("Cleansing Extras")
for card in cards:
    if(isFirst):
        clone = card.extra
        clone = clone.replace("<br>", "")
        clone = clone.replace("<div>", "")
        clone = clone.replace("</div>", "")
        if len(clone) ==0:
            card.extra = "."
        isFirst = False


    if (card.extra == ""):
        continue

    card.extra = card.extra.replace("\"\"", "\"")
    if card.extra[0] == "\"":
        card.extra = card.extra[1:]
    if card.extra[~0] == "\"":
        card.extra = card.extra[:-1]
    card.extra = card.extra.replace("<div>", "")
    card.extra = card.extra.replace("</div>", "")

    # only image checking
    clone = card.extra
    clone = clone.replace("<br />", "")
    clone = clone.replace("<br>", "")
    clone = clone.replace("<i>", "")
    clone = clone.replace("</i>", "")
    if clone[0:4] == "<img" or clone[0:4] == "<br " or clone[0:4]==" <im":
        clone = clone[clone.find(">") + 1:]
        # if everything breaks, the bug is here (because img text img and the loop bellow will corrupt everything)

        while clone.find("<img") != -1:
            clone = clone[clone.find(">") + 1:]

        clone = clone.replace(" ", "")
        if len(clone) == 0:
            card.extra = "Extra <br>" + card.extra

    card.extra = "<div>" + card.extra + "</div>"
    card.extra = card.extra.replace("img src=\"", "img src=\"" + config['images_dir'])
    res = [i for i in range(len(card.extra)) if card.extra.startswith("src=", i)]
    spans = [i for i in range(len(card.extra)) if card.extra.startswith("<span", i)]

    while (len(spans) > 0):
        for s in spans:
            p1 = card.extra[0:s]
            p2 = card.extra[s + 1:]
            p2 = p2[p2.index(">") + 1:].replace("</span>", "", 1)

            card.extra = p1 + p2
            break
        spans = [i for i in range(len(card.extra)) if card.extra.startswith("<span", i)]

    # card.extra = card.extra.replace("<b style=\"font-style: italic; \">", "<b>")

    card.extra = card.extra.replace(" \"<", " &quot;<")

    if card.extra.find("<b style=\"font-style: italic; \">") != -1:
        card.extra = card.extra.replace("</b><i>", "")
        card.extra = card.extra.replace("</i><b style=\"font-style: italic; \">", "")
        card.extra = card.extra.replace("<b style=\"font-style: italic; \">", "michaelferrara")

        index = card.extra.find("michaelferrara")
        p2 = card.extra[index:].replace("</b>", "", 1)
        p1 = card.extra[:index]

        # print(p1)
        # print(p2)
        card.extra = p1 + p2
        card.extra = card.extra.replace("michaelferrara", "")



    # images = []
    # notfound = []
    #
    # for r in res:
    #     img = ""
    #     for char in card.extra[r+5:]:
    #         if char=="\"":
    #             images.append(img)
    #             break
    #         img+=char
    #
    # for i in images:
    #     # print(i)
    #     exists = os.path.isfile(i)
    #     # print(exists)
    #
    # # print(images)

    # print(card.extra)
    # break;

    # print(card.text)
    # print(card.extra)
    # print()

out = open("outhtml.html", "w")
out.write("<ul>")
# Write cards
num = len(cards)
for i, card in enumerate(cards):
    out.write("<li>")
    out.write(card.text)
    out.write("<ul>")
    out.write("<li>")
    out.write(card.extra)
    out.write("</li>")
    out.write("</ul>")
    out.write("</li>")


out.write("</ul>")
out.close()

# new_parser = HtmlToDocx()
# new_parser.parse_html_file("outhtml.html", "jb")


output = pypandoc.convert_file(source_file='outhtml.html', format='html', to='docx',
                               outputfile=config['out_dir'], extra_args=['-RTS'])
