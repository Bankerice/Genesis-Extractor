import re
import string


from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

def main():
    br = RoboBrowser()

    mainpageGrades = extractMainPage(br)

def extractMainPage(robo):
    br = robo
    br.open("https://parents.chclc.org/genesis/sis/view?gohome=true")
    form = br.get_form()
    form["j_username"] = "3010476@chclc.org"
    form["j_password"] = "y7cvmz2d"
    br.submit_form(form)

    #Converts the HTML of the grade page into a string
    src = str(br.parsed())

    #Removes initial Javascript
    src = src[src.find('<!-- Start of Header-->')+len('<!-- Start of Header-->'): len(src)]

    
    #Removes all HTML tags
    soup = BeautifulSoup(src,"lxml")
    src = ''.join(soup.findAll(text=True))

    #Removes all tabs and newlines
    src = " ".join(src.split())

    #Cuts the string into the important parts
    notDone = True
    i = src.find('Fri')+3 #Consistent and close reference point
    while(notDone):
        i += 1
        if(ord(src[i])>=57):
            notDone = False
    src = src[i+2:src.rfind('%')+1]


    #Parses the text
    grades = src.split('%')
    grades.pop()
    for i in range(len(grades)):
        grades[i] = grades[i].split("Email:")
        if(i != 0):
            grades[i][0] = grades[i][0][11:len(grades[i][0])]

    return grades


if __name__ == '__main__':
    main()