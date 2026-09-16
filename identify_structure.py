import json
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node, Tree, Query

PY_LANGUAGE = Language(tspython.language())

parser = Parser(PY_LANGUAGE)

# source_code = """
# def normalize(xs):
#     if len(xs) == 0:
#         if 3 < 2:
#             print("This will never be printed")
#         return xs
#     s = sum(xs)
#     return [x / s for x in xs]

# def gromble(x):
#     if x > 0:
#         for i in range(10):
#             if i == 5:
#                 print("meowy!")
#         return "positive"
#     elif x < 0:
#         return "negative"
#     else:
#         return "zero"
# """

def get_node_text(node, _source_code):  
    return _source_code[node.start_byte:node.end_byte]


def get_nodes_after(node):
    nodes_after = []
    
    # 1. Start with the current node's next sibling
    current_sibling = node.next_sibling
    while current_sibling:
        # 2. Add just the sibling to the list
        nodes_after.append(current_sibling)
        
        # 3. Move to the next sibling
        current_sibling = current_sibling.next_sibling
        
    return nodes_after

def extract_nearest_if_branch(node, source_code):

    if node.type == "if_statement":
        return parse_branch(node, source_code)
    else:
        pass
        # print("no if statement found in node: " + str(node.text.decode('utf8')))
        # print("the children of the current node are: " + str([child.text.decode('utf8') for child in node.children]))

    for child in node.children:
        branch = extract_nearest_if_branch(child, source_code)
        if branch is not None:
            return branch
    
    # if node.next_sibling:
    #     return extract_nearest_if_branch(node.next_sibling, source_code)

    return None


def extract_early_return_and_value(consequence_node, source_code):
    return_value = None
    raises_exception = False
    for child in consequence_node.children:
        if child.type == "return_statement":
            return_value = child.children[1].text.decode('utf8')
        # an exception is also an early exit
        elif child.type == "raise_statement":
            raises_exception = True
    
    return return_value, raises_exception

def parse_branch(if_node, source_code):
    branches = []

    print("CURRENT:" + str(if_node))

    condition_list = []
    
    condition_node = if_node.child_by_field_name("condition")
    consequence_node = if_node.child_by_field_name("consequence")

    nested_branches = extract_nearest_if_branch(consequence_node, source_code)
    print("NESTED: " + str(nested_branches))

    condition_text = get_node_text(condition_node, source_code)
    body_text = get_node_text(consequence_node, source_code).strip()

    condition_list.append(condition_text)

    # extract return value if exists
    return_value, raises_exception = extract_early_return_and_value(consequence_node, source_code)

    branches.append({
        "type": "if" if len(branches) == 0 else "elif",
        "condition": condition_text,
        "branches": nested_branches if 'nested_branches' in locals() else None,
        "body_contains": body_text,
        "returns": return_value,
        "early_exit": True if return_value is not None or raises_exception else False
    })

    # get all the alts
    alts = if_node.children_by_field_name("alternative")

    for alt in alts:
        # print("ALT:" + str(alt))
        if alt.type == "elif_clause":
            condition_node = alt.child_by_field_name("condition")
            consequence_node = alt.child_by_field_name("consequence")

            condition_text = get_node_text(condition_node, source_code)
            body_text = get_node_text(consequence_node, source_code).strip()

            condition_list.append(condition_text)

            # extract return value if exists
            return_value, raises_exception = extract_early_return_and_value(consequence_node, source_code)

            branches.append({
                "type": "elif",
                "condition": condition_text,
                "body_contains": body_text,
                "returns": return_value,
                "early_exit": True if return_value is not None or raises_exception else False
            })

        elif alt.type == "else_clause":
            body_text = get_node_text(alt, source_code).strip()
            body_node = alt.child_by_field_name("body")
            
            return_value, raises_exception = extract_early_return_and_value(body_node, source_code)
            
            # combine all previous conditions for the else clause
            else_condition = " and ".join(condition_list)  
            # negate it
            else_condition = "not (" + else_condition + ")"

            branches.append({
                "type": "else",
                "condition": else_condition,
                "body_contains": body_text,
                "returns": return_value,
                "early_exit": True if return_value is not None or raises_exception else False
            })
        
    
    # implicit else:
    # check if the any of the branches have a return statement
    # if so, the code after the last branch will be executed as an else clause
    if not any(branch.get("type") == "else" for branch in branches):
        print("checking for implicit else clause...")
        for branch in branches:
            print("branch: " + str(branch))
            # if it has a return
            if branch.get("early_exit"):
                # get the last branch's condition
                cond = branch.get("condition")
                # negate it for the else clause
                implicit_else_condition = "not (" + cond + ")" if cond else None

                # get the code after the last branch
                nodes_after = get_nodes_after(if_node)
                for n in nodes_after:
                    if n.type == "return_statement":
                        return_value = n.children[1].text.decode('utf8')
                        break
                body_text = "\n".join([get_node_text(n, source_code) for n in nodes_after]).strip()

                branches.append({
                    "type": "else",
                    "condition": implicit_else_condition,
                    "body_contains": body_text,
                    "returns": return_value,
                    "early_exit": False
                })
                break

    return branches


def parse_function(node: Node):
    func = {}
    name_node = node.child_by_field_name("name")
    func["name"] = name_node.text.decode('utf8')
    param_node = node.child_by_field_name("parameters")
    params = []
    for child in param_node.children:
        if child.type == "identifier":
            params.append(child.text.decode('utf8'))
    func["parameters"] = params

    body_node = node.child_by_field_name("body")
    branches = []

    return_value = ""

    for c in body_node.children:
        cf = extract_nearest_if_branch(c, source_code)
        print(cf)
        if cf is not None:
            branches.append(cf[0]) if len(cf) == 1 else branches.append(cf)
        
        if c.type == "return_statement":
            return_value = c.children[1].text.decode('utf8')

    func["branches"] = branches
    func["returns"] = return_value

    return func

def identify_code_structure(source_code: str):
    tree = parser.parse(bytes(source_code, "utf8"))
    root = tree.root_node
    result = {"functions": []}
    for node in root.children:
        if node.type == "function_definition":
            func = parse_function(node)
            result["functions"].append(func)
    return result;


if __name__ == "__main__":
    # run it for EVERY file in dataset/python_programs
    dir_path = Path("dataset/python_programs")
    output_path = Path("structures")
    output_path.mkdir(exist_ok=True)
    for file_path in dir_path.glob("*.py"):
        with open(file_path, "r") as f:
            source_code = f.read()
        json_string = identify_code_structure(source_code)
        output_file = output_path / (file_path.stem + "_structure.json")
        with open(output_file, "w") as f:
            json.dump(json_string, f, indent=4)


# format for json structure thing file thing
# function: function name
# parameters: []
# branches: [] (within the function):
#   type
#   condition (if has condition)
#   body_contains (if has no return)
#   returns (if has return)

# will give this to cline i guess to identify semantic properties
# 