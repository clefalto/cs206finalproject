#!/bin/bash

# query the cline cli for every property we generated earlier to make tests!
# we have to do this in a loop because the cline cli doesn't support batch processing
# this is bashically just the same script as generate_properties.sh but with a different prompt and output file name

PROMPT_BASE=$(cat <<'EOF'

Write tests using the Hypothesis testing framework for Python to exercise all of the semantic properties you identified earlier. These semantic properties are located in FILE_PATH. Generate your test file with the "_test.py" suffix in the directory called "tests". Do not execute the tests.
The semantic properties of the program to analyze are as follows:

EOF
)

PROPERTY_DIR=properties
OUTPUT_DIR=tests

# ls $PROPERTY_DIR/*properties.json

# create the output directory if it doesn't exist
mkdir -p $OUTPUT_DIR
# loop through each structure and query cline
for PROPERTIES in $(ls $PROPERTY_DIR/*properties.json); do
    PROPERTIES_NAME=$(basename ${PROPERTIES})
    PROPERTIES_CONTENTS=$(cat $PROPERTIES)
    PROMPT="${PROMPT_BASE} ${PROPERTIES_CONTENTS}"
    # file_name=${OUTPUT_DIR}/"${PROPERTIES_NAME%_properties.json}_test.py" # kinda not doing this anymore
    # touch ${file_name}
    # echo "cline prompt: cline -y "${PROMPT/FILE_NAME/$STRUCTURE_NAME}" > ${file_name}"
    echo prompting for ${PROPERTIES}...
    cline -y "${PROMPT/FILE_PATH/$PROPERTIES}" | tee tests_logs/${PROPERTIES_NAME%_properties.json}_cline_output.txt
    # echo "cline_prompt: cline -y "${PROMPT/FILE_PATH/$STRUCTURE}" > ${file_name}"
done