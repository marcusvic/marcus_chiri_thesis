# Papers researcher
- Receives as inputs: query test in [Scopus UI](https://www.scopus.com/search/form.uri?display=advanced) first. Attention:
    - Because the API doesn't accept the "limit-to" clause, you have to input the subject areas in the "SUBJ" variable in the config.txt file
- Retrieves all_papers, a list of dictionaries. This list can be written to an Excel file or to a database. The code here writes to a database for further processing (for example, retrieving the abstracts and then the text of each article)


## AI analysis
- [ ] Join test and writes_csv in a main.py file
- [ ] Update the system prompt.
- [x] Have the AI retrieve the text passages that illustrate the reason why it categorised an item that way
- [ ] Have the confidence score for everything - nice to have because we can't explain it well. 
- [ ] Write a readme.md

## Cost
- [ ] When running the full thing, maximise caching. Check cache rates in case we have to pass the same 
- [ ] Check if cheaper models (gpt-4.1-nano-2025-04-14) perform the same