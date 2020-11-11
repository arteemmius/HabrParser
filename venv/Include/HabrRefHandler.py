import re
import os
import uuid
from selenium import webdriver
from parsel import Selector
from lxml import etree

# директория файлов с ссылками на статьи собранными с помощью HabrRefGetter.py
REF_STORAGE = 'href/'

# номер категории с которой начинать обработку
N = 0

def writerXML(categoryValue, authorValue, titleValue, keywordList, textValue, sourceValue):
    # корень xml. элемент, в который вложены остальные
    root = etree.Element("doc")

    source = etree.SubElement(root, "source", auto='true', type='str', verify='true')
    source.text = etree.CDATA(sourceValue)

    # categoryValue - название файла, из которого берем ссылки на статьи. Обрезаем txt

    category = etree.SubElement(root, "category", auto='true', type='str', verify='true')
    category.text = etree.CDATA(categoryValue.replace(".txt", ""))
    # в корень добавляем автором, названием и т.д. взятым xpath из кода далее
    author = etree.SubElement(root, "author", auto='true', type='str', verify='true')
    author.text = etree.CDATA(authorValue)

    title = etree.SubElement(root, "title", auto='true', type='str', verify='true')
    title.text = etree.CDATA(titleValue)

    keywords = etree.SubElement(root, "keywords", auto='true', type='list', verify='true')
    for i in range(0, len(keywordList)):
        item_keywords = etree.SubElement(keywords, "item", type='str')
        item_keywords.text = etree.CDATA(keywordList[i])

    content = etree.SubElement(root, "text", auto='true', type='str', verify='true')
    content.text = etree.CDATA(re.sub(r'\s+', ' ', textValue))
    # в объект elementTree ладем сбор корня и всех вложенных тегов. записываем все в файл result
    tree = etree.ElementTree(root)
    if not os.path.exists("result/" + categoryValue.replace(".txt", "")):
        os.makedirs("result/" + categoryValue.replace(".txt", ""))
    tree.write("result/" + categoryValue.replace(".txt", "") + "/" + str(uuid.uuid4()) + ".xml", encoding='utf-8', pretty_print=True)


driver = webdriver.Chrome()
driver.set_window_size(1500, driver.get_window_size()['height'])
# заходим в директорию ref, вытаскиваем названия файла, который совпадает с названием категории, в которой находятся статьи
countRef = 0
fileList = os.listdir(path=REF_STORAGE)
# заходим в файлик, проходимся по ссылкам и вытаскиваем всю нужную информацию по статьям
for k in range(N, len(fileList)):
    f = open(REF_STORAGE + fileList[k])
    for line in f:
        # html тсраницу вытаскиваем, далее из нее путем xpath все нужное
        driver.get(line)
        sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))

        # text name название
        textName = sel.xpath("//h1[@class='post__title post__title_full']/span[@class='post__title-text']/text()").extract_first()
        # print(textName)

        # text content
        text = sel.xpath("//div[@class='post__text post__text-html js-mediator-article']//text()").extract()
        # text = list(filter(lambda a: a != '\n', sel.xpath("//div[@class='post__text post__text-html js-mediator-article']//text()").extract()))
        # print("".join(str(x).replace("\n", "") for x in text))
        # print(text)

        # key words
        keywordsList = sel.xpath("//li[@class='inline-list__item inline-list__item_hub']/a/text()").extract()
        # print(keywordsList)

        # author
        authorName = sel.xpath("//header[@class='post__meta']/a/span[@class='user-info__nickname user-info__nickname_small']/text()").extract_first()
        # print(authorName)
        # вызывается функция после обработки каждой статьи. так создается xml, записывается и т.д.
        writerXML(fileList[k], authorName, textName, keywordsList, " ".join(str(x).replace("\n", "") for x in text), line.replace('\n', ''))
        countRef = countRef + 1
        print(str(countRef) + " ref successful processed")
driver.close()
