## use: pip install pyperclip

## in vscode download the extention: code runner
## copy the text you want to transform
## open the modifier file, right-click the this python file and press run
## the lang is now in you clipboard

## !!!!!!!!! for autofill, put ## above the event as title and put # above an option for its name

### I hate making tools like this, luckily chat knows regex

import re
import pyperclip

# Read everything you've copied (multiple events)
text = pyperclip.paste()
lines = text.splitlines()

# Helper to split into event blocks (country_event or province_event) with their titles
def split_events(lines):
    events = []  # list of (title_comment, block_lines)
    i = 0
    while i < len(lines):
        # Match country_event or province_event
        if re.match(r"^\s*(?:country_event|province_event)\s*=\s*{", lines[i]):
            # Find preceding title comment ##
            title_comment = None
            j = i - 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            if j >= 0:
                m = re.match(r"^\s*##\s*(.+)$", lines[j])
                if m:
                    title_comment = m.group(1).strip()
            # Collect the block until matching brace closes
            brace_count = 0
            k = i
            while k < len(lines):
                brace_count += lines[k].count('{') - lines[k].count('}')
                if brace_count == 0:
                    break
                k += 1
            block = lines[i:k+1]
            events.append((title_comment, block))
            i = k + 1
        else:
            i += 1
    return events

# Process each event block
loc_lines = ["l_english:"]
events = split_events(lines)
for title_comment, block in events:
    block_text = "\n".join(block)
    # extract title and desc keys
    title_key_match = re.search(r'^\s*title\s*=\s*(\S+)', block_text, re.MULTILINE)
    desc_key_match  = re.search(r'^\s*desc\s*=\s*(\S+)', block_text, re.MULTILINE)
    title_key = title_key_match.group(1) if title_key_match else 'missing_title'
    desc_key  = desc_key_match.group(1)  if desc_key_match  else 'missing_desc'
    # add title localization
    if title_comment:
        loc_lines.append(f"  {title_key}: \"{title_comment}\"")
    else:
        loc_lines.append(f"  {title_key}: \"EXAMPLE_TITLE\"")
    # description placeholder
    loc_lines.append(f"  {desc_key}: \"EXAMPLE_DESC\"")
    # find options within this block
    i = 0
    while i < len(block):
        # detect option comment (# comment inside block)
        cm = re.match(r"^\s*#\s*(.+)$", block[i])
        if cm:
            comment = cm.group(1).strip()
            # find next option start
            j = i + 1
            while j < len(block) and not re.match(r"^\s*option\s*=", block[j]):
                j += 1
            if j < len(block):
                # scan option block for name key
                brace_count = block[j].count('{') - block[j].count('}')
                k = j + 1
                name_key = None
                while k < len(block) and brace_count > 0:
                    brace_count += block[k].count('{') - block[k].count('}')
                    nm = re.match(r"^\s*name\s*=\s*(\S+)", block[k])
                    if nm and name_key is None:
                        name_key = nm.group(1)
                    k += 1
                if name_key:
                    loc_lines.append(f"  {name_key}: \"{comment}\"")
                i = k
                continue
        i += 1

# join and copy
output = "\n".join(loc_lines)
pyperclip.copy(output)
