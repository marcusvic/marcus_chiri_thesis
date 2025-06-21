import pybliometrics

pybliometrics.init()

from pybliometrics.scopus import ScopusSearch
# Your Scopus search string
query = "TITLE-ABS-KEY( \"policy implementation\" OR \"instrument implementation\" OR \"program implementation\") AND TITLE-ABS (driv* OR moderat* OR obstacle* OR mediat* OR imped* OR determin* OR issue* OR challeng* OR problem* OR barrier* OR facilit* OR enabl* OR factor*) AND TITLE (\"implementation\") AND LIMIT-TO ( SUBJAREA,\"SOCI\" )"

s = ScopusSearch(
    query, 
    download=True, 
    count=2
    )

s.get_results_size()
# Extract titles and abstracts
papers = []
for eid in s.get_eids():
    # You can use AbstractRetrieval for more details if needed
    papers.append({
        "eid": eid,
        "title": s.results[s.get_eids().index(eid)].title,
        "abstract": s.results[s.get_eids().index(eid)].description
    })