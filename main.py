import json
import os
import DarwinUtilityScriptCompiler as compiler
import ProcessorMethods as processor

entries = {}

if os.path.exists("entries.json"):
    file = open("entries.json", "r")
    entriesJson = file.read()
    file.close()
    entries = json.loads(entriesJson)
else:
    file = open("entries.json", "w")
    file.write("{}")
    file.close()

def splitStr(s: str):
    ls = []
    item = ""
    splitable = True
    for i in s.strip():
        if i == "\"": splitable = not splitable
        if i == " " and len(item.strip()) > 0 and splitable:
            ls.append(item.strip())
            item = ""
        item = item + i
    if splitable:
        if len(item.strip()) > 0: ls.append(item.strip())
        return ls

def init():
    while True:
        cmds = splitStr(str(input(">>")))
        cmd = cmds[0]

        if cmd == "exit": break
        elif cmd == "run":
            p1 = cmds[1].replace("\"", "")
            if "$" in p1: p1 = entries[p1.replace("$", "")]
            file = open(p1, "r")
            processor.run(file.readlines())
        elif cmd == "compile":
            p1 = cmds[1].replace("\"", "")
            p2 = cmds[2].replace("\"", "")
            if "$" in p1: p1 = entries[p1.replace("$", "")]
            if "$" in p2: p2 = entries[p2.replace("$", "")]
            compiler.compile(p1, p2)
        elif cmd == "mkentry":
            entries[cmds[1]] = str(cmds[2]).replace("\"", "")
            file = open("entries.json", "w")
            file.write(json.dumps(entries))
            file.close()
        elif cmd == "rmentry":
            entries.pop(cmds[1])
            file = open("entries.json", "w")
            file.write(json.dumps(entries))
            file.close()
        elif cmd == "help":
            print("compile <filename> <outputDestination>\t: To compile a file (not live)")
            print("run <filename>\t\t\t\t: To run a program (not live)")
            print("mkentry <nickname> <fileLocation>\t: To set a nickname to a file.")
            print("rmentry <nickname> \t\t\t: To remove a nickname to a file.")
            print("exit\t\t\t\t\t: To exit for simulator")
        else: print("Invalid command\nType help to show all commands")

init()

