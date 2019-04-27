import json
from plumbum import cli, local
from requests_html import HTMLSession
import urllib.request


class DownloadAudioBible(cli.Application):
    session = HTMLSession()
    chapter_info_file = local.path('chapters_info.json')

    def main(self):
        if not self.chapter_info_file.exists():
            self.get_chapter_info()

        self.download_mp3_for_all_chapter()

    def download_mp3_for_all_chapter(self):
        chapter_infos = self.chapter_info_file.read()
        chapter_infos = json.loads(chapter_infos)

        for chap in chapter_infos:
            self.download_chapter_audio(chap)

    def download_chapter_audio(self, chapter):
        local.path(chapter['name']).mkdir()
        file_dir = local.path(chapter['name'])
        for i in range(1, chapter['subs']):
            link = 'https://www.bible.com/mn/bible/1590/{}.{}.АБ2013'.format(chapter['pre'], i)
            req = self.session.get(link)
            mp3_link = req.html.find('source')[1].attrs['src']
            mp3_link = 'http://' + mp3_link.split('?version_id=')[0][2:]
            title = req.html.find('title', first=True).text
            file_name = file_dir / title + '.mp3'

            if not local.path(file_name).exists():
                mp3file = urllib.request.urlopen(mp3_link)
                with open(file_name, 'wb') as output:
                    output.write(mp3file.read())
                    print("Downloaded {}".format(file_name))

    def get_all_chapters(self):
        link = 'https://www.bible.com/bible/1/GEN.1.KJV'
        req = self.session.get(link)
        ul = req.html.find('ul#list ma0 pa0 bg-white pb5 min-vh-100')
        print(ul.html)

    def get_chapter_info(self):
        """Using selenium package because web is complicated to understand ajax requests"""

        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from time import sleep

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://www.bible.com")

        driver.find_element_by_xpath("//a[contains(text(),'Read')]").click()
        driver.implicitly_wait(2)

        driver.find_element_by_xpath(
            "//*[@role='button' and @class='w-100 flex items-center bb b--black-20 mr3 outline-0' "
            "and span[contains(text(),'Genesis 1')]]"
        ).click()
        driver.implicitly_wait(2)

        chapter_list = driver.find_element_by_xpath(
            "//ul[@class='list ma0 pa0 bg-white pb5 min-vh-100']"
        ).find_elements_by_tag_name("li")

        chapters = []
        for li in chapter_list:
            pre = li.get_attribute("option")
            name = li.text
            chapters.append({'pre': pre, 'name': name, 'subs': 0})

        for chap in chapters:
            driver.find_element_by_xpath("//li[@data-vars-event-label='{}']".format(chap['pre'])).click()
            driver.implicitly_wait(2)
            sub_chapters = driver.find_element_by_xpath(
                "//div[@class='ma0 pa0 pb5 flex flex-wrap']"
            ).find_elements_by_tag_name("div")
            num_sub_chapters = len(sub_chapters)
            chap['subs'] = num_sub_chapters
            print(chap)

            # Cancel from Popup
            driver.find_element_by_xpath(
                "//button[@data-vars-event-action='Cancel' and @data-vars-event-category='Chapter Picker' "
                "and @class='ma0 pa0 truncate f7 f6-m black-30 bn bg-transparent outline-0']"
            ).click()
            driver.implicitly_wait(2)

            # Open Chapters list
            driver.find_element_by_xpath(
                "//*[@role='button' and @class='w-100 flex items-center bb b--black-20 mr3 outline-0' "
                "and span[contains(text(),'Genesis 1')]]"
            ).click()
            sleep(2)
        driver.close()

        self.chapter_info_file.write(json.dumps(chapters))
        print("Chapter information saved to file {}".format(self.chapter_info_file))


if __name__ == '__main__':
    DownloadAudioBible.run()
