from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import csv

import itertools

def translate(string):

    string = string[:len(string)-1] # removes period


#seperates string into AND pieces
    if '; and ' in string:
        stringList = string.split('; and ')
    if '; ' in string:
        stringList = string.split('; ')
    else:
        stringList = string.split(' and ')
#print(stringList)

#Seperates each individual AND piece into it's seperate OR pieces    
    for i in range(len(stringList)):
    
        if 'one of ' in stringList[i]:
            stringList[i] = stringList[i][7:]
            stringList[i] = stringList[i][:stringList[i].find(' or ')]+', '+stringList[i][stringList[i].find(' or ')+4:]
            stringList[i] = stringList[i].split(", ")
        #print(stringList[i])
        else:
            stringList[i] = stringList[i].split(" or ")


    for i in range(len(stringList)):
        for j in range(len(stringList[i])):
            name = ''
            if len(stringList[i][j])>3:
                name = stringList[i][j][:-4]
            else:
                stringList[i][j] =  name + ' ' + stringList[i][j]          
                            
    



    all_prereqs = list(itertools.product(*stringList))
    stringToGo = ''
    for i in all_prereqs:
        for j in range(len(i)-1):
            stringToGo += i[j] + ';'
        stringToGo += i[len(i)-1]+'|'
    stringToGo = stringToGo[:-1]
    return stringToGo    


#downloads the webpage and closes it. saves it as page_html
with open('courses.csv', 'w', newline='') as file:
            fields = ['course_name','course_code', 'prerequisites']
            writer = csv.DictWriter(file, delimiter=',', fieldnames=fields)

            writer.writeheader()


#MAKE A DICTIONARY OF THE WEBPAGES
my_url = "https://www.ucalgary.ca/pubs/calendar/current/course-desc-main.html"
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

#html parsing
page_soup = soup(page_html, "html.parser")

containers = page_soup.findAll("div",{"class":"item-container"})
course_codes = containers[0].findAll("a",{"class":"link-text"})

my_dict = {}
for course in course_codes:
    course.string = course.string.rstrip(" ")
    course.string = course.string.lstrip(" ")
    if "," in course.string:
        continue
    if (len(course.string) > 1):
        
        my_dict[course.string[0:course.string.rindex(' ')]] = [course.string[course.string.rindex(' ')+1:], course['href']]

del my_dict['Course']
#END OF THE WEBPAGE SCRAPING

for key in my_dict:
    my_url = "https://www.ucalgary.ca/pubs/calendar/current/" + my_dict[key][1]
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()

#html parsing
    page_soup = soup(page_html, "html.parser")

#grabs each course
    containers = page_soup.findAll("div",{"class":"item-container"})
    course_codes = containers[0].findAll("a",{"class":"link-text"})

#Prints out the courses on a seperate line
    course_count = 0

    courses = {}

    for course in course_codes:
        course_count += 1
        course = str(course)

        courses[course_count-1] = dict()
        courses[course_count-1]['course_name'] = key + " " + course[-7:-4]
        courses[course_count-1]['course_code'] = my_dict[key][0] + " " + course[-7:-4]

#grabs all prerequistes
    all_prerequisites = page_soup.findAll("td", {"class":"myCell"})

#prints out the prerequisites on a seperate line
    prerequisite_count = 0
    for course in range(len(all_prerequisites)):
        prerequisite_count += 1
        prerequisites = all_prerequisites[course].find('span',{'class':'course-prereq'})
        prerequisite = ''
        for m in (prerequisites.contents):
        # print(m.string, end = "")
            prerequisite += m.string
        prerequisite = translate(prerequisite)
        print(prerequisite)
        try: 
            courses[prerequisite_count-1]['prerequisites'] = prerequisite
        except:
            continue
        print()

    with open('courses.csv', 'a', newline='') as file:
        fields = ['course_name','course_code', 'prerequisites']
        writer = csv.DictWriter(file, delimiter=',', fieldnames=fields)
        for courseCode, course in courses.items():
            writer.writerow(course)


