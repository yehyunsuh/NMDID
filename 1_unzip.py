import os
import argparse

from glob import glob


def main(args):
    zip_file_list = glob(args.input + '/*.zip')

    for zip_file in zip_file_list:
        # Unzip the zip file to the output directory
        os.system(f'unzip "{zip_file}" -d {args.output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Unzip zip files')

    parser.add_argument('--input', type=str, help='Input zip directory', default='0_NMDID')
    parser.add_argument('--output', type=str, help='Output unzipped directory', default='1_NMDID_unzipped')

    args = parser.parse_args()

    os.makedirs(f'{args.output}', exist_ok=True)

    main(args)