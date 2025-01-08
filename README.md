# mmseq-viral-db

This repository builds the MMseqs viral database for EVEREST using the latest UniProt version.

The script automates downloading, processing, and preparing viral proteomes and taxonomy data for MMseqs2 database creation. It supports UniProt databases and integrates several key bioinformatics tools, ensuring reproducibility and scalability.

## Features

- Downloads viral proteomes from UniProt (`SwissProt` or `TrEMBL`).
- Decompresses `.fasta.gz` files into `.fasta` format.
- Parses FASTA files to extract sequence identifiers and taxonomic IDs (`OX` field) into TSV format.
- Downloads and extracts NCBI taxonomy data, storing it in the `TAX/` directory.
- Combines FASTA, TaxID TSV, and taxonomy data into an MMseqs2 database for proteomic analysis.

## Setup

### Install Dependencies

1. **Conda Environment Setup**

Create a Conda environment with the following command usign the `yml` file [here](https://github.com/agudeloromero/mmseq-viral-db/blob/main/uniprot.yml):
```bash
conda env create -f uniprot.yml
conda activate uniprot
```
## Example Workflow

Download and Process SwissProt Database
```bash
./script.py --db swissprot
```

Download and Process TrEMBL Database
```bash
./script.py --db trembl
```

Specify Custom Output Path
```bash
./script.py --db swissprot --output custom_dir/taxid_output.tsv
```

Skip Specific Steps If taxonomy data is already available:
```bash
./script.py --db swissprot --skip-taxonomy
```

Keep Intermediate Files
```bash
./script.py --db swissprot --keep-intermediate
```

## Outputs

1. FASTA File: Processed viral proteomes in `.fasta` format.
2. TaxID TSV: A tab-separated file mapping sequence identifiers to taxonomic IDs.
3. NCBI Taxonomy Data: Extracted taxonomy files stored in the `TAX/` directory.
4. MMseqs2 Database: A ready-to-use database in `DB_MMSEQ2_aa/` combining:
    * Viral proteomes (`FASTA` file).
    * Taxonomic IDs (`TaxID TSV`).
    * NCBI taxonomy data (`TAX/` directory).

## Functions Overview

`check_file_exists(file_path, description)`

Ensures required files are available.


**`download_with_progress(url, output_path)`**

Downloads files with `aria2c` and provides real-time progress updates.

**`decompress_fasta_gz(input_gz_path, output_fasta_path)`**

Decompresses `.fasta.gz` files to `.fasta` format.

**`parse_fasta_to_dataframe_with_progress(file_path, output_file)`**

Parses FASTA headers to extract sequence identifiers and taxonomic IDs into a TSV file.

**`download_and_extract_taxonomy(url, output_dir)`**

Downloads and extracts the NCBI taxonomy dump, storing the data in the specified directory (default: `TAX/`).

**`build_mmseqs_db(fasta_path, taxid_path, taxonomy_dir, db_output_dir)`**

Creates an MMseqs2 database by combining:
      * Processed FASTA data.
      * Extracted taxonomic IDs.
      * NCBI taxonomy files.

## Help Menu

Use the `--help` option to view all usage instructions:
```bash
EVEREST_uniprot_mmseqdb.py --help
```

**Command-line Arguments**
```plaintext
usage: EVEREST_uniprot_mmseqdb.py [-h] --db {swissprot,trembl} [--output OUTPUT]
                 [--keep-intermediate] [--skip-taxonomy] [--skip-taxid]
                 [--skip-mmseqs]

Download and process viral proteomes and taxonomy data from UniProt.

optional arguments:
  -h, --help            Show this help message and exit.
  --db {swissprot,trembl}
                        Database to download: 'swissprot' or 'trembl'.
  --output OUTPUT       Path to the output TSV file (default: taxid_aa/taxid_aa.tsv).
  --keep-intermediate   Keep the intermediate .fasta.gz file after decompression.
  --skip-taxonomy       Skip downloading and extracting taxonomy data.
  --skip-taxid          Skip extracting taxid and parsing FASTA to TSV.
  --skip-mmseqs         Skip building the MMseqs2 database.

```

### Contributing

Contributions and feedback are welcome! Report issues or request features in the [repository](https://github.com/agudeloromero/Download_fasta_NCBI/issues).

### Acknowledgments

- [`aria2c`](https://github.com/aria2/aria2): For high-speed downloads.
- [`gzip`](https://docs.python.org/3/library/gzip.html): To decompress `.fasta.gz` files.
- [`pandas`](https://pandas.pydata.org/): For parsing and managing extracted data.
- [`MMseqs2`](https://github.com/soedinglab/MMseqs2): For database creation and taxonomy processing.
- [`NCBI`](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/): Download the taxonomy database (taxdump).
- [`UNIPROT`](https://www.uniprot.org/taxonomy/10239): Download the viral proteomes (Swiss-Prot | TrEMB).

