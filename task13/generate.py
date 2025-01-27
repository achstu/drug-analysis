from lxml import etree
import random
import copy
import threading
from tqdm import tqdm

ns = {"db": "http://www.drugbank.ca"}
xmlns = "{http://www.drugbank.ca}"


def sz(node):
    return 1 + sum(sz(child) for child in node)


tree = etree.parse("data/drugbank_partial.xml")
root = tree.getroot()
all_drugs = root.findall("db:drug", ns)
small_drugs = list(filter(lambda drug: sz(drug) <= 1000, all_drugs))


def unwrap(field, node: etree._Element):
    return getattr(node.find(f"db:{field}", ns), "text", None)


def unwrap_attrib(attrib, node: etree._Element):
    return node.attrib.get(attrib)


def print_node(node: etree._Element):
    print(etree.tostring(etree.ElementTree(node), pretty_print=True).decode("utf-8"))


def random_drug(drugset=small_drugs):
    return random.choice(drugset)


def random_drug_field(xpath):
    return getattr(random_drug(drugset=all_drugs).find(xpath, ns), "text", None)


def new_random_drug(drugbank_id):
    frame_drug = random_drug()
    new_drug = copy.deepcopy(frame_drug)

    def to_xpath(path):
        return "/".join(path).replace("{http://www.drugbank.ca}", "db:")

    def build(node, path=[]):
        if path:
            xpath = to_xpath(path)
            node.text = random_drug_field(xpath)

        for child in node:
            build(child, path + [child.tag])

    build(new_drug)
    new_drug.find("db:drugbank-id", ns).text = drugbank_id
    return new_drug


def generate():
    N = 19900
    for id in tqdm(
        range(N),
        desc="Generating drugs",
        unit="",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",
    ):
        root.append(new_random_drug(str(id)))


def save_to_file():
    new_tree = etree.ElementTree(root)
    with open("data/drugbank_partial_and_generated.xml", "wb") as file:
        new_tree.write(
            file,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )


def add_namespace(path):
    find = "<drug type="
    replace = '<drug xmlns="http://www.drugbank.ca" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" type='
    with open(path, "r") as file:
        lines = file.readlines()

    with open(path, "w") as file:
        for line in lines:
            file.write(line.replace(find, replace))


generate()
save_to_file()
add_namespace("data/drugbank_partial_and_generated.xml")
