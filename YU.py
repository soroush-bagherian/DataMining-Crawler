import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger('__main__')


class YU():
    Department_Page_Url = "https://www.york.ac.uk/students/studying/manage/programmes/module-catalogue/module"
    University = "University of York"
    Abbreviation = "UCB"
    University_Homepage = "https://www.york.ac.uk/"

    # Below fields didn't find in the website
    Prerequisite = None
    References = None
    Scores = None
    Projects = None
    Professor_Homepage = None

    def get_courses_of_department(self, department_id):

        academic_year = "2021-22"

        department_url = self.Department_Page_Url + "?query=&department= " + department_id + "&year=" + academic_year #+ "&max="+"500"+"&offset=0"

        department_course_len = self.get_courseList_len(department_url)

        department_url += "&max="+ department_course_len +"&offset=0"

        department_page_content = requests.get(department_url).text
        department_soup = BeautifulSoup(department_page_content, 'html.parser')

        courses = department_soup.find("table", {"id": "modules"}).find_all("tr")
        # remove table header
        courses.pop(0)

        return courses, department_url

    def get_courseList_len(self, department_url):

        department_page_content = requests.get(department_url).text
        department_soup = BeautifulSoup(department_page_content, 'html.parser')

        department_records_len = department_soup.find('div', {'class': 'pagination'}).find_all('a', {'class': 'step'})[-1].text

        return department_records_len

    def get_course_data(self, course):
        Course_Title = course.find(class_="title").text

        Unit_Count = course.find(class_="hours").text
        Unit_Count = Unit_Count[:-5].rstrip()

        Description = course.find(class_='courseblockdesc').text

        course_sections = course.find_all(class_='course-section')

        Objective = None
        Outcome = None
        Professor = None
        Required_Skills = None

        for section in course_sections:
            inner_sections = section.find_all('p')
            for inner_section in inner_sections:
                inner_section_title = inner_section.find('strong')

                if inner_section_title.text == "Course Objectives:":
                    inner_section_title.decompose()
                    Objective = inner_section.text.strip()

                if inner_section_title.text == "Student Learning Outcomes:":
                    inner_section_title.decompose()
                    Outcome = inner_section.text.strip()

                if inner_section_title.text == "Instructor:":
                    inner_section_title.decompose()
                    Professor = inner_section.text.strip()

                if inner_section_title.text == "Prerequisites:":
                    inner_section_title.decompose()
                    Required_Skills = inner_section.text.strip()

        return Course_Title, Unit_Count, Objective, Outcome, Professor, Required_Skills, Description

    def handler(self):
        html_content = requests.get(self.Department_Page_Url).text
        soup = BeautifulSoup(html_content, 'html.parser')

        departments = soup.find(id='department')

        # get department list with id
        departments_with_id = {}

        li = soup.find('select', {'id': 'department'})
        children = li.findChildren("option", recursive=False)
        for child in children:
            if len(child.contents) > 0:
                departments_with_id[child.text] = child.attrs['value']

        # get department's course

        for department in departments_with_id:

            department_id = departments_with_id[department]
            Department_Name = department

            courses, department_url = self.get_courses_of_department(department_id)

            # get course's data
            for course in courses:
                Course_Title, Unit_Count, Objective, Outcome, Professor, Required_Skills, Description = self.get_course_data(
                    course)

                self.save_course_data(
                    self.University, self.Abbreviation, Department_Name, Course_Title, Unit_Count,
                    Professor, Objective, self.Prerequisite, Required_Skills, Outcome, self.References, self.Scores,
                    Description, self.Projects, self.University_Homepage, Course_Homepage, self.Professor_Homepage
                )

            logger.info(f"{self.Abbreviation}: {Department_Name} department's data was crawled successfully.")

        logger.info(f"{self.Abbreviation}: Total {self.course_count} courses were crawled successfully.")


y = YU()

y.handler()
