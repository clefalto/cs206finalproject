# Final project for CS 206 - Graduate Software Testing

I created prompts and wrote a few scripts to automatically generate tests for a given dataset of simple (buggy) Python programs. 

## Workflow

`identify_structure.py`
First, I used [tree-sitter](https://tree-sitter.github.io/tree-sitter/) to parse out the structure of each of the given programs (in dataset.zip). The program outputs json structure files that describe the layout of each python program in a unambiguous way.

These json files were given to [Cline](https://cline.bot/) in the shell script `generate_properties.sh` to identify semantic properties in each structure file, which outputs into 'property' json files. 

Lastly, the property json files are used to generate pytest suites. This is also done through a Cline prompt, in `generate_tests.sh`. 

See the .pdfs for my report I submitted for the class.
