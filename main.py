import argparse
import re
import requests
import types
from colorama import init as OriginalColorama_init
from colorama import Fore as OriginalFore
from colorama import Style as OriginalStyle


class DummyColorama:
    BLACK=RED=GREEN=YELLOW=BLUE=MAGENTA=CYAN=WHITE=RESET_ALL=Style=colorama_init=''

    def colorama_init():
        pass

def debug_print(printable):
    if args.verbose:
        print(printable)

# return the tag name if it did not match in any of filters
def match_any_pattern(patterns, text):
    for pattern in patterns:
        if re.search(pattern, text):
            return None
    return text
    
def filter_results(results, path):
    x = []
    for result in results:
        artifact_url = configfile.BASE_URL + result['repo'] + '/' + result['path'] + '/' + result['name']
        if match_any_pattern(path['keep_filters'], result['name']) is not None:
            print(f'{Fore.RED}{artifact_url} -> will be deleted{Style.RESET_ALL}')
            x.append(result)
        else:
            debug_print(f'{Fore.GREEN}{artifact_url} -> will be kept{Style.RESET_ALL}')
    return(x)

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
    parser.add_argument('-P', '--plain', help="run in plain mode (print no color, suited for file output)", default=False, action="store_true")
    parser.add_argument('-v', '--verbose', help="run in verbose mode", default=False, action="store_true")
    args = parser.parse_args()

    if args.plain:
        Fore = Style = DummyColorama
        colorama_init = DummyColorama.colorama_init
    else:
        Fore = OriginalFore
        Style = OriginalStyle
        colorama_init = OriginalColorama_init
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
