import gammu
import os

def get_modem_info():
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()
    info = sm.GetManufacturer() + "\n" + sm.GetModel()[0] + "\n" + sm.GetFirmware()[0] + "\n" + sm.GetIMEI()
    return info

def extract_sms():
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()
    sms_list = []
    for folder in [0, 10]:  # 0: Inbox, 10: Outbox
        status = sm.GetSMSStatus()
        remain = status['SIMUsed'] + status['PhoneUsed']
        start = True
        while remain > 0:
            if start:
                sms = sm.GetNextSMS(Folder=folder, Start=True)
                start = False
            else:
                sms = sm.GetNextSMS(Folder=folder, Start=False)
            sms_list.extend(sms)
            remain -= len(sms)
    return sms_list

def get_all_contacts():
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()
    contacts = []
    start = True
    while True:
        try:
            entry = sm.GetNextPhonebookEntry(Start=start)
            contacts.append({
                'Name': entry.get('Name', ''),
                'Number': entry.get('Number', ''),
                'Location': entry.get('Location', '')
            })
            start = False
        except gammu.ERR_EMPTY:
            break
        except gammu.GSMError:
            break
    return contacts

def send_sms(number, text):
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()
    message = {
        'Text': text,
        'SMSC': {'Location': 1},
        'Number': number,
        'Class': -1,
        'Unicode': False,
        'Entries': [{'ID': 'ConcatenatedTextLong', 'Buffer': text}]
    }
    sm.SendSMS(message)

def menu():
    while True:
        print("\nOffice of Information Controll Group Division")
        print("  - 1 for get all sms(s)")
        print("  - 2 for get all contacts")
        print("  - 3 for send sms to a single number")
        print("  - 0 to exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            print("\nAll SMS Messages:")
            try:
                for sms in extract_sms():
                    print(f"Number: {sms.get('Number', '')}")
                    print(f"Text: {sms.get('Text', '')}")
                    print(f"Date: {sms.get('DateTime', '')}")
                    print("-" * 40)
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "2":
            print("\nAll Contacts:")
            try:
                for contact in get_all_contacts():
                    print(f"Name: {contact['Name']}, Number: {contact['Number']}, Location: {contact['Location']}")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "3":
            number = input("Enter recipient number: ").strip()
            text = input("Enter SMS text: ").strip()
            try:
                send_sms(number, text)
                print("SMS sent successfully.")
            except Exception as e:
                print(f"Error sending SMS: {e}")
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    try:
        print("Modem Information:")
        print(get_modem_info())
        print("\nSMS Messages:")
        for sms in extract_sms():
            print(f"Number: {sms['Number']}")
            print(f"Text: {sms['Text']}")
            print(f"Date: {sms['DateTime']}")
            print("-" * 40)
        print("\nContacts:")
        for contact in get_all_contacts():
            print(f"Name: {contact['Name']}, Number: {contact['Number']}, Location: {contact['Location']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    menu()