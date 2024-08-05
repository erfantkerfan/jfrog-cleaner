import argparse
import re
import requests
import types
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

def debug_print(printable):
    if args.verbose:
        print(printable)

# return the tag name if it did not match in any of filters
def match_any_pattern(patterns, text):
    for pattern in patterns:
        if re.search(pattern, text):
            return None
    return text

def save_safe_tags(deletion_candidate):
    grouped_by_repo_and_path = {}
    for item in deletion_candidate:
        key = f"{item['repo']}-{item['path']}"
        if key not in grouped_by_repo_and_path:
            grouped_by_repo_and_path[key] = []
        grouped_by_repo_and_path[key].append(item)

    regex_pattern = re.compile(configfile.SAFE_TAG, re.IGNORECASE)
    elements_to_remove = []
    for group_key, items in grouped_by_repo_and_path.items():
        matching_items = [item for item in items if regex_pattern.search(item['name'])]
        if matching_items:
            # Keep only the latest matching item
            matching_items_to_remove = matching_items[:-1]
            artifact_url = configfile.BASE_URL + matching_items[-1]['repo'] + '/' + matching_items[-1]['path'] + '/' + matching_items[-1]['name']
            print(f'{Fore.MAGENTA}{artifact_url} -> will be kept with SAVED tag!{Style.RESET_ALL}')
            elements_to_remove.extend(matching_items_to_remove)

    # Remove ans return elements from the original list
    return [item for item in deletion_candidate if item not in elements_to_remove]

def filter_results(results, path):
    deletion_candidate = []
    for result in results:
        artifact_url = configfile.BASE_URL + result['repo'] + '/' + result['path'] + '/' + result['name']
        if match_any_pattern(path['keep_filters'], result['name']) is not None:
            print(f'{Fore.RED}{artifact_url} -> will be deleted{Style.RESET_ALL}')
            deletion_candidate.append(result)
        else:
            debug_print(f'{Fore.GREEN}{artifact_url} -> will be kept{Style.RESET_ALL}')
    deletion_list = save_safe_tags(deletion_candidate)

    return(deletion_list)

def remove_asset_from_art(subject):
    artifact_url = configfile.BASE_URL + subject['repo'] + '/' + subject['path'] + '/' + subject['name']
    if not args.dry:
        requests.delete(artifact_url, auth=(configfile.USER, configfile.PASSWORD))

def cleanup_repo(path):
    query = 'items.find({"repo":"' + path['repo'] + '","path":"'+ path['path'] + '","created":{"$before":"' + path['keep_time'] + '"}},{"path":{"$ne":"."}},{"type":"folder"}).include("repo","name","path","created")'
    myResp = requests.post(configfile.BASE_URL + 'api/search/aql', auth=(configfile.USER, configfile.PASSWORD), headers=configfile.HEADERS, data=query)
    results = filter_results(eval(myResp.text)["results"], path)

    for result in results:
        remove_asset_from_art(result)

def prune_unreferenced_data():
    myResp = requests.post(configfile.BASE_URL + 'api/system/storage/prune/start', auth=(configfile.USER, configfile.PASSWORD), headers=configfile.HEADERS)

def run_gc():
    myResp = requests.post(configfile.BASE_URL + 'api/system/storage/gc', auth=(configfile.USER, configfile.PASSWORD), headers=configfile.HEADERS)

if __name__ == '__main__':
    # parsing input arguments
    parser = argparse.ArgumentParser(description='Cleaning up artifacts from jfrog artifactory in a granular manner.')
    parser.add_argument('-C', '--config', help="config file to use in this directory, defaults to config.py", default='config', type=str)
    parser.add_argument('-D', '--dry', help="run in dry-run mode", default=False, action="store_true")
    parser.add_argument('-S', '--safe', help="run in safe-mode (keeps at least one of the safe tagged images)", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', help="run in verbose mode", default=False, action="store_true")
    args = parser.parse_args()

    colorama_init()

    # import config file
    configfile = types.ModuleType(args.config[:-3] if args.config.endswith('.py') else args.config)
    with open(args.config + '.py' if not args.config.endswith('.py') else args.config, 'r') as file:
        exec(file.read(), configfile.__dict__)

    # this where the job gets done
    for path in configfile.PATHS:
        debug_print(f'{Fore.BLUE}{path} -> is being searched{Style.RESET_ALL}')
        cleanup_repo(path)
    if not args.dry:
        debug_print(f'{Fore.BLUE}pruning unreferenced data{Style.RESET_ALL}')
        prune_unreferenced_data()

        debug_print(f'{Fore.BLUE}pruning unreferenced data{Style.RESET_ALL}')
        run_gc()
