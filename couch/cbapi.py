import requests
import pprint
hosts = {'192.168.10.242': {'remote_hosts': {}, 'buckets': {}}, '192.168.10.220': {'remote_hosts': {}, 'buckets': {}}}


def get_info(host, method):
    http = requests.get('http://{host}:8091/{method}'.format(host=host, method=method),
                        auth=('Administrator', 'jhufybpfwbz300'))

    return http


for host in hosts.keys():
    answer1 = get_info(host, 'pools/default/remoteClusters').json()
    for remoteCluster in answer1:
        hosts[host]['remote_hosts'].update({remoteCluster['name']: {'remoteCluster_hostname': remoteCluster['hostname'],
                                                                    'remoteCluster_is_deleted': remoteCluster[
                                                                        'deleted'],
                                                                    'remoteCluster_uuid': remoteCluster['uuid']}})

    answer2 = get_info(host, 'pools/default/buckets').json()
    for buckets in answer2:
        if buckets['bucketType'] == 'membase':
            hosts[host]['buckets'].update({buckets['name']: buckets['uuid']})

print '~~~~~~~~~~~~~~~~~~~~~~~~~~'
replication = dict()
for host in hosts:
    for bucket_r in hosts[host]['buckets']:
        for remote_host in hosts[host]['remote_hosts']:
            print(hosts[host]['remote_hosts'][remote_host]['remoteCluster_uuid'], bucket_r)
            print(host, remote_host,
                  'http://' + host + ':8091' + '/settings/replications/' + hosts[host]['remote_hosts'][remote_host][
                      'remoteCluster_uuid'] + '%2F' + bucket_r + '%2F' + bucket_r)
            answer3 = get_info(host, 'settings/replications/' + hosts[host]['remote_hosts'][remote_host][
                'remoteCluster_uuid'] + '%2F' + bucket_r + '%2F' + bucket_r)

            print(answer3.content)
print '~~~~~~~~~~~~~~~~~~~~~~~~~~'


pprint.pprint(hosts)







