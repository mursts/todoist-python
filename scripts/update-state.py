#!/usr/bin/env python

import sys
import os
import json

import requests


def update(state, data):
    if 'day_orders' in data:
        state['day_orders'].update(data['day_orders'])
    if 'day_orders_timestamp' in data:
        state['day_orders_timestamp'] = data['day_orders_timestamp']
    if 'full_sync' in data:
        state['full_sync'] = data['full_sync']
    if 'live_notifications_last_read_id' in data:
        state['live_notifications_last_read_id'] = data['live_notifications_last_read_id']
    if 'locations' in data:
        state['locations'].append(data['locations'])
    if 'settings_notifications' in data:
        state['settings_notifications'].update(data['settings_notifications'])
    if 'sync_token' in data:
        state['sync_token'] = data['sync_token']
    if 'user' in data:
        state['user'].update(data['user'])

    for datatype in ['collaborators', 'collaborator_states', 'filters',
                     'items', 'labels', 'live_notifications', 'notes',
                     'project_notes', 'projects', 'reminders']:
        if datatype not in data:
            continue
        for newobj in data[datatype]:
            localobj = find(state, datatype, newobj)
            if localobj is not None:
                is_deleted = newobj.get('is_deleted', 0)
                if is_deleted == 0 or is_deleted is False:
                    localobj.update(newobj)
                else:
                    state[datatype].remove(localobj)
            else:
                is_deleted = newobj.get('is_deleted', 0)
                if is_deleted == 0 or is_deleted is False:
                    state[datatype].append(newobj)
    return state


def find(state, objtype, newobj):
    if objtype == 'collaborator_states':
        for obj in state[objtype]:
            if obj['project_id'] == newobj['project_id'] and obj['user_id'] == newobj['user_id']:
                return obj
    else:
        for obj in state[objtype]:
            if obj['id'] == newobj['id']:
                return obj
    return None


def main():
    session = requests.Session()

    if len(sys.argv) < 2:
        print('usage: update-state.py token')
        return

    token = sys.argv[1]

    cache = os.path.expanduser('~') + '/.todoist-sync/'
    try:
        os.makedirs(cache)
    except OSError:
        if not os.path.isdir(cache):
            raise

    try:
        with open(cache + token + '.json') as f:
            state = f.read()
        state = json.loads(state)
    except:
        state = {}

    try:
        with open(cache + token + '.sync') as f:
            sync_token = f.read()
    except:
        sync_token = '*'

    post = {
        'token': token,
        'sync_token': sync_token,
        'day_orders_timestamp': state.get('day_orders_timestamp', 0),
        'include_notification_settings': 1,
        'resource_types': json.dumps(['all']),
    }

    response = session.post('https://todoist.com/api/v7/sync', post)
    try:
        data = response.json()
        jsondata = json.dumps(data, indent=2, sort_keys=True)
        print(jsondata)
    except ValueError:
        return

    if state:
        result = json.dumps(update(state, data), indent=2, sort_keys=True)
    else:
        result = jsondata

    with open(cache + token + '.json', 'w') as f:
        f.write(result)
    with open(cache + token + '.sync', 'w') as f:
        f.write(data['sync_token'])


if __name__ == '__main__':
    main()
