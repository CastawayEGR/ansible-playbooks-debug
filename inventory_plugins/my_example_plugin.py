# plugins/inventory/my_example_plugin.py

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleParserError # Import for explicit parsing errors
import os

DOCUMENTATION = r'''
    name: my_example_plugin
    plugin_type: inventory
    short_description: Returns 5 example hosts with ansible_host set to localhost
    description:
        - This is a simple example inventory plugin that generates 5 hosts.
        - Each host will have the 'ansible_host' variable set to 'localhost'.
    options:
        plugin:
            description: The name of the plugin to use.
            required: True
            choices: ['my_example_plugin']
'''

class InventoryModule(BaseInventoryPlugin):

    NAME = 'my_example_plugin'

    def verify_file(self, path):
        """
        Verify that the inventory file is valid for this plugin.
        This plugin will handle files ending with .yml or .yaml.
        """
        # The BaseInventoryPlugin's verify_file expects 'path'
        # This checks if the file exists and is readable.
        if not super(InventoryModule, self).verify_file(path):
            return False

        # Only process files that end with .yml or .yaml
        # This makes the verification less prone to issues with initial YAML loading
        if path.endswith(('.yml', '.yaml')):
            return True
        return False

    def parse(self, inventory, loader, path, cache=True):
        """
        Parse the inventory data from the plugin's configuration.
        """
        # Call the super method to initialize basic inventory properties
        super(InventoryModule, self).parse(inventory, loader, path)

        # Load the YAML data from the inventory file path
        # 'path' here is the path to the inventory file (e.g., inventory.yml)
        try:
            yaml_data = loader.load_from_file(path)
        except Exception as e:
            # Raise a specific error if the YAML file cannot be loaded
            raise AnsibleParserError(f"Error loading YAML from '{path}': {e}")

        # Ensure the loaded data is a dictionary and specifies this plugin
        if not isinstance(yaml_data, dict):
            raise AnsibleParserError(
                f"Inventory file '{path}' is not a valid YAML dictionary. "
                "It should contain 'plugin: my_example_plugin'."
            )
        if 'plugin' not in yaml_data:
            raise AnsibleParserError(
                f"Inventory file '{path}' is missing the 'plugin' key. "
                "It must specify 'plugin: my_example_plugin'."
            )
        if yaml_data['plugin'] != self.NAME:
            raise AnsibleParserError(
                f"Inventory file '{path}' specifies plugin '{yaml_data['plugin']}', "
                f"but this plugin is '{self.NAME}'. Mismatch found."
            )

        # Create a group for our example hosts
        example_group = self.inventory.add_group('example_hosts')

        # Add 5 example hosts
        for i in range(1, 6):
            hostname = f'example_host_{i}'
            self.inventory.add_host(hostname, group=example_group)
            # Set the ansible_host variable for each host to localhost
            self.inventory.set_variable(hostname, 'ansible_host', 'localhost')

