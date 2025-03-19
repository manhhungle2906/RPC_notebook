import xmlrpc.client

server = xmlrpc.client.ServerProxy("http://localhost:8000")

def main():
    while True:
        print("\nNotebook RPC Client")
        print("1. Add a note")
        print("2. Find notes by topic")
        print("3. Fetch Wikipedia info")
        print("4. Exit")
        
        choice = input("Select an option: ")

        if choice == "1":
            topic = input("Client Enter an Topic ").strip()
            text = input("Client enter a note to the topic ").strip()
            response = server.add_note(topic, text)
            print(f"Server: {response}")

        elif choice == "2":
            topic = input("Enter the topic you want to search ").strip()
            notes = server.get_notes(topic)
            print("\n".join(notes))

        elif choice == "3":
            topic = input("Enter search term for Wikipedia: ").strip()
            response = server.fetch_wikipedia_info(topic)
            print(f"Server: {response}")

        elif choice == "4":
            print("Exiting client...")
            break

        else:
            print("Invalid option. Please choose again.")

if __name__ == "__main__":
    main()
