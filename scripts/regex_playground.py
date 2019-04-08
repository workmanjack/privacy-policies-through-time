import re


#with open('20110902041958_check_date.txt', 'r') as f:
with open('20110902041958_check_date.txt', 'r') as f:
    page = f.read()

# This policy was last updated on July 21, 2011 ("Effective Date").
# Last updated on July 21, 2011

regex = re.compile(r'last updated on (.*) \(')

match = regex.search(page)
print(match)
print(match.group(1))

