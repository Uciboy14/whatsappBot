import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from chromedriver_py import binary_path  # import the binary_path
import vobject
import random
import argparse

class WhatsAppBot:
    def __init__(self, contacts_file):
        self.contacts_file = contacts_file
        self.driver = self._initialize_driver()
        self.contacts = self._load_contacts()
        self.session_file = 'whatsapp_session.pkl'
        self.added_contacts_file = 'added_contacts.pkl'
        self.added_contacts = self._load_added_contacts()

    def _initialize_driver(self):
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=./User_Data")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service(binary_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _load_contacts(self):
        contacts = {}
        try:
            with open(self.contacts_file, 'r') as file:
                vcard = vobject.readComponents(file)
                for card in vcard:
                    if hasattr(card, 'tel'):
                        phone = card.tel.value
                        name = card.fn.value if hasattr(card, 'fn') else card.n.value if hasattr(card, 'n') else None
                        contacts[phone] = str(name).strip()
        except Exception as e:
            print(f"Error reading contacts file: {e}")
        return contacts

    def _load_added_contacts(self):
        if os.path.exists(self.added_contacts_file):
            with open(self.added_contacts_file, 'rb') as file:
                return pickle.load(file)
        return []

    def _save_added_contact(self, contact):
        self.added_contacts.append(contact)
        with open(self.added_contacts_file, 'wb') as file:
            pickle.dump(self.added_contacts, file)

    def open_whatsapp(self):
        self.driver.get("https://web.whatsapp.com/")
        print("Please scan the QR code to log in to WhatsApp Web.")
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="Scan me!"]'))
            )
            time.sleep(40)  # Allow some time for the user to scan the QR code
        except TimeoutException:
            print("QR code not found or session expired.")
            return False
        return True

    def save_session(self):
        cookies = self.driver.get_cookies()
        with open(self.session_file, 'wb') as file:
            pickle.dump(cookies, file)
        print("Session saved.")

    def load_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, 'rb') as file:
                cookies = pickle.load(file)
                self.driver.get("https://web.whatsapp.com/")
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
                print("Session loaded.")
        else:
            print("No session file found.")
            self.open_whatsapp()
            self.save_session()

    def search_contact(self, contact_name):
        try:
            input_element = WebDriverWait(self.driver, 35).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            input_element.click()  # Click to focus the input field
            input_element.clear()  # Clear any existing text
            input_element.send_keys(contact_name)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]'))
            )
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Search input element not found or timed out for contact: {contact_name}. Exception: {e}")
            return False
        return True

    def click_search_result(self, contact_name):
        try:
            search_result = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]'))
            )
            search_result.click()
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Search result not found or timed out for contact: {contact_name}. Exception: {e}")
            return False
        return True

    def open_group_info(self):
        try:
            group_info_button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//header//div[@title="Profile details"]'))
            )
            group_info_button.click()
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Group info button not found or timed out. Exception: {e}")
            return False
        return True

    def add_members_to_group(self):
        try:
            add_member_button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="button"]//div[text()="Add member"]'))
            )
            add_member_button.click()

            search_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox" and @aria-label="Search input textbox" and @data-tab="3"]'))
            )
            
            time.sleep(2)
            
            member_count = 0
            for phone, name in self.contacts.items():
                if phone in self.added_contacts:
                    print(f"Skipping already added contact: {name} ({phone})")
                    continue

                search_input.click()
                ## Clear the input field by simulating CTRL+A (select all) and DELETE
                search_input.clear()
                
                search_input.send_keys(phone)

                member_result = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f'//div[@role="button"]//span[@title="{name}"]'))
                )
                member_result.click()
                print(f"Clicked on 'Add member' button in the popup for: {name} ({phone}).")
                time.sleep(2)  # Small delay to ensure the member is added before continuing

                self._save_added_contact(phone)
                member_count += 1
                print(f"Total members added: {member_count}")

                # Clear the search input for the next member
                search_input = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@role="textbox" and @aria-label="Search input textbox" and @data-tab="3"]'))
                )
                search_input.click()
                # Highlight and delete previous text
                search_input.send_keys(Keys.CONTROL + "a")
                search_input.send_keys(Keys.DELETE)

                if member_count >= 5:
                    break

            # Click the confirm button after reaching the maximum number of members
            if member_count >= 5:
                try:
                    confirm_button = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@aria-label="Confirm"]'))
                    )
                    confirm_button.click()
                    print("Clicked on 'Confirm' button after adding 5 members.")
                    
                    time.sleep(3)
                    
                    add_member_popup_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[contains(@data-animate-modal-popup, "true")]//button//div[text()="Add members"]'))
                    )
                    add_member_popup_button.click()
                    print(f"Clicked on 'Add member' button in the pSSpup for: {name} ({phone}).")
                    #time.sleep(random.uniform(1, 3))
                    time.sleep(5)
                except (NoSuchElementException, TimeoutException) as e:
                    print(f"Confirm button not found or timed out. Exception: {e}")
            else:
                print(f"Only {member_count} members were added. No need to click 'Confirm' button.")
        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            print(f"Failed to add member to group. Exception: {e}")
            return False
        return True

    def process_contacts(self, group_name):
        if self.search_contact(group_name):
            if self.click_search_result(group_name):
                if self.open_group_info():
                    for i in range(50):
                        self.add_members_to_group()

def main():
    parser = argparse.ArgumentParser(description='WhatsApp Bot for adding contacts to groups.')
    parser.add_argument('group_name', type=str, help='The name of the WhatsApp group.')
    parser.add_argument('contacts_file', type=str, help='The path to the contacts file (VCF format).')
    args = parser.parse_args()
    

    while True:
        try:
            bot = WhatsAppBot(args.contacts_file)
            bot.load_session()

            bot.process_contacts(args.group_name)

            # Break the loop if everything goes well
            break
        except WebDriverException as e:
            print(f"WebDriverException encountered: {e}")
            print("Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying

# Example usage
if __name__ == "__main__":
    main()
