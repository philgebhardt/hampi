import sys
import re

import docx

start_asn = re.compile(r'^-- ASN1START$')
end_asn = re.compile(r'^-- ASN1STOP$')

def main(spec_file, asn_dir):

    doc = docx.Document(spec_file)
    start_printing = False
    out_lines = []
    for para in doc.paragraphs:
        if re.match(start_asn, para.text):
            start_printing = True
        if start_printing:
            out_lines.append(para.text + "\n")
        if re.match(end_asn, para.text):
            start_printing = False


    out_lines = [line.replace(chr(0xa0), ' ') for line in out_lines]

    modules = {}
    last_nonblank = None
    i_last_nonblank = None
    module_name = None
    for i, line in enumerate(out_lines):
        stripped = line.strip()
        if stripped == 'DEFINITIONS AUTOMATIC TAGS ::=':
            if module_name:
                modules[module_name]['end'] = i_last_nonblank
            module_name = last_nonblank
            modules[module_name] = {'start': i_last_nonblank }
        if stripped:
            last_nonblank = stripped
            i_last_nonblank = i

    modules[module_name]['end'] = len(out_lines)

    preclude = [
            "--\n",
            f"-- Generated using : {' '.join(sys.argv)}\n",
            "-- DO NOT EDIT BY HAND\n",
            "--\n"]
    for name, bounds in modules.items():
        start = bounds['start']
        end = bounds['end']
        asn_file = f"{asn_dir}/{name}.asn"
        with open(asn_file, 'w') as outfile:
            outfile.writelines(preclude)
            outfile.writelines(out_lines[start:end])


if __name__ == '__main__':

    if len(sys.argv) < 4:
        print("usage: parse_spec.py <spec.docx> -d <out dir>")
        sys.exit(1)

    spec_file = sys.argv[1]
    asn_dir = sys.argv[3]
    main(spec_file, asn_dir)
