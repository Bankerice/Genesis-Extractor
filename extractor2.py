import course
import assignment
import datetime
import re
import string


from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

re._pattern_type = re.Pattern

# Global variables
studentName = ""
studentID = ""
courses = list(map(course.Course,[]))
periods = ['A','B','C','D','E','F','G','H']
mp = 2

# Body
def main():
    br = RoboBrowser(parser='html.parser')

    mainpageGrades = extractMainPage(br)


def extractMainPage(robo):
    br = robo
    br.open("https://parents.chclc.org/genesis/sis/view?gohome=true")
    form = br.get_form()
    form["j_username"] = "@chclc.org"
    form["j_password"] = ""
    br.submit_form(form)
  
    #Converts the HTML of the Summary page into a string and uses it to create courses list of Course objects
    studentID = ""
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=studentsummary&action=form&studentid="+studentID)
    src = str(br.parsed())
    #print(src)
    studentID = src[src.find("Student ID")+34:src.find("Student ID")+41]
    
    courseSchedule = src[src.find('Teacher'):len(src)]
    courseSchedule = courseSchedule[courseSchedule.find('>A<')+1:courseSchedule.find('listheading')]
    soup = BeautifulSoup(courseSchedule,"lxml")
    courseSchedule = ''.join(soup.findAll(text=True))
    createCourseList(courseSchedule)



    #Converts the HTML of the grade page into a string
    #br.open("document.frmHome.action='parents?tab1=studentdata&tab2=gradebook&tab3=listassignments&studentid="+studentID+"&action=form&date="+)
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
        br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=coursesummary&studentid=" + str(studentID) + "&action=form&courseCode=" + str(courses[i].code) + "&courseSection=" + str(courses[i].section) + "&mp=2")
        a = str(br.parsed)
            
        assignment = a[a.find("<b>"):a.find("</b>")]
        assignment = assignment[3:len(assignment)]
        print(assignment)
        
        aCategory = a[a.find("Close Window"):len(a)]
        aCategory = aCategory[aCategory.find("</div>")+6:aCategory.find("<td")]
        aCategory = " ".join(aCategory.split())
        aCategory = aCategory[0:aCategory.find("</td>")-1]
        print(aCategory)
        aDate = a[a.find("listroweven"):len(a)]
        aDate = aDate[aDate.find("</div>")+1:aDate.find("style")]
        aDate = aDate[aDate.find("<div>")+5:aDate.find("</div>")]
        if (len(aDate)>0):
            yr = 0
            if (int(datetime.datetime.today().month) >= int(aDate[0:aDate.find("/")])):
                yr = datetime.datetime.today().year
            else:
                yr = datetime.datetime.today().year - datetime.timedelta(365)
            aDate = datetime.datetime(yr,int(aDate[0:aDate.find("/")]),int(aDate[aDate.find("/")+1:len(aDate)]))
        print(aDate)

        a = " ".join(a.split())
        aGrade = a[(a.find(" / "))-5:(a.find(" / "))+5]
        #aGrade = " ".join(aGrade.split())
        aPtsRec = aGrade[aGrade.find(">")+2:aGrade.find(" / ")]
        aPtsWorth = aGrade[aGrade.find(" / ")+3:len(aGrade)]
        print(aGrade)
        print(aPtsRec)
        print(aPtsWorth)
        if (len(aPtsWorth)>0):
            print("asdfasdf")
            intPtsWorth = int(aPtsWorth)
            intPtsRec = int(aPtsRec)
            courses[i].addAssignment(assignment,intPtsWorth,intPtsRec,aCategory,aDate.date)
            print(courses[i].courseName)
            

    


    #Removes initial Javascript
    src = src[src.find('<!-- Start of Header-->')+len('<!-- Start of Header-->'): len(src)]

    #Removes all HTML tags
    soup = BeautifulSoup(src,"lxml")
    src = ''.join(soup.findAll(text=True))

    #Removes all tabs and newlines
    src = " ".join(src.split())
    #studentName = src[src.index("Select Student:")+16:src.index("Weekly Summary")-1]    
    
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

    # for i in range(len(courses)):
    #     print(courses[i].courseName)


if __name__ == '__main__':
    main()


