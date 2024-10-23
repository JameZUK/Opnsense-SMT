# Social Media Timeout (SMT) Plugin for OPNsense

## Overview

The **Social Media Timeout (SMT)** plugin for OPNsense is designed to automatically block access to social media platforms after a predefined usage period. It leverages Unbound DNS logs to monitor access and applies DNS-based blocking using Response Policy Zones (RPZ).## Features- **Monitor Social Media Access:** Parses Unbound DNS logs to detect access to predefined social media domains.- **Usage Tracking:** Tracks the amount of time each user spends on social media.- **Automatic Blocking:** Blocks access to social media domains via DNS after exceeding the usage threshold.
- **Configurable Thresholds:** Allows customization of usage thresholds and block durations.
- **Web Interface:** Provides a user-friendly web interface for configuration.
- **Logging:** Detailed logging for monitoring and debugging purposes.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/smt_plugin.git
    ```

2. **Navigate to the Plugin Directory:**

    ```bash
    cd smt_plugin
    ```

3. **Build the Plugin Package:**

    ```bash
    make package
    ```

4. **Install the Plugin:**

    ```bash
    pkg install smt-0.1.txz
    ```

5. **Access the Web Interface:**

    - Navigate to `https://your-opnsense-ip/smts/config` to configure the plugin.

## Configuration

Use the web interface to set the following parameters:

- **Unbound Reload Command:** Command to reload Unbound DNS, e.g., `sudo service unbound reload`.
- **Blocklist Repository URL:** URL of the blocklist repository, e.g., `https://github.com/gieljnssns/Social-media-Blocklists`.
- **Local Blocklist Path:** Path to store the local blocklist file, e.g., `/usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/social_media_domains.txt`.
- **Usage Threshold (Hours):** Number of hours a user can access social media before being blocked.
- **Block Duration (Minutes):** Duration for which social media access is blocked.
- **Unbound Log File Path:** Path to Unbound DNS log file, e.g., `/var/log/unbound.log`.
- **RPZ File Path:** Path to the RPZ file, e.g., `/usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/social_media.rpz`.
- **Logging Level:** Select from `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- **Logging File Path:** Path to store the plugin's log file, e.g., `/usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/smt_plugin.log`.
- **Enable SMT Service:** Toggle to enable or disable the SMT service.

## Usage

Once configured and the service is enabled, the SMT plugin will start monitoring Unbound DNS logs. When a user exceeds the defined usage threshold for social media, their access will be blocked for the specified duration.

## Development

### Directory Structure

smt_plugin/ ├── Makefile ├── README.md ├── src/ │   ├── GUI/ │   │   ├── controllers/ │   │   │   └── OPNSense/ │   │   │       └── SMT/ │   │   │           └── ConfigController.php │   │   ├── models/ │   │   │   └── OPNSense/ │   │   │       └── SMT/ │   │   │           └── Config.php │   │   └── templates/ │   │       └── OPNSense/ │   │           └── SMT/ │   │               └── Config/ │   │                   └── config.ui.php │   └── Resources/ │       └── javascript/ │           └── smt.js ├── etc/ │   └── opnsense/ │       └── scripts/ │           └── smt/ │               ├── smt_plugin.py │               ├── requirements.txt │               └── config.yaml ├── etc/rc.d/ │   └── smt └── share/ └── examples/ └── smt/ ├── social_media_domains.txt └── config.yaml

### Dependencies

Ensure that the following Python packages are installed:

- `requests`
- `PyYAML`
- `watchdog`

These are specified in the `requirements.txt` file and are automatically installed during the plugin installation process.

### Logging

Logs are stored at the path specified in the configuration (e.g., `/usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/smt_plugin.log`). Use these logs to monitor the plugin's activity and debug issues.

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or support, please contact [your-email@example.com](mailto:your-email@example.com).


---

Instructions to Use:

1. Copy the Above Markdown:

Select all the text within the code block above and copy it.


2. Create a README.md File on GitHub:

Navigate to your GitHub repository where you want to add the README.md.

If a README.md does not already exist, GitHub typically prompts you to add one. Click on "Add a README".

If it exists, you can edit it by clicking the pencil icon.



3. Paste the Markdown Content:

Paste the copied markdown content into the README.md editor.


4. Customize Placeholders:

Replace yourusername with your actual GitHub username.

Update your-email@example.com with your contact email address.

Adjust any file paths or configuration details as necessary to match your deployment environment.



5. Commit the Changes:

After pasting and customizing the content, commit the changes to your repository.


6. Verify on GitHub:

Navigate to your repository on GitHub to ensure that the README.md is displayed correctly with all formatting intact.
