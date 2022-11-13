# Hasselback's Faculty Roster
Compiled Data of James R. Hasselback's Faculty lists, combined with Scopus IDs

## What is this?
James Hasselback publishes a near-complete list of faculties of Economics, Management, Finance and Accounting departments in the US, Canada and some other places for various years.  I have compiled those lists (available at http://www.jrhasselback.com/FacDir.html as pdfs) to make them usable in my research.

The following year-field combinations are available:

|           | Accounting | Economics | Finance | Management |
|-----------|------------|-----------|---------|------------|
| 1999-2000 |            |     x     |         |            |
| 2000-2001 |     x      |           |    x    |      x     |
| 2001-2002 |     x      |     x     |         |            |
| 2002-2003 |            |           |    x    |            |
| 2003-2004 |     x      |     x     |         |            |
| 2004-2005 |            |           |         |            |
| 2005-2006 |            |           |         |            |
| 2006-2007 |            |     x     |         |            |

I only report faculty member with PHD and who are not decesased, retired or emeritus.

They are augmented with the Scopus IDs of the researchers.  Although I've given great attention to the mapping of researchers to their Scopus Author profile IDs, there might be few errors.  We used all availble information, including affiliation history and field.

Feel free to use them in your research, too.  You can find a variable description on [James' website](http://www.jrhasselback.com/AtgDir.html).  I am open to data additions and gladly accept Pull Requests.  Note that I aggregated information for researchers holding a PhD only.

## How do I use this?

...

Usage in your scripts is easy:

* In python (with pandas):
```python
import pandas as pd

FACULTY_FILE = ('https://raw.githubusercontent.com/Michael-E-Rose/Hasselback'
                'FacultyRoster/master/hasselback.csv')
hass = pd.read_csv(FACULTY_FILE, index_col=0)
```

<!-- * In R:
```R
...
``` -->

<!-- * In Stata:
```Stata
...
```
 -->
## What's the benefit?
- Central online storage for seamless inclusion in local scripts.
- Longitudinal collection of faculty information for US-based researchers including academic rank, year of PhD and PhD school and more.

## Workflow
- 
- [`./mapping_files/institutions.csv`](./mapping_files/institutions.csv) and [`./mapping_files/persons.csv`](./mapping_files/persons.csv) are mapping files to aggregate over differently used university names and to map researchers to their Scopus profile IDs.
- [`condense_faculty_lists.py`](condense_faculty_lists.py) combines the information.
- [`hasselback.csv`](hasselback.csv) is the resulting file.
