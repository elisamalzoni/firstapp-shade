from shade import *
from pprint import pprint

simple_logging(debug=True)
conn = openstack_cloud(cloud='myfavoriteopenstack')

images = conn.list_images()
#for image in images:
#    pprint(image)

flavors =  conn.list_flavors()
#for flavor in flavors:
#    pprint(flavor)

image_id = 'bbc3648d-3d2c-4419-ba34-501db889bd66'
image = conn.get_image(image_id)
#pprint(image)

flavor_id = '554f5454-02c0-4825-a034-8c679189f90c'
flavor = conn.get_flavor(flavor_id)
pprint(flavor)

#instance_name = 'testing'
#testing_instance = conn.create_server(wait=True, auto_ip=True,
#    name=instance_name,
#    image=image_id,
#    flavor=flavor_id,
#    network='983f53ac-5082-46cd-be06-ae0353b02cfc')
#pprint(testing_instance)

instances = conn.list_servers()
#for instance in instances:
#    pprint(instance)

print('Checking for existing SSH keypair...')
keypair_name = 'demokey'
pub_key_file = '/home/cloud/.ssh/id_rsa.pub'

if conn.search_keypairs(keypair_name):
    print('Keypair already exists. Skipping import.')
else:
    print('Adding keypair...')
    conn.create_keypair(keypair_name, open(pub_key_file, 'r').read().strip())

for keypair in conn.list_keypairs():
    pprint(keypair)

print('Checking for existing security groups...')
sec_group_name = 'all-in-one'
if conn.search_security_groups(sec_group_name):
    print('Security group already exists. Skipping creation.')
else:
    print('Creating security group.')
    conn.create_security_group(sec_group_name, 'network access for all-in-one application.')
    conn.create_security_group_rule(sec_group_name, 80, 80, 'TCP')
    conn.create_security_group_rule(sec_group_name, 22, 22, 'TCP')

conn.search_security_groups(sec_group_name)

ex_userdata = '''#!/usr/bin/env bash

curl -L -s https://git.openstack.org/cgit/openstack/faafo/plain/contrib/install.sh | bash -s -- \
-i faafo -i messaging -r api -r worker -r demo
'''

instance_name = 'all-in-one'
testing_instance = conn.create_server(wait=True, auto_ip=False,
    name=instance_name,
    image=image_id,
    flavor=flavor_id,
    key_name=keypair_name,
    security_groups=[sec_group_name],
    network='983f53ac-5082-46cd-be06-ae0353b02cfc', 
    userdata=ex_userdata)

f_ip = conn.available_floating_ip()

pprint(f_ip)
print('The Fractals app will be deployed to http://%s' % f_ip['floating_ip_address'] )
