# Promprint Matchmaker

Search algorithms for matching book title strings across different registers for the [Promprint](https://www.promiscuousprint.com/) project

## General usage:
```
usage: mm [-h] [-d] {titles,publishers,n_grams} ...

Find register's hall entries in collections of library data

positional arguments:
  {titles,publishers,n_grams}
                        Matching subjects
    titles              Match titles in register to those in a collection
    publishers          Create a publishers index by grouping similar publisher names
    n_grams             Create a n_gram index

options:
  -h, --help            show this help message and exit
  -d, --debug           Print debug messages
```

## `titles` subcommand:

```
usage: mm titles [-h] [--publishers_index PUBLISHERS_INDEX] [--n_gram_index N_GRAM_INDEX] [-t SCORE_THRESHOLD]
                 [-w WORD_THRESHOLD] [-p PROCESSES]
                 register collection outpath

positional arguments:
  register              File of cleaned register data in csv format
  collection            File of cleaned collection data in tsv format
  outpath               Output file location

options:
  -h, --help            show this help message and exit
  --publishers_index PUBLISHERS_INDEX
                        File of publisher index used to replace publisher strings with more common names
  --n_gram_index N_GRAM_INDEX
                        File of n-gram index used to check for n-gram substring matches
  -t SCORE_THRESHOLD, --score_threshold SCORE_THRESHOLD
                        Threshold fuzzy matching score (0-100), only keep matches with scores above this value
  -w WORD_THRESHOLD, --word_threshold WORD_THRESHOLD
                        Threshold number of words/tokens for a collection title to be considered for matching
  -p PROCESSES, --processes PROCESSES
                        Number of threads to use in search, if > 1 will run searches in parallel
```

Usage example (default score threshold and word threshold, no debug):
```
uv run mm titles -p 8 ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv ../promprint-data/
```

This takes the `register_export.csv` register data and looks for entries from that register within `nls_catalog_export.tsv`, and outputs match info to the `/promprint-data` folder.

## `publishers` subcommand:

```
usage: mm publishers [-h] [-n N_TOP] [-t SCORE_THRESHOLD] outpath collections [collections ...]

positional arguments:
  outpath               Output file location
  collections           Path to collections with publishers to be collated

options:
  -h, --help            show this help message and exit
  -n N_TOP, --n_top N_TOP
                        Group similar matches for only the n_top most frequent publisher names
  -t SCORE_THRESHOLD, --score_threshold SCORE_THRESHOLD
                        Threshold fuzzy matching score (0-100), only keep matches with scores above this value
```

Usage example (default score threshold and number of top most frequent publishers used to generate indexes):

```
uv run mm publishers ../promprint-data/ ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv
```

This takes the `register_export.csv` register data and the `nls_catalog_export.tsv` catalog data, and collects all cleaned publisher names from these files. It calculates the N_TOP most frequent publisher names and matches each one of those in turn against all other entries. Close matches will be recorded in the index. The script outputs match info to the `/promprint-data` folder.

## `n_grams` subcommand:

```
usage: mm n_grams [-h] [-c COLUMNS [COLUMNS ...]] [-n N_TOP] [-t SCORE_THRESHOLD] outpath catalog catalog

positional arguments:
  outpath               Output file location
  catalog               Path to catalogs from which to build n_gram list

options:
  -h, --help            show this help message and exit
  -c COLUMNS [COLUMNS ...], --columns COLUMNS [COLUMNS ...]
                        Columns to create n-grams for, will create a separate list per column, default "clean_titles"
  -n N_TOP, --n_top N_TOP
                        Top n-grams to include in the index
  -t SCORE_THRESHOLD, --score_threshold SCORE_THRESHOLD
                        Threshold fuzzy matching score (0-100), only keep matches with scores above this value
```

Usage example:
```
uv run mm n_grams ../promprint-data/ ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv
```

This takes the `register_export.csv` register data and the `nls_catalog_export.tsv` catalog data, and collects all n\_grams from the specified columns found in these files. It takes the N_TOP most frequent n\_grams and outputs this list to the `/promprint-data` folder, alongside the full list of _all_ n\_grams found as well as a plot of the frequency of n\_grams.
