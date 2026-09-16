# def parse_branch(node: Node, cursor, type):
#     visited_children = False
#     cursor = tree.walk()
#     cursor.reset(node)
#     branch = {}
#     branch["type"] = type
#     cond_node = cursor.node.child_by_field_name("condition")
#     if cond_node:
#         branch["condition"] = cond_node.text.decode('utf8')
#     if (type == "if"):
#         branch["body_contains"] = node.child_by_field_name("consequence").text.decode('utf8')
#     elif (type == "else"):
#         branch["body_contains"] = node.child_by_field_name("body").text.decode('utf8')
#     print("BODY CONTAINS: " + branch["body_contains"])

#     cursor.goto_first_child()
    
#     while True:
#         if not visited_children:
#             if cursor.node.type == "return_statement":
#                 pass
#                 branch["returns"] = cursor.node.children[1].text.decode('utf8')
        
#             elif cursor.node.type == "if_statement":
#                 nested_branch = parse_branch(cursor.node, tree, "if")
#                 branch["branches"] = branch.get("branches", []) + [nested_branch]
#             elif cursor.node.type == "else_clause":
#                 else_branch = parse_branch(cursor.node, tree, "else")
#                 branch["branches"] = branch.get("branches", []) + [else_branch]
#             if not cursor.goto_first_child():
#                 visited_children = True
#         elif cursor.goto_next_sibling():
#             visited_children = False
#         elif not cursor.goto_parent():
#             break
#     return branch


    # cursor = tree.walk()
    # cursor.reset(node)  
    # func = {}
    # func["name"] = node.child_by_field_name("name").text.decode('utf8')
    # param_str = node.child_by_field_name("parameters").text.decode('utf8')
    # # remove the leading and trailing parentheses
    # param_str = param_str.removeprefix("(")
    # param_str = param_str.removesuffix(")")
    # func["parameters"] = param_str.split(', ')
    # parse through the function body to identify branches and returns

    # while True:
    #     if not visited_children:
    #         if cursor.node.type == "if_statement":
    #             branch = parse_branch(cursor.node, tree)
    #             func["branches"] = func.get("branches", []) + [branch]
    #             if branch.get("returns"):
    #                 # if the branch has a return, the rest of the function body will be executed as an else branch
    #                 # add it to the branches list as well
    #                 else_branch = {"type": "else"}
    #                 nodes_after = get_nodes_after(cursor.node)
    #                 else_branch["body_contains"] = [n.text.decode('utf8') for n in nodes_after]
    #                 print(else_branch)
                    
    #             print(branch)
    #         elif cursor.node.type == "else_clause":
    #             print("else clause!")
    #         # elif cursor.node.type == "return_statement":
    #         #     pass
    #         #     print("RETURNS: " + cursor.node.children[1].text.decode('utf8'))
    #         #     # func["returns"] = cursor.node.child_by_field_name("value").text.decode('utf8')
        
    #         if not cursor.goto_first_child(): # don't go to the children if we already parsed it earlier
    #             visited_children = True
    #     elif cursor.goto_next_sibling():
    #         visited_children = False
    #     elif not cursor.goto_parent():
    #         break 



            # if branch.get("returns"):
            #     # if the 'if' branch has a return, the rest of the function body will be executed as an else branch
            #     # add it to the branches list as well
            #     if branch.get("condition"):
            #         else_condition = "not (" + branch["condition"] + ")" # negate the condition for the else clause
            #         else_branch = {"type": "else", "condition": else_condition}
            #     else_branch = {"type": "implicit_else"}
            #     nodes_after = get_nodes_after(child)
            #     print("NODES AFTER:" + str(nodes_after))
            #     # it looks kinda weird when you do this
            #     else_branch["body_contains"] = [n.text.decode('utf8') for n in nodes_after]
            #     print(else_branch)
            #     branches.append(else_branch)

        # elif child.type == "else_clause":
        #     else_branch = parse_branch(child, tree, "else")
        #     else_branch["body_contains"] = child.child_by_field_name("body").text.decode('utf8')
        #     branches.append(else_branch)