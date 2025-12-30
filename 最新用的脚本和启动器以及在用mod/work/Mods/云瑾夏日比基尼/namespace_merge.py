# Author: qwerty3yuiop
# Special Thanks:
#   SilentNightSound#7430 much of this guy's code was used for this
#   bloodreign616#4766 (pirilika) did much of the testing on this script
# V3.1 of Mod Merger/Toggle Creator Script utilizing namespaces

# Merges multiple mods into one, utilizing name spaces

# USAGE: Run this script in a folder which contains all the mods you want to merge
# So if you want to merge mods CharA, CharB, and CharC put all 3 folders in the same folder as this script and run it

# This script will automatically search through all subfolders to find mod ini files.
# It will not use .ini if that ini path/name contains "disabled"

# NOTE: This script will only function properly on mods generated using the 3dmigoto GIMI plugin

import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generates a merged mod from several mod folders")
    parser.add_argument("-r", "--root", type=str,  default=".",  help="Location to use to create mod")
    parser.add_argument("-d", "--delete", action="store_true", help="run the script in delete mode")
    parser.add_argument("-v", "--vanilla", action="store_true",  help="exclude vanilla outifit as a part of the mod")
    parser.add_argument("-n", "--name", type=str,  default="master.ini", help="(not functional)")
    args = parser.parse_args()
    
    # run delete mode if delete arguement is used
    if args.delete:
        delete_main(args.root)
        return
    
    print("\nGenshin and Star Rail Mod Merger/Toggle Creator Script Utilizing Namespaces\n")
    
    # searches for files returns if none found
    print("\nSearching for .ini files")
    ini_files = collect_ini(args.root, args.name)
    if not ini_files:
        print("Found no .ini files - make sure the mod folders are in the same folder as this script.")
        return
    # Place holder for the vanilla outfit
    ini_files.insert(0, None)
    # lists all found files
    print("\nFound:")
    print("\t0:  Vanilla Outfit")
    for i, ini_file in enumerate(ini_files):
        if i != 0:
            print(f"\t{i}:  {ini_file}")
    
    # order of merge given by sorting the list ini_files
    print("\nThis script will merge using the order listed above (0 is the default the mod will start with, and it will cycle 0,1,2,3,4,0,1...etc)")
    print("If this is fine, please press ENTER. If not, please enter the order you want the script to merge the mods (example: 3 0 1 2)")
    print("If you enter less than the total number, this script will only merge those listed.\n")
    print("Vanilla outfit will be bound to the first value by default. You can list the number wherever you want like with all other files.")
    if args.vanilla:
        print("The vanilla outfit will be removed at the end it is safe to press enter or select an order you can still include vanilla if you add it to your order\n")
    ini_files = get_user_order(ini_files)
    if args.vanilla and ini_files[0] == None:
        ini_files.pop(0)
    # the name of the namespace cause I don't want to deal with finding it
    print("\nPlease enter the name of the object this merged mod is for (no spaces)\n")
    name = input()
    while not name:
        print("\nPlease enter a name\n")
        name = input()
    # sets key to cycle forward
    print("\nPlease enter the key that will be used to cycle mods. Key must be a single letter\n")
    key = input()
    while not key or len(key) != 1:
        print("\nKey not recognized, must be a single letter\n")
        key = input()
    key = key.lower()
    # sets key to cycle backward
    print("\nPlease enter the key that will be used to cycle mods backwards. Key must be a single letter\n")
    back = input()
    while not back or len(back) != 1:
        print("\nKey not recognized, must be a single letter\n")
        back = input()
    back = back.lower()

    # generating backup inis
    print("generating backups")
    generate_backup(ini_files)

    # Generates the namespace for the master file
    constants =    f"namespace = {name}\Master\n; Constants ---------------------------\n\n"
    overrides =    "; Overrides ---------------------------\n\n"

    swapvar = "swapvar"
    # adds the [Constants] section
    constants += f"[Constants]\nglobal persist ${swapvar} = 0\n"
    constants += f"global $active\n"
    constants += "global $creditinfo = 0\n"
    # adds the [KeySwap] section
    constants += f"\n[KeySwap]\n"
    constants += f"condition = $active == 1\n"
    constants += f"key = {key}\nback = {back}\ntype = cycle\n${swapvar} = {','.join([str(x) for x in range(len(ini_files))])}\n$creditinfo = 0\n\n"
    # adds the [Present] section to not swap when character is not active
    constants += f"[Present]\n"
    constants += f"post $active = 0\n"

    # this gets the position override and may cause problems if mods for multiple charters are added as that character will not be detected
    overrides += f"[TextureOverride{name}Position]\n"
    for file in ini_files:
        if file != None:
            temp = get_position_hash(str(file))
            if temp != ";None found\n":
                overrides += temp
                break
    overrides += "$active = 1\n"

    # adds the neccessary if statements into the ini files
    print("Modifying inis...")
    count = 0
    for ini_file in ini_files:
        if ini_file != None:
            edit_ini(str(ini_file),name,count)
        count += 1
    
    # removes the null value now
    try:
        ini_files.remove(None)
    except ValueError:
        print()
    print("Printing results")
    result = f"; Merged Mod: {', '.join([x for x in ini_files])}\n\n"
    result += constants
    result += overrides
    result += "\n\n"
    result += "; .ini generated by GIMI (Genshin-Impact-Model-Importer) mod merger script utilizing namespaces\n"
    result += "; If you have any issues or find any bugs dm qwerty3yuiop on discord or leave a comment on game banana"

    with open(f"Master{name}.ini", "w", encoding="utf-8") as f:
        f.write(result)

    print("All operations completed")

# delete script method
def delete_main(root):
    print("\nNamespace Merged Mod Unmerger\n")
    print("\nTHIS SCRIPT WILL DELETE FILES FROM YOUR DEVICE USE WITH CAUTION AND MAKE BACKUPS")
    print("press enter to procede or enter anything else to exit")
    userin = input()
    if userin != "":
        print("exiting")
        return
    # searches for active files returns if none found
    print("\nSearching for paths containing active inis")
    ini_paths = collect_ini(root, "none")
    if not ini_paths:
        print("Found no .ini files - make sure the mod folders are in the same folder as this script.")
        return
    # lists all found files
    print("\nFound:")
    for i, ini_file in enumerate(ini_paths):
        print(f"\t{i}:  {ini_file}")
    print("All inis displayed above will be deleted and their backups will be restored")
    print("Press enter to procede with the delete or enter a number to remove a file from the deletion list.")
    print("ONLY ENTER ONE NUMBER! you will be able to remove other paths from deletion list")
    userin = input()
    while userin != "":
        try:
            ini_paths.pop(int(userin))
            print(f"\nremoved path number {userin}")
        except:
            print(f"\nUnable to remove {userin} from deletion list")
        finally:
            print("Current Deletion List:")
            for i, ini_file in enumerate(ini_paths):
                print(f"\t{i}:  {ini_file}")
        print("Press enter to procede with the delete or enter a number to remove a file from the deletion list.")
        print("ONLY ENTER ONE NUMBER! you will be able to remove other paths from deletion list")
        userin = input()
    try:
        for file in ini_paths:
            # deletes the file
            os.remove(str(file))
            # renames the backup file
            try:
                rename_file(file)
            except:
                print(f"No back up file found for {file}")
        
        print("All operations completed")
    except:
        print("something went wrong")

# Collects all .ini files from current folder and subfolders
def collect_ini(path, ignore):
    ini_files = []
    for root, dir, files in os.walk(path):
        if "disabled" in root.lower():
            continue
        for file in files:
            if "disabled" in file.lower() or ignore.lower() in file.lower():
                continue
            if os.path.splitext(file)[1] == ".ini":
                ini_files.append(os.path.join(root, file))
    return ini_files

# Gets the user's preferred order to merge mod files
def get_user_order(ini_files):

    choice = input()
    # User entered data before pressing enter
    while choice:
        choice = choice.strip().split(" ")

        if len(choice) > len(ini_files):
            print("\nERROR: please only enter up to the number of the original mods\n")
            choice = input()
        else:
            try:
                result = []
                choice = [int(x) for x in choice]
                if len(set(choice)) != len(choice):
                    print("\nERROR: please enter each mod number at most once\n")
                    choice = input()
                elif max(choice) >= len(ini_files):
                    print("\nERROR: selected index is greater than the largest available\n")
                    choice = input()
                elif min(choice) < 0:
                    print("\nERROR: selected index is less than 0\n")
                    choice = input()
                    print()
                else:
                    for x in choice:
                        result.append(ini_files[x])
                    return result
            except ValueError:
                print("\nERROR: please only enter the index of the mods you want to merge separated by spaces (example: 3 0 1 2)\n")
                choice = input()

    # User didn't enter anything and just pressed enter
    return ini_files

# Editing existing inis and adding needed text at the end for shader and texture overrides.
def edit_ini(path, name, num):
    with open(path, 'r') as file:
        lines = file.readlines()
    found = False
    count = 0
    max = len(lines)-1
    block = []
    with open(path, 'w') as file:
        for line in lines:
            # Ends the if when a line with [ or when end of file is reached
            # meant to end on next overide
            if found and line.startswith('[') or count == max:
                block.append(line)
                line = comment_fix(block)
                block = []
                found = False
            # if there is already a match priority remove it
            elif found and line.lower().startswith('match_priority'):
                block.append("")
            # adds a tab to every line in the if
            elif found:
                line = "\t" + line
                block.append(line)
            # looks for lines that start with a hash and starts an if statement.
            elif line.strip().lower().startswith('hash = ') or line.strip().lower().startswith('hash='):
                # adds namespace also this line is by ricochet_7
                line = line + f'match_priority = {num}\n' + f'if $\{name}\Master\swapvar=={num}\n'
                found = True
                block.append(line)
            if not found:
                file.write(line)
            count += 1

# makes sure to place the endif immediatly after code to be enclosed
def comment_fix(block):
    index = len(block) - 1
    # cycle from the bottom
    for line in reversed(block):
        # If text that is not ; "" [ are found, end if is placed there
        if not line.strip().startswith(';') and not line.strip().startswith('[') and not line.strip() == "":
            block[index] = block[index].rstrip()+"\nendif\n\n"
            break
        # removes any indentation given to comments as a result of the previous function
        elif line.strip().startswith(';'):
            block[index] = block[index].lstrip()
        index -= 1
    line = ""
    for x in block:
        line = line + x
    block = []
    return line

# makes a copy of a file that is DISABLED
def generate_backup(file_list):
    for file_path in file_list:
        if file_path != None:
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            new_file_path = os.path.join(dir_name, 'DISABLED' + base_name)
            with open(file_path, 'r') as original_file, open(new_file_path, 'w') as new_file:
                new_file.write(original_file.read())

# finds the position override of a a character and returns it
def get_position_hash(path):
    with open(path, 'r') as file:
        lines = file.readlines()
        found = False
        for line in lines:
            # Ends the if when a line with [] or ; is found
            if line.startswith('[TextureOverride') and line.endswith('Position]\n'):
                found = True
            if found and (line.strip().lower().startswith('hash = ') or line.strip().lower().startswith('hash=')):
                return line
        return ";None found\n"
    
# renames file
def rename_file(file_path):
    if file_path != None:
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        os.rename(dir_name + '\\DISABLED' + base_name, dir_name + '\\' + base_name)

if __name__ == "__main__":
    main()
    