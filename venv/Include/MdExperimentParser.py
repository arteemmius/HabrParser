import os
import uuid
import re
from selenium import webdriver
from parsel import Selector
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree

# количество статей, которое планируем взять с https://md-eksperiment.org/etv_clubs.php?page=1&category=STATJI
# если указано неотрицательное число, считаем, что нужно забрать именно столько статей, если указан -1 то забираем все статьи с сайта
N = 1100


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
        os.makedirs("result/" + categoryValue.replace(".txt", "").replace(":", ","))
    tree.write("result/" + categoryValue.replace(".txt", "") + "/" + str(uuid.uuid4()) + ".xml", encoding='utf-8', pretty_print=True)


def parseKeyWords(keyWords):
    for i in range(0, len(keyWords)):
        s = keyWords[i].replace("\n", "").replace("\\u200", "").replace("\\u200b", "")
        s = re.sub(r'\s+', ' ', s)
        if s == " " or s == "":
            continue
        else:
            return s.split(",")


# инициализируем веб-драйвер
driver = webdriver.Chrome(ChromeDriverManager().install())
# размер окна
driver.set_window_size(1500, driver.get_window_size()['height'])
# get html by url вызываем метод get и передаем ему url сайта
driver.get("https://md-eksperiment.org/etv_clubs.php?page=1&category=STATJI")
# get data инициализируем объект selector для использования библиотеки xpath. sel ссылка на объект
# вытаскиваем код html страницы и передаем его в selector для обработки xpath
sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
sectionRefList = list()
sectionNameList = list()
# количество страниц на сайте
pageCountList = sel.xpath("//div[@class='row']//ul[@class='pagination-list']/li/a/text()").extract()
pageCount = int(pageCountList[len(pageCountList) - 1])
#print("pageCount = " + str(pageCount))

# получили все ссылки на статьи - sectionRefList и все названия категорий статей sectionNameList
for i in range(0, pageCount):
    # список ссылок на разделы. вытаскивается xpath-ом через selector
    sectionRefList = sectionRefList + sel.xpath("//div[@class='columns is-multiline block-section']/div[@class='column is-mobile is-half-tablet is-one-quarter-desktop']//h3/a/@href").extract()
    # названия категорий
    sectionNameList = sectionNameList + sel.xpath("//div[@class='columns is-multiline block-section']/div[@class='column is-mobile is-half-tablet is-one-quarter-desktop']//h3/a/text()").extract()
    # вычисляем адрес следующей страницы
    nextPageRef = sel.xpath("//div[@class='row']//a[@class='pagination-next']/@href").extract_first()
    if i == pageCount - 1:
        break;
    driver.get("https://md-eksperiment.org/" + nextPageRef)
    sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))

countGetArticle = 0
# идем по категориям и забираем статьи
for j in range(0, len(sectionRefList)):
    driver.get("https://md-eksperiment.org" + sectionRefList[j])
    sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
    # количество страниц на сайте
    includePageList = sel.xpath("//div[@class='row']//ul[@class='pagination-list']/li/a/text()").extract()
    includePageCount = int(includePageList[len(includePageList) - 1])
    #print("includePageCount = " + str(includePageCount))
    articleRefList = list()
    articleNameList = list()
    for k in range(0, includePageCount):
        # ссылки на статьи
        articleRefList = articleRefList + sel.xpath("//div[@class='columns is-multiline block-section ']/div[@class='column is-mobile is-half-tablet is-one-quarter-desktop']//h3/a/@href").extract()
        # названия статей
        articleNameList = articleNameList + sel.xpath("//div[@class='columns is-multiline block-section ']/div[@class='column is-mobile is-half-tablet is-one-quarter-desktop']//h3/a/text()").extract()
        if k == includePageCount- 1:
            break;
        # вычисляем адрес следующей страницы
        nextPageRefS = sel.xpath("//div[@class='row']//a[@class='pagination-next']/@href").extract_first()
        driver.get("https://md-eksperiment.org" + nextPageRefS)
        sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
    #print(articleRefList)
    #print(articleNameList)
    for l in range(0, len(articleRefList)):
        driver.get("https://md-eksperiment.org" + articleRefList[l])
        sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
        # название статьи
        titleValue = sel.xpath("//header[@class='row content-header']/h1/text()").extract_first()
        #print(titleValue)
        # ключевые слова
        keywordList = sel.xpath("//div[@class='content']//p[@class='text-keywords']/text()").extract()
        #print(keywordList)
        content = sel.xpath("//div[@class='content']//p/text()").extract()
        content.pop()
        # текст
        textValue = " ".join(str(x).replace("\n", "") for x in content)
        #print(textValue)
        # ссылка на статью
        sourceValue = "https://md-eksperiment.org" + articleRefList[l]
        # записываем данные в xml файл
        writerXML(sectionNameList[j], "", titleValue, parseKeyWords(keywordList), textValue, sourceValue)
        countGetArticle = countGetArticle + 1
        print(str(countGetArticle) + " статей успешно обработано!")
        if countGetArticle >= N and N != -1:
            print("получено " + str(countGetArticle) + " статей, выход из программы...")
            driver.close()
            exit(0)

#print(sectionRefList)
#print(sectionNameList)
#print(str(len(sectionRefList)))
#print(str(len(sectionNameList)))
driver.close()
