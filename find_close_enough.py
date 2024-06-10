"""
Command line utility to find close enough recorded dubs to be reused for a given voice.
This is useful if you make minor edits to the text and want to reuse the same dub.

Usage:
python find_close_enough.py <voice>
    
    Where <voice> is the name of the voice to search for close enough dubs.
    
The script will output a report in HTML format with the potential dubs to be copied over.
You can then decide to copy them over or not.
"""
import sys
import os
import shutil
from collections import defaultdict
import json

from thefuzz import fuzz
import difflib
from tqdm import tqdm

from locations import VOICES_DIR, DUBS_FILE_PATH, BACKUP_DUBS_FILE_PATH, USED_DUBS_FILE_PATH

LENGTH_DIFF_THRESHOLD = 5
EDIT_RATIO_THRESHOLD = 90

if len(sys.argv) < 2:
    print("Usage: python find_close_enough.py <voice>")
    sys.exit(1)

voice = sys.argv[1]

# Look up all the used dubs
# Check if they are missing a dubbing
# Look at all the existing speeches text and see if they are similar
#   ignore capitals, punctuation, whitespace, edit distance being less than 5?
# If they are similar, make a list of the potential ones to be copied over

def clean_text(text):
    text = text.lower()
    text = ''.join(e for e in text if e.isalnum())
    return text

def show_diff(seqm):
    """
    Unify operations between two compared strings
    seqm is a difflib.SequenceMatcher instance whose a & b are strings
    
    https://stackoverflow.com/questions/774316/python-difflib-highlighting-differences-inline
    """
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<ins>" + seqm.b[b0:b1] + "</ins>")
        elif opcode == 'delete':
            output.append("<del>" + seqm.a[a0:a1] + "</del>")
        elif opcode == 'replace':
            #raise NotImplementedError( "what to do with 'replace' opcode?" )
            output.append("<ins>" + seqm.b[b0:b1] + "</ins>")
            output.append("<del>" + seqm.a[a0:a1] + "</del>")
        else:
            raise RuntimeError( f"unexpected opcode unknown opcode {opcode}" )
    return ''.join(output)


with open(USED_DUBS_FILE_PATH) as used_file:
    used = json.load(used_file)

missing_dubs = []
for hash_name, usages in tqdm(used.items()):
    potential_dub_path = os.path.join(VOICES_DIR, voice, hash_name+'.mp3')
    if not os.path.exists(potential_dub_path):
        #print(hash_name, [usage['label'] for usage in usages])
        missing_dubs.append(hash_name)
        
with open(DUBS_FILE_PATH) as dub_file:
    dubs = json.load(dub_file)

close_enough_matches = defaultdict(list)
for hash_name in tqdm(missing_dubs):
    actual_text = dubs[hash_name]
    for other_hash_name, other_text in dubs.items():
        if other_hash_name == hash_name:
            continue
        actual, other = clean_text(actual_text), clean_text(other_text)
        if abs(len(actual) - len(other)) < LENGTH_DIFF_THRESHOLD:
            continue
        difference = fuzz.ratio(actual, other)
        if difference > EDIT_RATIO_THRESHOLD:
            close_enough_matches[hash_name].append((other_hash_name, other_text, actual_text, actual, other, difference))
            
REPORT_PATH = "close_enough_report.html"
with open(REPORT_PATH, 'w') as report_file:
    report_file.write("<html><body>")
    #html_differ = difflib.HtmlDiff(wrapcolumn=80)
    handled = {}
    for hash_name, options in tqdm(close_enough_matches.items()):
        if not options:
            report_file.write(f"No options for <span>{hash_name}</span>: <pre>{dubs[hash_name][:50]}</pre><br/>\n")
        else:
            for (other_hash_name, other_text, actual_text, actual, other, difference) in options:
                potential_dub_path = os.path.join(VOICES_DIR, voice, other_hash_name+'.mp3')
                if os.path.exists(potential_dub_path):
                    report_file.write(f"Found <span>{hash_name}</span> in <span>{other_hash_name}</span> (difference: {difference})<br/>\n")
                    sm = difflib.SequenceMatcher(None, other_text, actual_text)
                    report_file.write(f"<pre>{show_diff(sm)}</pre>")
                    handled[hash_name] = other_hash_name
                    #report_file.write(f"<table><tr><td><pre>{actual_text}</pre></td><td><pre>{other_text}</pre></td></tr></table>\n")
                    #table = html_differ.make_table(actual_text.splitlines(), other_text.splitlines())
                    #report_file.write(table)
    report_file.write("No options:<br><pre>")
    unhandled = 0
    for hash_name in missing_dubs:
        if hash_name not in handled:
            report_file.write(f"{hash_name}: {dubs[hash_name][:50]}\n")
            unhandled += 1
    report_file.write("</pre>")
    report_file.write(f"Total unhandled: {unhandled}<br>")
    report_file.write(f"Total able to be reused: {len(handled)}<br>")
    report_file.write("</body></html>")
    
print(f"Total unhandled: {unhandled}")
print(f"Total able to be reused: {len(handled)}")
print("Report written to:", REPORT_PATH)

print(f"Prepared to copy over the {len(handled)} dubs. Type 'Y' to continue.")
decision = input("[Y/N]: ")

if decision == 'Y':
    for missing, found in handled.items():
        missing, found = os.path.join(VOICES_DIR, voice, missing+'.mp3'), os.path.join(VOICES_DIR, voice, found+'.mp3')
        if os.path.exists(missing):
            print(f"Skipping {missing} because it already exists.")
            continue
        shutil.copy(found, missing)
else:
    print("Aborting.")