#!/usr/bin/python3

import csv
import json
import requests

iq_url, iq_session, organizations, applications = "", "", [], []

def main():
    global iq_url, iq_session
    iq_url = "http://localhost:8070"
    iq_session = requests.Session()
    iq_session.auth = requests.auth.HTTPBasicAuth("admin", "admin123") 
    file_name = "sample_move.csv"

    set_orgs()
    set_apps()

    apps_to_move = get_load_file(file_name)
    for app in apps_to_move:
        found = find_app(app['publicId'])
        if found:
            org_to_move_to = check_org(app['organizationName'])
            if org_to_move_to != found["organizationId"]:
                print(f"Moving app '{app['publicId']}'' to organization '{app['organizationName']}'")
                resp = move_application(found["id"], org_to_move_to)
                print("-- Success" if resp else "## Failed")
    #----------------------------------------------------------------------
#--------------------------------------------------------------------------

def get_load_file(file_name):
    container, missing, required = [],[], ['organizationName', 'publicId']
    print("checking import file for required columns")

    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for r in required:
            if r not in reader.fieldnames:
                missing.append(r)
        if len(missing) > 0:
            print(f"Import File is missing fields {missing}.")
            exit(1)
        for row in reader:
            container.append(row)
    return container

#--------------------------------------------------------------------------

def set_apps():
    global applications
    url = f'{iq_url}/api/v2/applications'
    applications = iq_session.get(url).json()["applications"]

def set_orgs():
    global organizations
    url = f'{iq_url}/api/v2/organizations'
    organizations = iq_session.get(url).json()["organizations"]

def check_org(name):
    for c in organizations:
        if name in c['name']: 
            return c['id']
    return None

def find_app(publicId):
    for app in applications:
        if publicId == app["publicId"]:
            return app
    return None

def move_application(applicationInternalId, organizationId):
    url = f'{iq_url}/api/v2/applications/{applicationInternalId}/move/organization/{organizationId}'
    resp = iq_session.post(url).status_code == 200
    return resp

#--------------------------------------------------------------------
if __name__ == "__main__":
    main()