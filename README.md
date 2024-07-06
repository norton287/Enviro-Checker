```markdown
# EnviroCheck

EnviroCheck is a Python script that monitors a MariaDB database for the latest timestamp in the `readings` table. If the latest timestamp is more than 30 minutes old, the script sends an alert email. Additionally, the script includes log rotation to manage log files efficiently.  This is designed for the Pimoroni Enviro Indoor+ Weather Station.  It is inherently flawed and will just hang from time to time and without a reliable way to monitor it, this is the best solution I've found with my backend that I wrote for it to ensure it stays up and running and updating my database.  If you are interested in the backend server portion that the Enviro dumps to I can upload it here for you to pull as well.  It is written in PHP and uses MariaDB as the DB for the storage of the readings from the Enviro Indoor+.

## Features

- Connects to a MariaDB database and checks the latest timestamp in the `readings` table.
- Sends an email alert if the latest timestamp is more than 30 minutes old.
- Rotates log files older than 2 days and compresses them.
- Removes compressed log files older than 7 days.

## Prerequisites

- Python 3.x
- MariaDB server

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/envirocheck.git
    cd envirocheck
    ```

2. **Create a virtual environment** (optional but recommended):

    ```sh
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. **Install required Python packages**:

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

The script requires an INI file for database and email configuration. The path to this INI file should be set in the `ENVIRO_INI_LOC` environment variable.

### Example INI File

Create a file named `config.ini` with the following content:

```ini
[database]
user = your_db_user
password = your_db_password
host = your_db_host
database = your_db_name

[email]
smtp_server = your_smtp_server
smtp_port = your_smtp_port
smtp_user = your_smtp_user
smtp_password = your_smtp_password
email_from = your_email_from
email_to = your_email_to
```

### Setting the Environment Variable

On Linux or macOS, you can set the environment variable in your shell profile (`~/.bashrc`, `~/.bash_profile`, `~/.zshrc`, etc.):

```sh
export ENVIRO_INI_LOC=/path/to/your/config.ini
```

On Windows, you can set it in the system environment variables.

### Log File

The script writes logs to `/var/log/envirocheck.log`. Ensure that the script has the necessary permissions to write to this directory.

## Usage

Run the script using Python:

```sh
python enviro_check.py
```

The script will:

1. Rotate the log file if it is older than 2 days.
2. Remove gzipped log files older than 7 days.
3. Connect to the MariaDB database and check the latest timestamp in the `readings` table.
4. Send an email alert if the latest timestamp is more than 30 minutes old.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Contributions are welcome! Please open an issue or submit a pull request.

## Troubleshooting

If you encounter any issues, check the log file at `/var/log/envirocheck.log` for detailed error messages. Ensure that the database credentials and email settings in the INI file are correct.

---

### Contact

For any inquiries or support, please contact here@spindlecrank.com.
```
