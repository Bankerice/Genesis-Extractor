import course
import assignment
import userActions
import datetime
import re
import string
import os

from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

re._pattern_type = re.Pattern

# Global variables
studentName = ""
studentID = ""
password = ""
courses = list(map(course.Course,[]))
periods = ['A','B','C','D','E','F','G','H']
mp = 2
mpStartDates = [[1,9,2019],[2,11,2019],[25,1,2020],[4,4,2020]]

# Body
def main():
    br = RoboBrowser(parser='html.parser')
    mainpageGrades = extractMainPage(br)
    userAct()

def restart():
    # Clear arrays
    courses = list(map(course.Course,[]))

    br = RoboBrowser(parser='html.parser')
    mainpageGrades = extractMainPage(br)

def initUserData():
    if not os.path.exists("config.ini"):  
        file = open("config.ini","w")

        file.write(input("Student ID: ")+"\n")
        file.write(input("Password: ")+"\n")

        file.close()


def extractMainPage(robo):
    br = robo
    br.open("https://parents.chclc.org/genesis/sis/view?gohome=true")


    while br.url == "https://parents.chclc.org/genesis/sis/view?gohome=true":
        initUserData()


        form = br.get_form()

        file = open("config.ini","r")
        text = file.readlines()
        studentID = text[0].strip("\n")
        password = text[1].strip("\n")
        form["j_username"] = studentID+ "@chclc.org"
        form["j_password"] = password
        br.submit_form(form)
        file.close()

        if(br.url == "https://parents.chclc.org/genesis/sis/view?gohome=true"):
            initUserData()
            os.remove("config.ini")
            
    #Converts the HTML of the Summary page into a string and uses it to create courses list of Course objects
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=studentsummary&action=form&studentid="+studentID)
    src = str(br.parsed())
    
    courseSchedule = src[src.find('Teacher'):len(src)]
    courseSchedule = courseSchedule[courseSchedule.find('>A<')+1:courseSchedule.find('listheading')]
    soup = BeautifulSoup(courseSchedule,"lxml")
    courseSchedule = ''.join(soup.findAll(text=True))
    createCourseList(courseSchedule)


    #Converts the HTML of the grade page into a string
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=weeklysummary&action=form&studentid="+studentID)
    src = str(br.parsed)
    links = br.get_links()
    urls = [link.get("href") for link in links]
    for i in range(len(links)):
        if str(links[i]).__contains__("listassignments"):
            br.follow_link(links[i])
            a = str(br.parsed)
            a = " ".join(a.split())

    # CREATE ASSIGNMENT LIST
    # Determine course codes for each course
    for i in range(len(courses)):
        code = src[src.find(courses[i].courseName[0:7])-90:src.find(courses[i].courseName[0:7])+10]
        if(len(code)>0):
            code = code[code.find(",")+2:code.find(")")-1]
            courses[i].code = code[0:code.find(":")]
            courses[i].section = code[code.find(":")+1:len(code)+1]

    # Create assignment list for each course from course code
    for i in range(len(courses)):

        if (len(courses[i].code)>0): # Does not include study hall
            br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=coursesummary&studentid=" + str(studentID) + "&mp=MP" + str(mp) +"&action=form&courseCode=" + str(courses[i].code) + "&courseSection=" + str(courses[i].section))
            a = str(br.parsed)
            createAssignmentList(a,i)

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
    courseInfo = src.split('%')
    courseInfo.pop()
    for i in range(len(courseInfo)):
        courseInfo[i] = courseInfo[i].split("Email:")
        if(i != 0):
            courseInfo[i][0] = courseInfo[i][0][11:len(courseInfo[i][0])]
    
        # Separate info
        cInfo = courseInfo[i][0]
        cName = cInfo[0:cInfo[0:cInfo.index(",")].rfind(" ")]
        cTeacher = cInfo[cInfo[0:cInfo.index(",")].rfind(" ")+1:len(cInfo)-1]


    
   
def createCourseList(courseSchedule):
    #Creates courses list of Course objects from info on Summary page
    
    #Ignore LBs
    while(courseSchedule.__contains__("L1\n")):
        lb1 = courseSchedule[courseSchedule.find('L1\n'):len(courseSchedule)]
        lb1 = lb1[0:lb1.find("\n\n")+3]
        courseSchedule = courseSchedule[0:courseSchedule.find('L1\n')] + courseSchedule[courseSchedule.find('L1\n')+len(lb1):len(courseSchedule)]
    while(courseSchedule.__contains__("L2\n")):
        lb2 = courseSchedule[courseSchedule.find('L2\n'):len(courseSchedule)]
        lb2 = lb2[0:lb2.find("\n\n")+3]
        courseSchedule = courseSchedule[0:courseSchedule.find('L2\n')] + courseSchedule[courseSchedule.find('L2\n')+len(lb2):len(courseSchedule)]

    courseSchedule = courseSchedule[0:len(courseSchedule)-3]
    courseSchedule = courseSchedule.split("\n\n")
    
    #Create list of Course objects
    for i in range(len(courseSchedule)):
        if courseSchedule[i].startswith("\n"):
            courseSchedule[i] = courseSchedule[i][1:len(courseSchedule[i])]
        courseSchedule[i] = courseSchedule[i].split("\n")
        courses.append(course.Course(courseSchedule[i][1],courseSchedule[i][5],courseSchedule[i][0],True if courseSchedule[i][2]=='FY' else False))

def createAssignmentList(a,i):
    # Creates a list of assignments for every course
    
    a2 = a[a.find("<b>Assignments</b>")+18:a.find("Assignments graded as")]

    while(a2.__contains__("<b>")):
        valid = True

        # Assignment Name
        assignment = a2[a2.find("<b>")+3:a2.find("</b>")]
        a2 = a2[a2.find("</b>")+4:len(a2)]
        
        # Assignment Category
        aCategory = a[a.find("Close Window")+10:len(a)]
        aCategory = aCategory[aCategory.find("</div>")+6:aCategory.find("<td")]
        aCategory = " ".join(aCategory.split())
        aCategory = aCategory[0:aCategory.find("</td>")]

        # Assignment Date Posted
        aDate = a[a.find("listrow"):len(a)]
        aDate = aDate[aDate.find("</div>")+1:aDate.find("style")]
        aDate = aDate[aDate.find("<div>")+5:aDate.find("</div>")]
        year = datetime.date.today().year
        if (int(aDate[0:aDate.find("/")])>datetime.date.today().year):
            year -= 1
        aDate1 = datetime.date(year,int(aDate[0:aDate.find("/")]),int(aDate[aDate.find("/")+1:len(aDate)]))
        a = a[a.find("Close Window")+10:len(a)]

        # Assignment Grade
        a2 = " ".join(a2.split())
        
        aGrade = a2[a2.find("nowrap="):a2.find("nowrap=")+30]
        aGrade = aGrade[0:aGrade.find("<")]
        if(aGrade.__contains__("/")): # Found " / " marker indicating a grade
            aPtsRec = aGrade[aGrade.find(">")+2:aGrade.find(" / ")]
            aPtsWorth = aGrade[aGrade.find(" / ")+3:len(aGrade)]
        else:
            continue # Assignments marked as "DONE," etc.
        try: 
            intPtsWorth = float(aPtsWorth)
            intPtsRec = float(aPtsRec)
        except ValueError:
            valid = False
            
        # Add assignment to course assignments list 
        if (valid):
            courses[i].addAssignment(assignment,intPtsWorth,intPtsRec,aCategory,aDate1)
            # Fix adding-assignment-to-all-courses issue
            for j in range(len(courses)):
                if (j!=i):
                    temp = []
                    for x in range(len(courses[j].assignments)):
                        if ((str(courses[j].assignments[x].assignmentName).__contains__(assignment))==0):
                            temp.append(courses[j].assignments[x])
                    courses[j].assignments = temp
    
def getCourseList():
    return courses

def userAct():
    # interface = userActions.UserActions(studentName,studentID,1)
    # for i in interface.getDailyCourseGrades(5,1,9,2019,1,11,2019):
    #     print(str(i[0])+"\t"+str(i[1]))
    mp = 2
    # restart()
    interface2 = userActions.UserActions(studentName,studentID,2)
    # interface.setMP(2)
    for i in interface2.getDailyCourseGrades(5,2,11,2019,20,12,2019):
        print(str(i[0])+"\t"+str(i[1]))
        
    mp = 1
    # restart()
    interface = userActions.UserActions(studentName,studentID,1)
    # interface.setMP(1)
    for i in interface.getDailyCourseGrades(5,1,9,2019,1,11,2019):
        print(str(i[0])+"\t"+str(i[1]))
    

    # print(interface.getCourseGradeOnDay(5,20,12,2019,2))

def userAct2():
    # ------------------------------------------- TEST USER ACTIONS -------------------------------------------
    val = False
    # while (val==0):
    #     ans = input("Choose MP: ")
    #     try:
    #         mpAns = int(ans)
    #         val = True
    #     except ValueError:
    #         val = False
    mpAns = 2
    mp = 2
    interface = userActions.UserActions(studentName,studentID,mpAns)
    # print(interface.getCourseGradeOnDay(5,20,12,2019,2))
    
    # val = False
    # while (val==0):
    #     ans = input("Choose Course as number from 0 to " + str(len(courses)-1) + ": ")
    #     try:
    #         courseAns = int(ans)
    #         val = True
    #     except ValueError:
    #         val = False

    courseAns = 5
    courseNum = courseAns
    print(courses[courseAns].courseName)
    # for i in range(len(courses[courseAns].assignments)):
        # print(courses[courseAns].assignments[i].assignmentName)
    mpStartDates = [[1,9,2019],[2,11,2019],[25,1,2020],[4,4,2020]] # marking period start dates

    # MP 1 (manually - no loop)
    d1 = mpStartDates[0][0]
    m1 = mpStartDates[0][1]
    y1 = mpStartDates[0][2]

    d2 = mpStartDates[1][0] - 1
    m2 = mpStartDates[1][1]
    y2 = mpStartDates[1][2]

    # interface.setMP(1)
    # mp = 1
    # print(mp)
    # arr = interface.getDailyCourseGrades(courseNum,d1,m1,y1,d2,m2,y2)
    # arrTotal = [[]]

    # for a in range(len(arr)):
    #     arrTotal.append(arr[a])
    #     try:
    #         print(str(arr[a][0])+ "\t" + str(arr[a][1]))
    #     except IndexError:
    #         print(str(a) + "\t" + str(len(arr)))
            
    # MP 2 (manually - no loop)
    d1 = mpStartDates[1][0]
    m1 = mpStartDates[1][1]
    y1 = mpStartDates[1][2]

    d2 = datetime.datetime.today().day #mpStartDates[2][0] - 1
    m2 = datetime.datetime.today().month #mpStartDates[2][1]
    y2 = datetime.datetime.today().year #mpStartDates[2][2]

    mp = 2
    interface = userActions.UserActions(studentName,studentID,2)
    # mp = 2
    # restart()
    print(mp)
    arr2 = interface.getDailyCourseGrades(courseNum,d1,m1,y1,d2,m2,y2)
    
    
            
    for a in range(len(arr2)):
        # arrTotal.append(arr2[a])
        try:
            print(str(arr2[a][0])+ "\t" + str(arr2[a][1]))
        except IndexError:
            print(str(a) + "\t" + str(len(arr2)))
    
    # print(arrTotal)
    
    # for a in range(len(arrTotal)):
    #     try:
    #         print(str(arrTotal[a][0]) + "\t" + str(arrTotal[a][1]))
    #     except IndexError:
    #         print(str(a) + "\t" + str(len(arrTotal)))
    
    
    # Output data as a text file

    # for a in range (len(courses)):
    #     courseNum = a
    #     # if (len(courses[a].code)>0):
    #     for x in range (0,1): #(0,4): # Goes through every marking period 
    #         arr = [[]] # [day count][date,grade]

    #         d1 = mpStartDates[x][0]
    #         m1 = mpStartDates[x][1]
    #         y1 = mpStartDates[x][2]

    #         if (x<4):
    #             d2 = datetime.datetime.today().day #mpStartDates[x+1][0] - 1
    #             m2 = datetime.datetime.today().month #mpStartDates[x+1][1]
    #             y2 = 2019 #mpStartDates[x+1][2]
    #         else:
    #             d2 = 17
    #             m2 = 6
    #             y2 = 2020
            
    #         interface.setMP(x+1)
    #         arr = interface.getDailyCourseGrades(courseNum,d1,m1,y1,d2,m2,y2)
    #         interface.outputData(courseNum, arr, (x==0))

        
    #         # if (arr!=0):
    #         #     for i in range(1,len(arr)):
    #         #         a = arr[i]
    #         #         print(str(a[0])+":\t"+str(a[1]))
        

if __name__ == '__main__':
    main()


