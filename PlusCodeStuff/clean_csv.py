import csv
import re

def filter_csv(input_file, output_file, regex_pattern):
    # Compile the regular expression pattern
    pattern = re.compile(regex_pattern)

    # Open the input CSV file for reading
    with open(input_file, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # Open the output CSV file for writing
        with open(output_file, mode='w', newline='', encoding='utf-8') as outputfile:
            writer = csv.writer(outputfile)

            # Iterate over the rows in the input CSV file
            for row in reader:
                # Join the row into a single string to match the regex
                row_string = ' '.join(row)

                # If the row does not match the pattern, write it to the output file
                if not pattern.search(row_string):
                    writer.writerow(row)

if __name__ == "__main__":
    # Example usage
    input_file = 'plus_codes_for_bigquery.csv'  
    output_file = 'cleaned_pluscode.csv'  
    regex_pattern = r'^6G[5-9][H-X]'  # Match lines starting with "5F"

    filter_csv(input_file, output_file, regex_pattern)