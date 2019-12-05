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
    studentID = ""
    form["j_username"] = studentID + "@chclc.org"
    form["j_password"] = ""
    br.submit_form(form)
  
    #Converts the HTML of the Summary page into a string and uses it to create courses list of Course objects
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=studentsummary&action=form&studentid="+studentID)
    src = str(br.parsed())
    studentID = src[src.find("Student ID")+34:src.find("Student ID")+41]
    
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
            
            print(courses[i].courseName + " GRADE:\t" + str(courses[i].currentMPGrade)) # off by a little because of weighting
            
    # Test by printing all assignments of all courses
    # for i in range(len(courses)):
    #     if (len(courses[i].code)>0):
    #         print(courses[i].courseName)
    #         for x in range(len(courses[i].assignments)):
    #            print(courses[i].assignments[x].assignmentName + "\t" + str(courses[i].assignments[x].gradePercent) + "\t" + str(courses[i].assignments[x].category) + "\t" + str(courses[i].assignments[x].datetimePosted))
        
    


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
    


if __name__ == '__main__':
    main()


