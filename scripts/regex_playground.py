import re
import dateparser


#with open('20110902041958_check_date.txt', 'r') as f:
with open('20150420205418_check_date.txt', 'r') as f:
    page = f.read()

# This policy was last updated on July 21, 2011 ("Effective Date").
# Last updated on July 21, 2011

regex = re.compile(r'Revised: (\w+ \d+, \d+)')

match = regex.search(page)
print(match)
print(match.group(1))
update_date = dateparser.parse(match.group(1))
print(update_date)
