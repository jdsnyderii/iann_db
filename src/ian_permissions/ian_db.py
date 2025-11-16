"""IANdb - AWS IAM database manager."""
import json
import sqlite3
import requests


class IANdb:
    """AWS IAM database manager."""

    DEFAULT_URL = "https://raw.githubusercontent.com/iann0036/iam-dataset/main/aws/iam_definition.json"
    DEFAULT_DB = "data/aws_iam_advanced.db"

    @staticmethod
    def categorize_access_level(access_level):
        """Categorize IAM access_level into read/write/admin/other."""
        if access_level in ['Read', 'List']:
            return 'read'
        elif access_level in ['Write', 'Tagging']:
            return 'write'
        elif access_level == 'Permissions management':
            return 'admin'
        else:
            return 'other'

    @staticmethod
    def create(url: str = DEFAULT_URL, db_path: str = DEFAULT_DB):
        """Create or populate the SQLite DB from the IAM JSON definition.

        Args:
            url: URL to fetch the IAM definition JSON from.
            db_path: Path where the SQLite database will be created/updated.

        Raises:
            Exception: If fetching the JSON fails.
        """
        # Fetch the full IAM definition JSON from GitHub
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch JSON: {response.status_code}")

        data = response.json()  # Expected to be a list of service objects

        # Connect to SQLite database (creates file if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                prefix TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                condition TEXT NOT NULL,
                description TEXT,
                type TEXT,
                FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS privileges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                access_level TEXT NOT NULL,
                description TEXT,
                privilege TEXT NOT NULL,
                read_write TEXT,
                FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS privilege_resource_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                privilege_id INTEGER NOT NULL,
                condition_keys TEXT,
                dependent_actions TEXT,
                resource_type TEXT,
                FOREIGN KEY (privilege_id) REFERENCES privileges (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                arn TEXT NOT NULL,
                condition_keys TEXT,
                resource TEXT NOT NULL,
                FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE CASCADE
            )
        ''')

        # Clear existing data for a fresh load (optional; remove if you want to append)
        cursor.execute('DELETE FROM privilege_resource_types')
        cursor.execute('DELETE FROM privileges')
        cursor.execute('DELETE FROM resources')
        cursor.execute('DELETE FROM conditions')
        cursor.execute('DELETE FROM services')

        # Map service_name to ID for efficient lookups
        services_map = {}

        # Load data counters
        total_services = 0
        total_privileges = 0
        total_conditions = 0
        total_resources = 0
        total_priv_resource_types = 0

        for service_obj in data:
            service_name = service_obj.get('service_name', '')
            prefix = service_obj.get('prefix', '')

            # Insert service (or ignore if exists)
            cursor.execute(
                'INSERT OR IGNORE INTO services (service_name, prefix) VALUES (?, ?)',
                (service_name, prefix)
            )
            # Get the ID
            cursor.execute('SELECT id FROM services WHERE service_name = ?', (service_name,))
            row = cursor.fetchone()
            if row is None:
                continue  # Skip if insert failed unexpectedly
            service_id = row[0]
            services_map[service_name] = service_id
            total_services += 1

            # Insert conditions
            for cond in service_obj.get('conditions', []):
                cursor.execute(
                    'INSERT INTO conditions (service_id, condition, description, type) VALUES (?, ?, ?, ?)',
                    (service_id, cond.get('condition', ''), cond.get('description', ''), cond.get('type', ''))
                )
                total_conditions += 1

            # Insert resources
            for res in service_obj.get('resources', []):
                condition_keys_json = json.dumps(res.get('condition_keys', []))
                cursor.execute(
                    'INSERT INTO resources (service_id, arn, condition_keys, resource) VALUES (?, ?, ?, ?)',
                    (service_id, res.get('arn', ''), condition_keys_json, res.get('resource', ''))
                )
                total_resources += 1

            # Insert privileges and their resource_types
            for priv in service_obj.get('privileges', []):
                read_write = IANdb.categorize_access_level(priv.get('access_level', ''))
                cursor.execute(
                    'INSERT INTO privileges (service_id, access_level, description, privilege, read_write) VALUES (?, ?, ?, ?, ?)',
                    (
                        service_id,
                        priv.get('access_level', ''),
                        priv.get('description', ''),
                        priv['privilege'],  # Required field
                        read_write
                    )
                )
                priv_id = cursor.lastrowid
                total_privileges += 1

                # Insert resource_types for this privilege
                for rt in priv.get('resource_types', []):
                    condition_keys_json = json.dumps(rt.get('condition_keys', []))
                    dependent_actions_json = json.dumps(rt.get('dependent_actions', []))
                    cursor.execute(
                        'INSERT INTO privilege_resource_types (privilege_id, condition_keys, dependent_actions, resource_type) VALUES (?, ?, ?, ?)',
                        (priv_id, condition_keys_json, dependent_actions_json, rt.get('resource_type', ''))
                    )
                    total_priv_resource_types += 1

        conn.commit()
        conn.close()

        print(f"Successfully loaded data into {db_path}:")
        print(f"- {total_services} services")
        print(f"- {total_conditions} conditions")
        print(f"- {total_privileges} privileges (actions)")
        print(f"- {total_resources} resources")
        print(f"- {total_priv_resource_types} privilege-resource-type mappings")

