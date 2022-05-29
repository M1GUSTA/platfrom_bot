import re

string = "само сообщение\n\n\n" \
         "заголовок\n" \
         ".\n\n" \
         "тdds\n" \
         "ddf"

title = re.search(r"\n{3}(.+)\n{2}", string, re.DOTALL)
print(title.group(1))

content = re.search(r"\n{2}(.+(\n.+)?){1,}.$", string)
print(content.group(1))

