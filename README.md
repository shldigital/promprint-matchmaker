# Promprint Matchmaker

Algorithms for matching book entries across different digital catalogs for the [Promprint](https://www.promiscuousprint.com/) project.

The main purpose of these scripts is to compare book entries across a stationer's register catalog and another digital library catalog, recording scores for various types of similarity across entry columns such as the book title, publisher and potentially creator, where it exists or can be guessed. The scripts require catalogs that have been cleaned using the [Promprint data-wrangling code](https://github.com/shldigital/promprint-data-wrangling).

## Installation
These instructions assume you are using either linux or mac, but they should work for windows.

This repo uses a command line program called [`uv`](https://docs.astral.sh/uv/getting-started/installation/) to manage python versions and dependencies independently of your local python version and libraries. First use the previous link to install `uv`. Then [clone this repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) to your local machine.

Once you have a copy of this repo one your machine, navigate to the repository in the command line, from where you can run the code via include jupyter notebooks using `uv`:

```
cd path-to-repository/promprint-matchmaker
uv run jupyter lab
```

This should automatically open a browser tab at `http://localhost:8888/lab`, but if it doesn't you can manually enter that address into your browser to start using the jupyter server.

You can also run tests on the code:

```
uv run pytest                   # Run tests on the repository
```

Note that the first time you run any of the commands above, `uv` will automatically synchronise the libraries required to run these scripts.


## Usage via Jupyter notebook:
So far there are two core scripts included in this repository that can be run from the included jupyter notebook (`titles_match.py` and `n_gram_list.py`), plus a third script that is experimental (`publisher_index.py`) and is not in the notebook, but can be run using the CLI (see the `CLI usage` section below).

### `match-titles.ipynb` comparing entries between registers and other catalogs

The notebook defines the location of all the necessary inputs and outputs:

- `register` and `collection` are the locations of the outputs of the promprint-data-wrangling code, corresponding to a cleaned stationer's register file and a cleaned catalog from the National Library of Scotland (at this time that is the only other catalog we have for comparison). Edit these so that they match the location on your computer.

- `n_gram_index` serves a dual purpose: it's both the folder that the `n_gram_list.py` script will output its n-gram index file to, and the folder that the `titles_match.py` script will read the same n-gram index from (more info on the n-gram index to follow). Set to `None` if you are not using the n-gram index

- `publishers_index` is a file containing a specially formatted publishers index that will be used to label an entry with a known publishing entity defined by the index and based on that entry's publisher string. Set to `None` if you are not using the publisher index
- `matches` is the output folder for the matching data

The relevant variables are also annotated in the notebook. More documentation on these will follow.

### `n_gram_list` function:
This function produces a list (saved to the folder specified by `n_gram_index`) of the top most frequent n-grams that occur in the given columns of the catalogs passed to the function. For example we can find the top 100 most common n-grams found in the `clean_title` column of the stationer's register and nls catalogs.

This list can optionally be used in the `titles_match` function to check whether a significant part  of the similarity in two entries can be attributed to commonly occuring n-grams, such as 'map of' or 'dictionary of'. If so then we may recategorise the comparison as a non-match, depending on the similarity of the remaining part of the string that is not the n-gram.

### `titles_match` function:
This function produces two relevant `.csv` formatted documents with the following naming scheme:

```
<date>-<register_name>-<library-collection-name>-matches.csv
<date>-<register_name>-<library-collection-name>-unmatched.csv
```

A third document with title:

`<date>-<register_name>-<library-collection-name>-top-matches.csv`

May also be produced but it's currently redundant and contains the same content as the `matches` file.

So for example, for the `1863b` register and the `NLS` library collection, we may have filenames:
```
2026-09-11-1863b-NLS-matches.csv
2026-09-11-1863b-NLS-unmatched.csv
```

The `matches` document contains a list of entries from the register catalogue that have been 'matched' with at least one entry from the library catalogue. The `unmatched` document contains all of the remaining entries in the register catalog.

Entries are considered a match when the similarity of the cleaned titles of the two entries is equal to or above the `score_threshold`, set within the notebook. The `matches` document only includes the match with the highest score, in the event that a register entry matches with multiple library entries.

In addition to the title similarity score, the document also includes similarity scores for the publisher and, if it can be inferred, for the similarity of the creator. This may help the researcher to manually assess and correct marginal or erroneous matches. To help further with this, the `match_titles` function can also take an n-gram list, generated from the other script, which may help to further disambiguate marginal matches.

More information on these algorithms will follow.

## CLI usage:
`uv run mm -h`:

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
`uv run mm titles -h`:

```
usage: mm titles [-h] [--publishers_index PUBLISHERS_INDEX]
                 [--n_gram_index N_GRAM_INDEX] [-t SCORE_THRESHOLD]
                 [-s SUBSTRING_SCORE_THRESHOLD] [-w WORD_THRESHOLD]
                 [-p PROCESSES] [--short_title_limit SHORT_TITLE_LIMIT]
                 register collection outpath

positional arguments:
  register              File of cleaned register data in csv format
  collection            File of cleaned collection data in tsv format
  outpath               Output file location

options:
  -h, --help            show this help message and exit
  --publishers_index PUBLISHERS_INDEX
                        File of publisher index used to replace publisher
                        strings with more common names
  --n_gram_index N_GRAM_INDEX
                        File of n-gram index used to check for n-gram
                        substring matches
  -t SCORE_THRESHOLD, --score_threshold SCORE_THRESHOLD
                        Threshold fuzzy matching score (0-100), only keep
                        matches with scores above this value
  -s SUBSTRING_SCORE_THRESHOLD, --substring_score_threshold SUBSTRING_SCORE_THRESHOLD
                        Threshold fuzzy matching score (0-100), only keep
                        substring matches with scores above this value
  -w WORD_THRESHOLD, --word_threshold WORD_THRESHOLD
                        Threshold number of words/tokens for a collection
                        title to be considered for matching
  -p PROCESSES, --processes PROCESSES
                        Number of threads to use in search, if > 1 will run
                        searches in parallel
  --short_title_limit SHORT_TITLE_LIMIT
                        If given then texts with fewer tokens than this are
                        only matched at the beginning of longer texts.
```

Usage example (default score threshold and word threshold, no debug):
```
uv run mm titles -p 8 ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv ../promprint-data/
```

This takes the `register_export.csv` register data and looks for entries from that register within `nls_catalog_export.tsv`, and outputs match info to the `/promprint-data` folder.

## `n_grams` subcommand:

```
usage: mm n_grams [-h] [-c COLUMNS [COLUMNS ...]] [-n N_TOP] [--min_degree MIN_DEGREE] [--max_degree MAX_DEGREE]
                  [--min_frequency MIN_FREQUENCY]
                  outpath catalog catalog

positional arguments:
  outpath               Output file location
  catalog               Path to catalogs from which to build n_gram list

options:
  -h, --help            show this help message and exit
  -c COLUMNS [COLUMNS ...], --columns COLUMNS [COLUMNS ...]
                        Columns to create n-grams for, will create a separate list per column
  -n N_TOP, --n_top N_TOP
                        Top n-grams to include in the index
  --min_degree MIN_DEGREE
                        Minimum degree of n-gram to include
  --max_degree MAX_DEGREE
                        Max degree of n-gram to include
  --min_frequency MIN_FREQUENCY
                        Minimum frequency of n-gram to include
```

Usage example:
```
uv run mm n_grams ../promprint-data/ ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv
```

This takes the `register_export.csv` register data and the `nls_catalog_export.tsv` catalog data, and collects all n\_grams from the default "clean\_title" column found in these files. It takes the N_TOP most frequent n\_grams and outputs this list to the `/promprint-data` folder, alongside the full list of _all_ n\_grams found as well as a plot of the frequency of n\_grams.

Run the n-gram compilation for multiple columns:
```
uv run mm n_grams ../promprint-data/ ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv --columns clean_title clean_publisher
```

This takes the `register_export.csv` register data and the `nls_catalog_export.tsv` catalog data, and collects all n\_grams from the specified columns found in these files, here "clean_title" and "clean_publisher". It takes the N_TOP most frequent n\_grams and outputs this list to the `/promprint-data` folder, alongside the full list of _all_ n\_grams found as well as a plot of the frequency of n\_grams. Each column will have separate n-gram files.


## `publishers` subcommand (not currently in use):

```
usage: mm publishers [-h] [-n N_TOP] [-t SCORE_THRESHOLD] [--n_gram_index N_GRAM_INDEX]
                     outpath collections [collections ...]

positional arguments:
  outpath               Output file location
  collections           Path to collections with publishers to be collated

options:
  -h, --help            show this help message and exit
  -n N_TOP, --n_top N_TOP
                        Group similar matches for only the n_top most frequent publisher names
  -t SCORE_THRESHOLD, --score_threshold SCORE_THRESHOLD
                        Threshold fuzzy matching score (0-100), only keep matches with scores above this value
  --n_gram_index N_GRAM_INDEX
                        File of n-gram index used to check for n-gram substring matches
```

Usage example (default score threshold and number of top most frequent publishers used to generate indexes):

```
uv run mm publishers ../promprint-data/ ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv
```

This takes the `register_export.csv` register data and the `nls_catalog_export.tsv` catalog data, and collects all cleaned publisher names from these files. It calculates the N_TOP most frequent publisher names and matches each one of those in turn against all other entries. Close matches will be recorded in the index. The script outputs match info to the `/promprint-data` folder.

You can also pass a index of common n-grams found in the publisher columns (generated using the `n_grams` subcommand, below). This will use the n-gram substring match scoring method (reference to follow) to match publisher names for the purposes of being indexed.
```
uv run mm publishers --n_gram_index=../promprint-data/publishers_n_gram_index.csv ../promprint-data/ ../promprint-data/register_export.csv ../promprint-data/nls_catalog_export.tsv
```


