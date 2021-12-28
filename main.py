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
options.binary_location = "D:\workspace\chrome.sync\Chrome-bin\chrome.exe"
options.headless = True
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
      return an object that contains the categories and its links
      e.g: {
          categories: ['Getting started'],
          links: [ [{name: '...', url: '/courses/...'}, ...], [...], ... ]
          }
    """
    # menu = document.querySelector(".course-category-hover").parentNode.querySelectorAll("menu a")
    menu = driver.execute_script("""
      // category and links indexes will be the same here
      let data = {
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

# url example: https://www.educative.io/courses/grokking-computer-networking


def downloadCourse(url):
    try:
        driver.get(url)
        sleep(1)
        courseName = driver.execute_script("return document.title")
        pathToSaveEverything = courseName
        Path(pathToSaveEverything).mkdir(parents=True, exist_ok=True)

        content = getCourseContentsLinks()
        # TODO: take screenshot, convert it to pdf, save the pdf in the category directory and remove the screenshot
        for i, categoryName in enumerate(content.get("categories")):
            # opening from filename
            print("\n")
            print(categoryName)
            print("-------------------------------------")
            courseCategoryDir = os.path.join(
                pathToSaveEverything, cleanFileName(categoryName))

            Path(courseCategoryDir).mkdir(parents=True, exist_ok=True)

            #! TODO: FIX THIS
            for course in content.get("links")[i]:
                pdfFileName = course.get("name") + ".pdf"
                screenShotImg = takeScreenShot(base_url+course.get("url"))
                # sleep(2)
                print(course.get("name") + " DONE !")
                # os.rename(screenShotImg, os.path.join(
                #     courseCategoryDir, cleanFileName(screenShotImg)))
                # with open(os.path.join(courseCategoryDir, pdfFileName), "wb") as f:
                #     f.write(img2pdf.convert(screenShotImg))
                #     os.remove(screenShotImg)
                # print(course)
                # move the converted pdf to the right course category dir
                # os.rename(pdfFileName, os.path.join(
                #     courseCategoryDir, pdfFileName))
                #   os.remove(path)
        return courseName
    except Exception as e:
        print(e)
        return e


def takeScreenShot(url):
    """
    @params: <url> which is the course url
    @returns: the screenshot file name if success else it returns an Exception
    """
    try:
        driver.get(url)
        sleep(6)

        screenShotFileName = driver.execute_script("return document.title")
        screenShot = cleanFileName(screenShotFileName)+".png"
        # # document.body.parentNode.scroll(Height || Width) => int

        def getWindowLen(X): return driver.execute_script(
            "return document.body.parentNode.scroll"+X)

        driver.set_window_size(getWindowLen("Width"), getWindowLen("Height"))
        driver.find_element_by_tag_name(
            "body").screenshot(screenShotFileName+".png")
        sleep(1)
        # driver.quit()
        return screenShot
    except Exception as e:
        return e


# courseName = downloadCourse(
#     "https://www.educative.io/courses/grokking-computer-networking")

if __name__ == "__main__":
    print("DOWNLOADING...")
    courseName = ""
    try:
        #! FIX THE LOGIN
        login("contactwassim016@gmail.com", "Wassim_005")
        print("\n Logging in... \n")
        sleep(3)
        courseName = downloadCourse(
            "https://www.educative.io/courses/grokking-computer-networking")
    except Exception as e:
        print("\n Failed !!")
        print(e)
    # finally:
    #     driver.quit()
