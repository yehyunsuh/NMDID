import os
import argparse

from glob import glob


def main(args):
    unzipped_file_list = glob(args.input + '/omi/incomingdir/*')
    
    for unzipped_file in unzipped_file_list:
        case_id = unzipped_file.split('/')[-1]
        os.makedirs(f'{args.output}/{case_id}', exist_ok=True)

        case_sub_direcotries = glob(unzipped_file + '/*')
        
        # From the case directory, exclude when it contains 'NONE' or 'localizers' in the path
        scan_path = [case_dir for case_dir in case_sub_direcotries if 'NONE' not in case_dir and 'localizers' not in case_dir][0]
        
        # Convert DICOM to NIfTI: https://github.com/rordenlab/dcm2niix
        scan_by_body_list = glob(scan_path + '/*')
        
        for scan_by_body in scan_by_body_list:
            body_part = scan_by_body.split('/')[-1]
            file_name = f'{case_id}_{body_part}'
            os.system(f'dcm2niix -o {args.output}/{case_id} -f {file_name} -z y -s y {scan_by_body}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert DICOM to NIfTI')

    parser.add_argument('--input', type=str, help='Input unzipped directory', default='1_NMDID_unzipped')
    parser.add_argument('--output', type=str, help='Output NIfTI directory', default='2_NMDID_nii')

    args = parser.parse_args()

    main(args)