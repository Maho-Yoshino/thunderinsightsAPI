#!/usr/bin/env python

import json
import sys
from app.wt_bin_parser.data_parser import parse_binary_data
from app.wt_bin_parser.utils import parse_args, read_input_file
#from data_parser import parse_binary_data
#from utils import parse_args, read_input_file

def parse_data(bin_data):

    results = parse_binary_data(bin_data)
    
    return results

def parse_file(filename):

    bin_data = read_input_file(filename)

    results = parse_binary_data(bin_data)

    return results


if __name__ == "__main__":
    main()
