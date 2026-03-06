import xml.etree.ElementTree as ET

files = [
    "storage/reference/ES2002a.A.words.xml",
    "storage/reference/ES2002a.B.words.xml",
    "storage/reference/ES2002a.C.words.xml",
    "storage/reference/ES2002a.D.words.xml"
]

START_TIME = 77.44
END_TIME = 300

words = []

for file in files:

    print("Reading:", file)

    tree = ET.parse(file)
    root = tree.getroot()

    for elem in root.iter():

        tag = elem.tag.split("}")[-1]

        if tag == "w":

            start = elem.attrib.get("starttime")

            if start is None:
                continue

            start = float(start)

            if START_TIME <= start <= END_TIME:

                if elem.text:
                    words.append(elem.text.lower())

text = " ".join(words)

with open("storage/reference/reference_trimmed.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("\nReference transcript created")
print("Total words:", len(words))