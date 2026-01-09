# Promprint Matchmaker

Search algorithms for matching book title strings across different registers for the [Promprint](https://www.promiscuousprint.com/) project

Usage:
```
usage: mm [-h] [-d] [-t SCORE_THRESHOLD] [-w WORD_THRESHOLD] [-p PROCESSES] register collection outpath

Find register's hall entries in collections of library data

positional arguments:
  register              File of cleaned register data in csv format
  collection            File of cleaned collection data in tsv format
  outpath               Output file location

options:
  -h, --help            show this help message and exit
  -d, --debug           Print debug messages
  -t SCORE_THRESHOLD, --score_threshold SCORE_THRESHOLD
                        Threshold fuzzy matching score (0-100), only keep matches with scores above this value
  -w WORD_THRESHOLD, --word_threshold WORD_THRESHOLD
                        Threshold number of words/tokens for a collection title to be considered for matching
  -p PROCESSES, --processes PROCESSES
                        Number of threads to use in search, if > 1 will run searches in parallel
```

Usage example (default score threshold and word threshold, no debug):
```
uv run mm -p 8 ../promprint-data/251104-1863b-full_export.csv ../promprint-data/nls_catalog_1863b_export.tsv ../promprint-data/
```

This takes the `251104-1863b-full_export.csv` register data and looks for entries from that register within `nls_catalog_1863b_export.tsv`, and outputs match info to the `/promprint-data` folder.
