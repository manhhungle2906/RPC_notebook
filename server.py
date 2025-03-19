from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import xml.etree.ElementTree as ET
import datetime
import requests
import os

XML_FILE = "notes.xml"

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """Threaded XML-RPC Server to handle multiple client requests concurrently."""
    pass

class NotebookServer:
    def __init__(self):
        self._initialize_xml()

    def _initialize_xml(self):
        if not os.path.exists(XML_FILE):
            root = ET.Element("notebook")
            tree = ET.ElementTree(root)
            tree.write(XML_FILE)

    def _load_xml(self):
        tree = ET.parse(XML_FILE)
        return tree, tree.getroot()

    def _save_xml(self, tree):
        import xml.dom.minidom
        xml_str = ET.tostring(tree.getroot(), encoding="utf-8")
        parsed_xml = xml.dom.minidom.parseString(xml_str)
        
        with open(XML_FILE, "w", encoding="utf-8") as f:
            f.write(parsed_xml.toprettyxml(indent="  "))

    def add_note(self, topic, text):
        tree, root = self._load_xml()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        topic_element = None
        for elem in root.findall("topic"):
            if elem.get("name") == topic:
                topic_element = elem
                break
        if topic_element is None:
            topic_element = ET.SubElement(root, "topic", name=topic)
 
        note = ET.SubElement(topic_element, "note")
        ET.SubElement(note, "timestamp").text = timestamp
        ET.SubElement(note, "text").text = text
        #save in the xml file 
        self._save_xml(tree)
        return f"Note added under topic: {topic}"

    def get_notes(self, topic):
        _, root = self._load_xml()
        for elem in root.findall("topic"):
            if elem.get("name") == topic:
                notes = []
                for note in elem.findall("note"):
                    timestamp = note.find("timestamp").text
                    text = note.find("text").text
                    notes.append(f"[{timestamp}] {text}")
                return notes if notes else ["No notes found."]
        return ["Topic not found."]

    def fetch_wikipedia_info(self, topic):
        wiki_url = f"https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": topic,
            "limit": 1,
            "format": "json"
        }

        response = requests.get(wiki_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and data[1]:  
                article_title = data[1][0]
                article_url = data[3][0]
                wiki_info = f"Wikipedia: {article_title} - {article_url}"

                tree, root = self._load_xml()

                topic_element = None
                for elem in root.findall("topic"):
                    if elem.get("name") == topic:
                        topic_element = elem
                        break

                if topic_element is None:
                    topic_element = ET.SubElement(root, "topic", name=topic)

                note = ET.SubElement(topic_element, "note")
                ET.SubElement(note, "timestamp").text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ET.SubElement(note, "text").text = wiki_info

                self._save_xml(tree)
                return f"Wikipedia info saved: {wiki_info}"

        return "No Wikipedia article are found."


server = ThreadedXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
server.register_instance(NotebookServer())

print("Threaded RPC Server running on port 8000...")
server.serve_forever()
