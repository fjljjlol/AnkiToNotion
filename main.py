import pypandoc
from card import *
from user import *
import yaml
import sys
import os

with open("config.yaml") as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)
    user_config = conf[user]
    card_config = conf['card']

if user_config["block_print"]:
    sys.stdout = open(os.devnull, 'w')

cards = get_cards(user_config['tsv'], card_config['optionals'])

# used to ensure first always has extra text
isFirst = True

# 1 cleanse the text
# print("Cleansing Text")
for card in cards:
    card.initial_pruning()

    # ----------------Text Pruning----------------
    #Clozure pruning
    card.text = "<div>" + card.text + "</div>"
    card.text = card.text.replace("{{", "`{{")
    card.text = card.text.replace("}}", "}}`")

    card.do_text_special()

    #TODO do the same thing to card.extra
    divs = len([i for i in range(len(card.text)) if card.text.startswith("<div", i)])
    closedivs = len([i for i in range(len(card.text)) if card.text.startswith("</div", i)])
    for i in range(0, divs-closedivs):
        card.text+="</div>"

    #clozure bolding
    card.clozure_bolding()

    # only image checking
    card.perform_only_image_detection(TextType.TEXT)

    # Images handling
    card.text = card.text.replace("img src=\"", "img src=\"" + user_config['images_dir'])
    if user_config['debug']:
        card.get_images(user_config['default_img'])


    # print(card.text)

    #----------------Extra Pruning----------------
    if isFirst:
        clone = card.extra
        clone = clone.replace("<br>", "")
        clone = clone.replace("<div>", "")
        clone = clone.replace("</div>", "")
        if len(clone) ==0:
            card.extra = "."
        isFirst = False


    if card.extra != "":
        # only image checking
        card.perform_only_image_detection(TextType.EXTRA)

        card.extra = "<div>" + card.extra + "</div>"

        #Images handling
        card.extra = card.extra.replace("img src=\"", "img src=\"" + user_config['images_dir'])
        if user_config['debug']:
            card.get_images(user_config['default_img'])

        # if not user_config['debug']:
        #     card.extra = card.extra.replace("img src=\"", "img src=\"" + user_config['images_dir'])
        # else:
        #     # card.extra = card.extra.replace("img src=\"","")
        #     card.extra = card.extra.replace("img src=\"", "img src=\"" + user_config['images_dir'])
        #     card.get_images(user_config['default_img'])
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

        card.do_extra_special()


    # ----------------Optional Pruning----------------
    # only image checking
    card.perform_only_image_detection(TextType.OPTIONAL, True)

    #Images handling
    for name, val in card.optionals.items():
        card.optionals[name] = val.replace("img src=\"", "img src=\"" + user_config['images_dir'])
        if user_config['debug']:
            card.get_images(user_config['default_img'])


    # print(card.text)
    # print()




# for card in cards:
#     print(card)
#     print()


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

    if card.has_optionals():
        for name, val in card.optionals.items():
            out.write("<li>")
            out.write(val)
            out.write("</li>")

    out.write("</ul>")
    out.write("</li>")


out.write("</ul>")
out.close()

# new_parser = HtmlToDocx()
# new_parser.parse_html_file("outhtml.html", "jb")


output = pypandoc.convert_file(source_file='outhtml.html', format='html', to='docx',
                               outputfile=user_config['out_dir'], extra_args=['-RTS'])
