#!/usr/bin/env python3

import os
import gzip
import argparse
import pandas as pd
import subprocess

__author__ = "Patricia Agudelo-Romero, PhD"

def check_file_exists(file_path, description="file"):
    """
    Check if a file exists and print an error message if it doesn't.

    :param file_path: Path to the file.
    :param description: Description of the file for error messages.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Required {description} not found: {file_path}")

def download_with_progress(url, output_path):
    """
    Download a file using aria2c and display its outcome.

    :param url: URL of the file to download.
    :param output_path: Path to save the downloaded file.
    """
    print(f"Starting download: {url}")
    command = [
        "aria2c", "--file-allocation=none", "-c", "-x", "10", "-s", "10", "-o", output_path, url
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(line.strip())  # Print aria2c's stdout output
    process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"aria2c failed with return code {process.returncode}.")
    print(f"Download completed: {output_path}")

def decompress_fasta_gz(input_gz_path, output_fasta_path):
    """
    Decompress a .fasta.gz file to .fasta format.

    :param input_gz_path: Path to the input .fasta.gz file.
    :param output_fasta_path: Path to save the decompressed .fasta file.
    """
    print(f"Decompressing: {input_gz_path} to {output_fasta_path}")
    with gzip.open(input_gz_path, 'rt') as gz_file:
        with open(output_fasta_path, 'w') as fasta_file:
            fasta_file.writelines(gz_file)
    print(f"Decompressed to: {output_fasta_path}")

def parse_fasta_to_dataframe_with_progress(file_path, output_file):
    """
    Parse a FASTA file and extract taxonomic IDs and sequence identifiers.

    :param file_path: Path to the input FASTA file.
    :param output_file: Path to the output TSV file.
    """
    rows = []
    print(f"Parsing FASTA file: {file_path}")
    with open(file_path, 'r') as fasta_file:
        for line in fasta_file:
            if line.startswith(">"):
                parts = line.split('|')
                between_pipes = parts[1] if len(parts) > 1 else "N/A"
                ox_index = line.find("OX=")
                ox_string = line[ox_index + 3:].split()[0] if ox_index != -1 else "N/A"
                rows.append([between_pipes, ox_string])
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, sep="\t", index=False, header=False)
    print(f"Output written to: {output_file}")

def download_and_extract_taxonomy(url, output_dir):
    """
    Download and extract NCBI taxonomy dump.

    :param url: URL to download the taxonomy dump.
    :param output_dir: Directory to save the downloaded and extracted files.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"Downloading taxonomy data from: {url}")
    download_command = [
        "aria2c", "--file-allocation=none", "-c", "-x", "10", "-s", "10", "-d", output_dir, url
    ]
    subprocess.run(download_command, check=True)
    downloaded_file = os.path.join(output_dir, os.path.basename(url))
    print(f"Extracting taxonomy data: {downloaded_file}")
    subprocess.run(["tar", "-xvzf", downloaded_file, "-C", output_dir], check=True)
    os.remove(downloaded_file)
    print(f"Taxonomy data extracted to: {output_dir}")

def build_mmseqs_db(fasta_path, taxid_path, taxonomy_dir, db_output_dir):
    """
    Build MMseqs2 database for the given FASTA file.

    :param fasta_path: Path to the input FASTA file.
    :param taxid_path: Path to the taxid TSV file.
    :param taxonomy_dir: Directory containing NCBI taxonomy files.
    :param db_output_dir: Directory to save the MMseqs2 database.
    """
    os.makedirs(db_output_dir, exist_ok=True)
    tmp_dir = os.path.join(db_output_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    db_path = os.path.join(db_output_dir, "viral.aa.fnaDB")
    print(f"Creating MMseqs2 database at: {db_path}")
    subprocess.run(["mmseqs", "createdb", fasta_path, db_path], check=True)

    print("Creating MMseqs2 taxonomy database...")
    subprocess.run([
        "mmseqs", "createtaxdb", db_path, tmp_dir,
        "--ncbi-tax-dump", taxonomy_dir, "--tax-mapping-file", taxid_path
    ], check=True)
    print("MMseqs2 database created successfully.")

def main():
    parser = argparse.ArgumentParser(
        description="Download and process viral proteomes and taxonomy data from Uniprot."
    )
    parser.add_argument("--db", type=str, choices=["swissprot", "trembl"], required=True, help="Database to download: 'swissprot' or 'trembl'.")
    parser.add_argument("--output", type=str, default="taxid_aa/taxid_aa.tsv", help="Path to the output TSV file (default: taxid_aa/taxid_aa.tsv).")
    parser.add_argument("--keep-intermediate", action="store_true", help="Keep the intermediate .fasta.gz file after decompression.")
    parser.add_argument("--skip-taxonomy", action="store_true", help="Skip downloading and extracting taxonomy data.")
    parser.add_argument("--skip-taxid", action="store_true", help="Skip extracting taxid and parsing FASTA to TSV.")
    parser.add_argument("--skip-mmseqs", action="store_true", help="Skip building the MMseqs2 database.")

    args = parser.parse_args()

    db_urls = {
        "swissprot": 'https://rest.uniprot.org/uniprotkb/stream?compressed=true&format=fasta&query=%28%28taxonomy_id%3A10239%29+AND+%28reviewed%3Atrue%29%29',
        "trembl": 'https://rest.uniprot.org/uniprotkb/stream?compressed=true&format=fasta&query=%28%28taxonomy_id%3A10239%29+AND+%28reviewed%3Afalse%29%29',
    }

    output_dir = args.db
    gz_path = os.path.join(output_dir, f"viral_proteomes_{args.db}.fasta.gz")
    fasta_path = gz_path.replace(".fasta.gz", ".fasta")

    download_with_progress(db_urls[args.db], gz_path)
    decompress_fasta_gz(gz_path, fasta_path)

    if not args.skip_taxid:
        parse_fasta_to_dataframe_with_progress(fasta_path, args.output)

    if not args.keep_intermediate:
        os.remove(gz_path)
        print(f"Intermediate file '{gz_path}' has been deleted.")

    if not args.skip_taxonomy:
        taxonomy_url = "ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"
        download_and_extract_taxonomy(taxonomy_url, "TAX")

    if not args.skip_mmseqs:
        check_file_exists(fasta_path, "FASTA file")
        check_file_exists(args.output, "TaxID file")
        check_file_exists("TAX/nodes.dmp", "taxonomy nodes.dmp file")
        build_mmseqs_db(fasta_path, args.output, "TAX", "DB_MMSEQ2_aa")

    print("All steps completed successfully.")

if __name__ == "__main__":
    main()
