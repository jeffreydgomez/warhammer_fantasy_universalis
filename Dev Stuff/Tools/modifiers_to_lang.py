## use: pip install pyperclip

## in vscode download the extention: code runner
## copy the text you want to transform
## open the modifier file, right-click the this python file and press run
## the lang is now in you clipboard

import pyperclip
import re

input_text = pyperclip.paste()
pattern = re.compile(r'(\w+)\s*=\s*{')
keys = pattern.findall(input_text) 
output = "\n".join([f" {key}: \"EXAMPLE_TEXT\"" for key in keys])

pyperclip.copy(output)