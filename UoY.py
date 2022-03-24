from BaseCrawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger('__main__')


class UoY(BaseCrawler):
    Department_Page_Url = "https://www.york.ac.uk/students/studying/manage/programmes/module-catalogue/module"
    University = "University of York"
    Abbreviation = "UoY"
    University_Homepage = "https://www.york.ac.uk/"

    # Below fields didn't find in the website
    Scores = None
    Projects = None
    Professor = None
    Professor_Homepage = None
    Required_Skills = None

    def get_courses_of_department(self, department_id):

        academic_year = "2021-22"

        department_url = self.Department_Page_Url + "?query=&department=" + department_id + "&year=" + academic_year

        department_course_len = self.get_courseList_len(department_url)

        department_url += "&max=" + str(department_course_len) + "&offset=0"

        department_page_content = requests.get(department_url).text
        department_soup = BeautifulSoup(department_page_content, 'html.parser')

        courses_module = department_soup.find("table", {"id": "modules"})

        if courses_module is not None:
            courses = courses_module.find_all("tr")
            # remove table header
            courses.pop(0)
            return courses, department_url

        return None, ""

    def get_courseList_len(self, department_url):

        department_page_content = requests.get(department_url).text
        department_soup = BeautifulSoup(department_page_content, 'html.parser')

        department_records_len = department_soup.find('div', {'class': 'pagination'}).find_all('a', {'class': 'step'})[
            -1].text

        return int(department_records_len) * 10

    def get_course_data(self, course):
        page_title = course.find(id="mdcolumn").find('h1').text
        Course_Title = page_title
        # Course_Title = page_title.rpartition(' - ')[0]

        Unit_Count = course.find('strong',text='Credit value').next_sibling.text
        Unit_Count = Unit_Count.split(' ')[1]


        course_sections = course.find(id='mdcolumn').find_all('h2')

        Prerequisite = None
        pre_list = course.find('h3', text='Pre-requisite modules')
        if pre_list is not None:
            Prerequisite = pre_list.next_sibling.next_sibling.get_text().strip()

        Description = ''
        Objective = ''
        Outcome = ''
        References = ''

        for section in course_sections:

            if section.text == "Module summary":
                summary = course.find('h2', text='Module summary')
                if summary is not None:
                    Description = self.remove_extra_newlines(summary.next_sibling.next_sibling.text)
            
            elif section.text == "Module content":
                content = course.find('h2', text='Module content')
                if content is not None:
                    Description += '\n' + self.remove_extra_newlines(content.next_sibling.next_sibling.get_text())

            elif section.text == "Module aims":
                sub_aim = section.next_sibling.next_sibling.get_text()
                Objective = self.remove_extra_newlines(sub_aim).strip()

            elif section.text == "Module learning outcomes":
                sub_outcome = section.next_sibling.next_sibling.get_text()
                Outcome = self.remove_extra_newlines(sub_outcome).strip()

            if section.text == "Indicative reading":
                References = section.next_sibling.next_sibling.get_text()

        return Course_Title, Unit_Count, Objective, Outcome, Prerequisite, Description, References

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
        for Department_Name in departments_with_id:
            # department = 'Computer Science'
            department_id = departments_with_id[Department_Name]

            courses, department_url = self.get_courses_of_department(department_id)
            if courses is not None:
                # get course's data
                for course in courses:
                    Course_Homepage = self.University_Homepage + course.find_all("a", href=True)[0]['href'][1:]
                    course_page_content = requests.get(Course_Homepage).text
                    course_soup = BeautifulSoup(course_page_content, 'html.parser')
                    Course_Title, Unit_Count, Objective, Outcome, Prerequisite, Description, References = \
                        self.get_course_data(course_soup)

                    self.save_course_data(
                        self.University, self.Abbreviation, Department_Name, Course_Title, Unit_Count,
                        self.Professor, Objective, Prerequisite, self.Required_Skills, Outcome, References, self.Scores,
                        Description, self.Projects, self.University_Homepage, Course_Homepage, self.Professor_Homepage
                    )
                    if self.course_count % 10 == 0:
                        print(self.course_count)

            print(f"{self.Abbreviation}: {Department_Name} department's data was crawled successfully.")

        print(f"{self.Abbreviation}: Total {self.course_count} courses were crawled successfully.")

    def remove_extra_newlines(self, str):
        cleaned_str = str
        while '\n\n' in cleaned_str:
            cleaned_str = cleaned_str.replace("\n\n", "\n")
        return cleaned_str


y = UoY()
y.handler()
