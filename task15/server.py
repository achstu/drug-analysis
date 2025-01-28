from fastapi import FastAPI, HTTPException
from lxml import etree
import uvicorn


def init():
    def unwrap(field, node: etree._Element):
        return getattr(node.find(f"db:{field}", ns), "text", None)

    path = "data/drugbank_partial.xml"
    ns = {"db": "http://www.drugbank.ca"}
    root: etree._Element = etree.parse(path).getroot()

    data = {}
    for pathway in root.findall("db:drug/db:pathways/db:pathway", ns):
        pathway_name = unwrap("name", pathway)
        for drug in pathway.findall("db:drugs/db:drug", ns):
            drug_id = unwrap("drugbank-id", drug)
            data.setdefault(drug_id, [])
            data[drug_id].append(pathway_name)

    return {k: len(v) for (k, v) in data.items()}


data = init()
print(data)

def pathway_count(drugbank_id: str) -> int:
    if drugbank_id not in data:
        raise ValueError("DrugBank ID not found")
    return data[drugbank_id]


app = FastAPI()


@app.post("/pathways/")
async def get_pathways_count(drugbank_id: str):
    try:
        pathways_count = pathway_count(drugbank_id)
        return {"drugbank_id": drugbank_id, "pathway_count": pathways_count}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
