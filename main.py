#
# * Author: wassim ben jdida
# * Github: wassimbj
# -----------------------------------------------------------------------------------
# a python script for downloading educative.io courses
# ? NOTE: this is a not a hacking tool, you must have access to the course to be able to download it
# ? read the readme to see how you can use it :)
# -----------------------------------------------------------------------------------s

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import img2pdf
import os
from pathlib import Path

base_url = "https://educative.io"

options = webdriver.ChromeOptions()
# change this one according to where you have the binary
options.binary_location = "D:\workspace\chrome.sync\Chrome-bin\chrome.exe"
options.headless = True
options.add_argument("--log-level=3")
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
# driver.maximize_window()
driver.set_window_size(1700, 1700)  # you can change this based on your PC


def login(email, password):
    """
    opens the login modal, enter the login details and submit the form
    @returns true for success and Excpetion otherwise
    """
    try:
        driver.get(base_url)
        sleep(7)
        # # open login modal
        driver.execute_script(
            'document.querySelector(".logged-out > div > button").click()')
        sleep(2)
        # enter email and password
        driver.execute_script(
            'document.querySelector("form")[0].value = "'+email+'"')
        driver.execute_script(
            'document.querySelector("form")[1].value = "'+password+'"')
        # submit the form
        driver.execute_script('document.querySelector("form")[3].click()')
        return True
    except Exception as e:
        print("Login Error: ")
        print(e)
        return e


def getCourseContentsLinks():
    """
    loop throught the course contents, get the categories and the lessons for each category
    @returns: a dict
    """

    menu = driver.execute_script("""
      // category and links indexes will be the same here
      let data = {
        totalLessons: 0,
        categories: [],
        links: []
      }
      let categories = document.querySelectorAll(".course-category-hover")
      for(let i = 0; i < categories.length; i++){
         let category = categories[i].parentNode.querySelector("h5").textContent
         let menuLinks = categories[i].parentNode.querySelectorAll("menu a")
         let menu = []
         for(let j = 0; j < menuLinks.length; j++){
            menu.push({
                name: menuLinks[j].querySelector('span').textContent,
                url: menuLinks[j].getAttribute("href")
            })
            data.totalLessons += 1
         }
         data.categories.push(category)
         data.links.push(menu)
      }
      return data
   """)
    # return the data object
    return dict(menu)


def cleanFileName(name):
    return str(name).replace(":", "-").replace("?", "")


def downloadCourse(whereToSaveIt, url):
    # url example: https://www.educative.io/courses/grokking-computer-networking
    """
    navigate to the lesson link, take a screenshot and convert it to pdf

    @params: <url> = course url, example is above
    @returns: a stats dict which has the total lessons and the successfully downloaded files.
    """
    try:
        driver.get(url)
        sleep(1)
        courseName = driver.execute_script("return document.title")
        pathToSaveEverything = os.path.join(whereToSaveIt, courseName)
        Path(pathToSaveEverything).mkdir(parents=True, exist_ok=True)
        downloadedFiles = 0
        content = getCourseContentsLinks()
        stats = {
            "totalLessons": content.get("totalLessons"),
            "totalDownloaded": 0
        }
        for i, categoryName in enumerate(content.get("categories")):
            print("\n")
            print(categoryName)
            print("-------------------------------------")
            courseCategoryDir = os.path.join(
                pathToSaveEverything, cleanFileName(categoryName))

            Path(courseCategoryDir).mkdir(parents=True, exist_ok=True)

            for course in content.get("links")[i]:
                pdfFileName = cleanFileName(course.get("name") + ".pdf")
                pdfFilePath = os.path.join(courseCategoryDir, pdfFileName)

                screenShotImgName = cleanFileName(course.get("name")+".png")
                screenShotImgPath = os.path.join(
                    courseCategoryDir, screenShotImgName)
                isScreenShoted = takeScreenShot(
                    base_url+course.get("url"), screenShotImgPath)
                # screenshot is not taken
                if isScreenShoted == False:
                    continue

                with open(pdfFilePath, "wb") as f:
                    img2pdf
                    f.write(img2pdf.convert(screenShotImgPath))
                    os.remove(screenShotImgPath)
                    print("Downloaded: [" + course.get("name")+"]")
                    downloadedFiles += 1

        stats["totalDownloaded"] = downloadedFiles
        return stats
    except Exception as e:
        print(e)
        return e


def takeScreenShot(url, savingPath):
    """
    @params: <url> which is the course url
    @returns: True if success else it returns False
    """
    try:
        driver.get(url)
        sleep(10)

        screenShotFileName = driver.execute_script("return document.title")

        def getWindowLen(X): return driver.execute_script(
            "return document.body.parentNode.scroll"+X)

        driver.set_window_size(getWindowLen("Width"), getWindowLen("Height"))
        isSaved = driver.find_element_by_tag_name(
            "body").screenshot(savingPath)
        if isSaved == False:
            # print(f"\n\n NOT SAVED ({savingPath}) !!! \n\n")
            return False
        sleep(1)

    except Exception as e:
        return False


if __name__ == "__main__":
    try:

        # getting the data
        print("\n\n ------------------------------------------------------- \n")
        email = input("Your educative.io email: ")
        password = input("your password: ")
        print("\n")
        courseUrl = input("Course url: ")
        saveDir = input("Path to save this course: ")
        print("\n ------------------------------------------------------- \n")

        # the real stuff
        result = login(email, password)
        if result != True:
            print("LOGIN ERROR")
            raise Exception()

        print("\n LOGGING IN... \n")
        sleep(3)  # wait until we login
        print("\n DOWNLOADING... \n")
        downloadStats = downloadCourse(saveDir, courseUrl)

        print(f"""
            \n FINISHED. \n
            Total lessons: {downloadStats.get("totalLessons")}
            \n
            Total downloaded: {downloadStats.get("totalDownloaded")}
        """)

    except Exception as e:
        print("\n FAILED !!")
        print(e)
    finally:
        driver.quit()
