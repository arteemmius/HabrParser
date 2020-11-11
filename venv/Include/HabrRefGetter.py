from selenium import webdriver
from parsel import Selector
import re

# номер категории с которой начинать обработку
N = 0

driver = webdriver.Chrome("c:/utils/chromedriver_win32/chromedriver.exe")
# размер окна
driver.set_window_size(1500, driver.get_window_size()['height'])
# get html by url вызываем метод get и передаем ему url сайта

driver.get("https://habr.com/ru/hubs/")
# get data инициализируем объект selector для использования библиотеки xpath. sel ссылка на объект
# вытаскиваем код html страницы и передаем его в selector для обработки xpath
sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
# список ссылок на разделы. вытаскивается xpath-ом через selector
sectionRefList = sel.xpath("//div[@class='media-obj__body media-obj__body_list-view list-snippet']/a/@href").extract()
# список ссылок на названия категорий, разделов
sectionNameList = sel.xpath("//div[@class='media-obj__body media-obj__body_list-view list-snippet']/a/text()").extract()

# вытаскиваем номер последней страницы для сбора всех ссылок на катеогории и названий категорий
lastPage = re.findall('page\d+', sel.xpath("//a[@class='toggle-menu__item-link toggle-menu__item-link_pagination toggle-menu__item-link_bordered']/@href").extract_first())[0].replace("page", "")
# ходим по категориям и дособираем все категории и названия категорий со 2-й страницы
for i in range(2, int(lastPage) + 1):
    driver.get("https://habr.com/ru/hubs/page" + str(i) + "/")
    sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
    sectionRefList = sectionRefList + sel.xpath("//div[@class='media-obj__body media-obj__body_list-view list-snippet']/a/@href").extract()
    sectionNameList = sectionNameList + sel.xpath("//div[@class='media-obj__body media-obj__body_list-view list-snippet']/a/text()").extract()
# ходим по всем категориям, заходим в категории, вытаскиваем ссылки на статьи
for i in range(N, len(sectionRefList)):
    f = open('href/' + sectionNameList[i] + '.txt', 'a')
    # переходим в конкретную категорию и обрабатываем xpath и вытащили код html
    driver.get(sectionRefList[i])
#    print(sectionRefList[i])
#    print(sectionNameList[i])
    sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
    # работаем с одной страницей. если в категории 1 страница
    if sel.xpath("//ul[@class='toggle-menu toggle-menu_pagination']").extract_first() is None:
        # записываем ссылки на все статьи на этой странице
        f.write("\n".join(str(x) for x in sel.xpath("//li[@class='content-list__item content-list__item_post shortcuts_item']//h2[@class='post__title']/a/@href").extract()))
        f.write("\n")
    # работаем с двумя и более страницами
    else:
        # на сайте 8 или менее страниц. нет элемента последней страницы, поэтому элемент последней страницы просто как номер страницы, xpathщм вытаскиваем ссылки на страницы
        if sel.xpath("//a[@class='toggle-menu__item-link toggle-menu__item-link_pagination toggle-menu__item-link_bordered']/@href").extract_first() is None:
            # lastNumber = sel.xpath("//ul[@class='toggle-menu toggle-menu_pagination']/li[last()]/a/text()").extract_first()
            lastNumber = re.findall('page\d+', sel.xpath("//ul[@class='toggle-menu toggle-menu_pagination']/li[last()]/a/text()").extract_first())[0].replace("page", "")
        # если в категории более 8 страниц. вытаскиваем номер последней страницы. снова вытаскиваем ссылки на статьи
        else:
            # lastNumber = re.sub(r'[a-zA-Z/_]', '', sel.xpath("//a[@class='toggle-menu__item-link toggle-menu__item-link_pagination toggle-menu__item-link_bordered']/@href").extract_first())
            lastNumber = re.findall('page\d+', sel.xpath("//a[@class='toggle-menu__item-link toggle-menu__item-link_pagination toggle-menu__item-link_bordered']/@href").extract_first())[0].replace("page", "")
        for j in range(1, int(lastNumber) + 1):
            # обработали первую страницу
            if j == 1:
                f.write("\n".join(str(x) for x in sel.xpath("//li[@class='content-list__item content-list__item_post shortcuts_item']//h2[@class='post__title']/a/@href").extract()))
                f.write("\n")
                continue
            driver.get(sectionRefList[i] + "page" + str(j) + "/")
            sel = Selector(text=driver.find_element_by_xpath("//*").get_attribute("outerHTML"))
            # так как на хабре попадаются битые страницы(https://habr.com/ru/hub/infosecurity/page724/), проверяем загружена ли страница
            if sel.xpath("//a[@class='logo']") is None:
                continue
            f.write("\n".join(str(x) for x in sel.xpath("//li[@class='content-list__item content-list__item_post shortcuts_item']//h2[@class='post__title']/a/@href").extract()))
            f.write("\n")

driver.close()
