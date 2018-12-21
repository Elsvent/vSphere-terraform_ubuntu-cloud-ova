from __future__ import print_function
from json import loads as jsloads
from yaml import load as yamlload
from yaml import dump as yamldump
from os import path

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def read_yaml(filename):
    with open(filename, 'r') as yamlfile:
        return yamlload(yamlfile)

def read_terraform_json(filename):
    with open(filename, 'r') as jsonfile:
        data=jsonfile.read().replace('\n', '')
        # hack jsonload without unicode
        return _byteify(
                jsloads(data, object_hook=_byteify),
                ignore_dicts=False
        )

def get_hosts(data):
    host_list = []
    for host in data:
        host_list += host.keys()
    return host_list

def get_ips(data):
    ip_list = []
    for ip in data:
        ip_list += ip.values()
    return ip_list

def insert_hosts(host_ip_dict, yaml_data):
    for host, ip in host_ip_dict.iteritems():
        temp_dict = {}
        temp_dict = {'ip': ip, 'name': host}
        yaml_data[0]['vars']['bind_zone_domains'][0]['hosts'].append(temp_dict)
    return yaml_data

def remove_dummy_host(yaml_data):
    del yaml_data[0]['vars']['bind_zone_domains'][0]['hosts'][0]
    return yaml_data

def write_back_yaml(data, filename):
    with open(filename, 'w') as output_yaml:
        yamldump(data, output_yaml)
def get_terraform_json():
    result = []
    for i in range(1, 10):
        if path.isfile("ns{0}.json".format(i)):
            result.append("ns{0}.json".format(i))
    return result

def main(terraform_json_list):

    master_yaml_file = "master.yml"
    master_template_yaml_file = "master_tpl.yml"

    for filename in terraform_json_list:
        json_data = read_terraform_json(filename)
        hosts = get_hosts(json_data)
        ips = get_ips(json_data)

        host_ip_dict = dict(zip(hosts, ips))

        if path.isfile(master_yaml_file):
            yaml_data = read_yaml(master_yaml_file)
        else:
            yaml_data = read_yaml(master_template_yaml_file)
        updated_yaml_data = insert_hosts(host_ip_dict, yaml_data)

        write_back_yaml(updated_yaml_data, master_yaml_file)

    yaml_data = read_yaml(master_yaml_file)
    write_back_yaml(remove_dummy_host(yaml_data), master_yaml_file)

if __name__ == '__main__':
    terraform_json_list = get_terraform_json()
    main(terraform_json_list)
