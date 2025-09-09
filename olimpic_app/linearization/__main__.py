from xml.dom import minidom
import argparse
import sys
import os


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

linearize_parser = subparsers.add_parser(
    "linearize",
    aliases=[],
    help="Generates an LMX file from a MusicXML file"
)
linearize_parser.add_argument(
    "filename",
    type=str,
)
linearize_parser.add_argument(
    "output_filename",
    type=str
)

delinearize_parser = subparsers.add_parser(
    "delinearize",
    aliases=[],
    help="Generates a MusicXML file from an LMX file"
)
delinearize_parser.add_argument(
    "filename",
    type=str,
)
delinearize_parser.add_argument(
    "output_filename",
    type=str
)



###################
# Implementations #
###################

from .Linearizer import Linearizer
from .Delinearizer import Delinearizer
from ..symbolic.MxlFile import MxlFile
import xml.etree.ElementTree as ET
from ..symbolic.part_to_score import part_to_score


def linearize(filename: str, output_filename: str):
    if filename == "-":
        input_xml = sys.stdin.readline()
        mxl = MxlFile(ET.ElementTree(
            ET.fromstring(input_xml))
        )
    elif filename.endswith(".mxl"):
        mxl = MxlFile.load_mxl(filename)
    else:
        with open(filename, "r") as f:
            input_xml = f.read()
            mxl = MxlFile(ET.ElementTree(
                ET.fromstring(input_xml))
            )
    
    try:
        part = mxl.get_piano_part()
    except:
        part = mxl.tree.find("part")
    
    if part is None or part.tag != "part":
        print("No <part> element found.", file=sys.stderr)
        exit()
    
    linearizer = Linearizer(
        errout=sys.stderr
    )
    linearizer.process_part(part)
    output_lmx = " ".join(linearizer.output_tokens)
    
    if filename == "-":
        print(output_lmx)
    else:
        with open(output_filename, "w") as f:
            print(output_lmx, file=f)

def delinearize_helper(input_lmx: str):
    delinearizer = Delinearizer(
        errout=sys.stderr
    )
    delinearizer.process_text(input_lmx)
    score_etree = part_to_score(delinearizer.part_element)
    output_xml = ET.tostring(
        score_etree.getroot(),
        encoding="utf-8",
        xml_declaration=True
    )
    dom = minidom.parseString(output_xml)
    output_xml = dom.toprettyxml(indent="\t")

    return output_xml

def delinearize(filename: str, output_filename):
    if filename == "-":
        input_lmx = sys.stdin.readline()
    else:
        with open(filename, "r") as f:
            input_lmx = f.readline()

    output_xml = delinearize_helper(input_lmx)

    if filename == "-":
        print(output_xml)
    else:
        with open(output_filename, "w") as f:
            print(output_xml, file=f)

# version that relies on storing intermediate info as files less
def direct_delinearize(input_lmx: str):
    output_xml = delinearize_helper(input_lmx)
    return output_xml

########
# Main #
########

args = parser.parse_args()

# annotation commans
if args.command_name == "linearize":
    linearize(args.filename, args.output_filename)
elif args.command_name == "delinearize":
    delinearize(args.filename, args.output_filename)
else:
    parser.print_help()
    exit(2)
