# Install Prerequisites

- sudo apt-get install libffi-dev
- sudo apt-get install libxml2-dev libxslt1-dev
# Clone the Tempest Git Repository
The Tempest source MUST be inside the Jumpgate source directory.
Change directory into the Jumpgate source directory, then do 
- sudo git clone https://github.com/openstack/tempest

# Install Tempest Requirements
Change directory into the Tempest source directory, then do
- sudo pip install -r requirements.txt

# Configure Tempest
Change directory into the Jumpgate source directory.
- sudo cp etc/tempest.conf.sample etc/tempest.conf
Now edit etc/tempest.conf

## URL for OpenStack Identity API endpoint
These do not need to be changed unless you configured Jumpgate ( /etc/jumpgate/jumpgate.conf ) to respond to a different IP address or port

uri = http://127.0.0.1:5000/v2.0/

uri_v3 = http://127.0.0.1:5000/v3/

## Identity Users
The user information will be the same as used from the testing nova section from Installing Jumpgate.
 
Same value as OS_USERNAME, your SoftLayer username

username = 

Same value as OS_PASSWORD, your SoftLayer API key

password = 

Same value as OS_TENANT_ID, your SoftLayer account id

tenant_name =

 
The Admin user will have the same values as the user above.
 
admin_username = 

admin_password = 

admin\_tenant\_name =

## Image Refs
The image refs need values.  These values are UUIDs of public images in SoftLayer.  You can use the values below or choose your own by using the SoftLayer CLI, 'sl image list --public'.

image_ref = 54f4ed9f-f7e6-4fe6-8b54-3a7faacd82b3

image\_ref\_alt = c27eb0ad-bddd-44c7-a37a-e3ddbbfed277

## Networking
Some things have changed in the tempest.conf.sample from the Tempest project.  In order for networking to work properly, change these values to EMPTY.
 
public\_network\_id = {$PUBLIC_NETWORK_ID}

public\_router\_id = {$PUBLIC_ROUTER_ID}
 
Like so
 
public\_network\_id =

public\_router\_id =

DO NOT CHANGE ANY OTHER VALUES



From the Jumpgate source directory, execute the following
python run\_tempest\_tests.py
You will see output in the terminal.  Also a tempest.log file will be created in the tempest directory.
If everything worked properly, you should see some new instances created in your SoftLayer account.

# Known Issues
Tempest is still not working correctly as it should clean up its mess ( delete the test instances ) when it is done.

