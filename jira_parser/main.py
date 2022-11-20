from jira import JIRA, JIRAError
import json
import sys
import argparse
import logging
import time




# variables
countries = []
unique_countries = []
notes = []
undescribed = []







# main function all others start here
def main(sys_args):
    # here is a logger for system output
    logger = initiate_logger()
    


    # let's parse the json file somefile.json
    filename = "somefile.json"
    logger.info("Start parsing the file: " + filename)
    notes = parse_json_file(filename)
    logger.info("The file " + filename + " was parsed successfully")


    # parse arguments sys_args that comes from cmd line like "python main.py sys_args"
    parser = argparse.ArgumentParser(description="Password to connect to JIRA")
    parser.add_argument("pass_to_jira", type=str, help="Password to connect to JIRA")
    api_token = parser.parse_args(sys_args)

    # connect to jira with an API token that comes from the cmd line as a first argument
    jira = connect_to_jira(api_token)
    logger.info("Successfully connected to JIRA")

    # here will be the final list
    notes_with_summary = []


    logger.info("Start extracting issues from JIRA...")
    for note in notes:
        try:
            issue = jira.issue(note[0])
            # print(issue.fields.summary)
            note.append(issue.fields.summary)
            notes_with_summary.append(note)

        except JIRAError as e:
            # print(e.status_code)
            # print(e.text)
            note.append('No summary for the issue: "' + note[0] + '" found')
            notes_with_summary.append(note)
            pass

    logger.info("Issues extracted successfully")
    logger.info("Printing rules...")
    time.sleep(7)


    
    # logger.info("List of unique rules:")
    for note in notes_with_summary:
        print(note[0] + ': ' + note[4])
        print(note[1])
        print(note[2])
        print(note[3])
        print("---------------------------------------------------------")


def connect_to_jira(args):
    # Connecting to JIRA
    jira = JIRA(
        basic_auth=("admin@domain.com", args.pass_to_jira),
        options={'server': 'https://jira.domain.net'}
    )
    return jira



def parse_json_file(filename):
    count = 1
    with open(filename, 'r') as file:
        data = json.load(file)

        print_countries(data, count)
        notes = extract_notes(data, count)

    return notes



# print all countries from file
def print_countries(data, count):
    # get them
    for item in data["result"]:
        if item["configuration"]["target"] == "country":
            countries.append(item["configuration"]["value"])

    # print them
    unique_countries = list(set(countries))
    print("\n---------------------------------------------------------")
    print("List of blocked countries:")
    print("---------------------------------------------------------")
    for c in unique_countries:
        print(c)
    
    print("---------------------------------------------------------")




# print all notes from file
def extract_notes(data, count):

    # list all notes to notes array
    for item in data["result"]:
        if (item["notes"]) != "":
            notes.append(item["notes"])
        else:
            id={}
            ip_list = []
            filter={}
            id["id"] = count
            id["paused"] = "false"
            id["action"] = item["mode"]

            ip_list.append("(ip.src eq {})".format(item["configuration"]["value"]))
            filter["expression"] = ip_list
            id["filter"] = filter
            undescribed.append(id)
            count += 1

    unique_notes = list(set(notes))

    print("\n\n---------------------------------------------------------")
    print("List of unique rules:")
    print("---------------------------------------------------------")
   
    result = []

    for unique_note in unique_notes:
        result_item = []
        result_item.append(unique_note)
        # print("\n--------------------------------------")
        # print(unique_note)

        ip_list = []
        id={}
        filter={}
        id["id"] = count


        # list all items again and compare to combine unique one
        for item in data["result"]:
            if item["notes"] == unique_note:
                ip_list.append("(ip.src eq {})".format(item["configuration"]["value"]))

        result_item.extend([item["mode"], item["paused"]])
        # print(item["mode"])
        # print(item["paused"])
        delimeter = " or "''
        res = delimeter.join(ip_list)

        id={}
        ip_list = []
        filter={}

        id["paused"] = item["paused"]
        id["action"] = item["mode"]


        # finally print it
        count += 1
        result_item.append(res)
        result.append(result_item)
        # print(res)
        # print("--------------------------------------\n")

    return(result)




def initiate_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    consolelog_handler = logging.StreamHandler()
    consolelog_formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(name)-25s  | %(message)s',
                                             datefmt='%m-%d-%Y | %H:%M:%S')
    consolelog_handler.setFormatter(consolelog_formatter)
    consolelog_handler.setLevel(logging.INFO)
    logger.addHandler(consolelog_handler)

    return logger






if __name__ == "__main__":
    main(sys.argv[1:])
    
    
