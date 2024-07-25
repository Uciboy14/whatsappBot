# WhatsApp Bot
A Python-based bot to automate the process of adding contacts to WhatsApp groups using Selenium.

## Features

- Loads contacts from a VCF file
- Opens Whatsapp Web and logs in.
- Searches for a specific Whatsapp group.
- Adds contacts to the group.

## Requirements

- Python 3.6+
- Google Chrome
- ChromeDriver
- Virtualenv (optional but recommended)

## Installation

1. **Clone the repository**

```sh
git clone https://github.com/uciboy14/whatsappBot.git
cd whatssappBot
```

2. **Run the bot:**

    ```sh
    python bot.py "Group Name" "path/to/contacts.vcf"
    ```

    Replace `"Group Name"` with the name of your WhatsApp group and `"path/to/contacts.vcf"` with the path to your VCF file.

3. **Follow the instructions:**

    - The bot will open WhatsApp Web in a Chrome browser window.
    - Scan the QR code to log in.
    - The bot will automatically start adding contacts to the specified group.

## Important Notes

- Ensure you have Google Chrome installed.
- The bot uses ChromeDriver to automate Chrome. Make sure ChromeDriver is compatible with your Chrome version.
- The bot can add a maximum of 5 members per session to avoid detection and potential bans from WhatsApp.

## Troubleshooting

- **Session not loading:**
    - Make sure you have scanned the QR code properly.
    - Ensure the session file `whatsapp_session.pkl` exists and is not corrupted.

- **WebDriverException:**
    - If the bot encounters a WebDriverException, it will retry after 10 seconds. Ensure your ChromeDriver is correctly set up.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

