#!/bin/bash

# query the cline cli for every structure we generated earlier to extract the properties
# we have to do this in a loop because the cline cli doesn't support batch processing

PROMPT_BASE=$(cat <<'EOF'
Please identify structure aligned semantic properties from the code structure file located at FILE_PATH. Separate scopes into branch-level and function-level properties. A branch-level property holds only under certain conditions. A function-level property holds for all executions of the function. Also identify invariants, pre-conditions, post-conditions, metamorphic relations, and any other property types that help capture the intended semantics of the program.
Output the branch-level properties you identify in a JSON file with the following format:
{
    "scope": "branch",
    "function": name of function,
    "condition": branch condition (e.g. "len\(xs\) == 0"),
    "property": property shorthand (e.g. "identity_on_empty"),
    "formal": formalized property (e.g. "normalize\(xs\) == xs")
}
Output all the function-level properties you identify in the same JSON file with the following format:
{
    "scope": "function",
    "function": function name (e.g. "normalize"),
    "property": property shorthand (e.g. "unit_sum"),
    "precondition": condition that must be true for the property to hold (e.g. "sum\(xs\) != 0"),
    "formal": formalized property (e.g. "sum\(normalize\(xs\)\) == 1")
}
Create a JSON file in the properties directory with the same name as the structure file but with _properties.json suffix. For example, if the structure file is ad_mix_structure.json, the properties file should be ad_mix_properties.json. The JSON file should contain a list of all the properties you identified for that structure.
The structure of the program to analyze is: 
EOF
)

STRUCTURE_DIR=structures
OUTPUT_DIR=properties

# create the output directory if it doesn't exist
mkdir -p $OUTPUT_DIR
# loop through each structure and query cline
for STRUCTURE in $(ls $STRUCTURE_DIR/*_structure.json); do
    STRUCTURE_NAME=$(basename ${STRUCTURE})
    STRUCTURE_CONTENTS=$(cat $STRUCTURE)
    PROMPT="${PROMPT_BASE} ${STRUCTURE_CONTENTS}"
    file_name=${OUTPUT_DIR}/"${STRUCTURE_NAME%_structure.json}_properties.json"
    # touch ${file_name}
    # echo "cline prompt: cline -y "${PROMPT/FILE_NAME/$STRUCTURE_NAME}" > ${file_name}"
    echo prompting for ${STRUCTURE}...
    cline -y "${PROMPT/FILE_PATH/$STRUCTURE}"
    # echo "cline_prompt: cline -y "${PROMPT/FILE_PATH/$STRUCTURE}" > ${file_name}"
done