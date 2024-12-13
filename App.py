import streamlit as st
import nltk
import spacy
from streamlit_tags import st_tags
import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
import io, random
import plotly.express as px
from Courses import ds_course, web_course, android_course, ios_course, uiux_course,marketing_course,finance_course,hr_course,healthcare_course,education_course,law_course,engineering_course,sales_course,design_course,construction_course
from pymongo import MongoClient
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
nltk.download('stopwords')
nltk.download('punkt')
nlp=spacy.load("en_core_web_sm")

def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("Courses & Certificates Recommendations")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


client = MongoClient("mongodb+srv://rapanchalk:rapanchalk@cluster0.isp47ql.mongodb.net/") 
db = client.resume_parser

def insert_feedback(feed_name, feed_email, feed_score, comments, timestamp):
    # Reference to the MongoDB collection
    f_collection = db.user_feedback
    
    # Create the document to be inserted
    feedback_document = {
        "name": feed_name,
        "email": feed_email,
        "resume_score": str(feed_score),  # Convert to string if needed
        "timestamp": timestamp,  # Ensure timestamp is in the correct format
        "comments": comments,
        "feed_score": feed_score
    }
    f_collection.insert_one(feedback_document)
    print("Feedback inserted successfully!")

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    collection = db.user_data
    document = {
        "name": name,
        "email": email,
        "resume_score": str(res_score),
        "timestamp": timestamp,
        "page_no": str(no_of_pages),
        "predicted_field": reco_field,
        "user_level": cand_level,
        "actual_skills": skills,
        "recommended_skills": recommended_skills,
        "recommended_courses": courses
    }
st.set_page_config(
    page_title="Job Portal with AI Resume Analyser",
)

def run():
    # Custom CSS
    st.markdown("""
        <style>
            .title {
                font-size: 40px;
                color: #2C3E50;
                text-align: center;
                font-weight: bold;
                margin-bottom: 40px;
            }
            
            .header {
                color: #2980B9;
                font-size: 30px;
                font-weight: bold;
            }
            
            .subheader {
                color: #3498DB;
                font-size: 22px;
                font-weight: bold;
            }
            
            .success-message {
                color: green;
                font-weight: bold;
            }
            
            .warning-message {
                color: orange;
                font-weight: bold;
            }
            
            .error-message {
                color: red;
                font-weight: bold;
            }

            .resume-tip {
                font-size: 18px;
                color: #8E44AD;
                text-align: justify;
                margin-bottom: 20px;
            }

            .resume-score {
                font-size: 20px;
                color: #E74C3C;
                font-weight: bold;
            }

            .select-box {
                border: 1px solid #2980B9;
                border-radius: 10px;
                padding: 10px;
            }

            .progress-bar {
                background-color: #27AE60;
                height: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    type = ["Job Seeker", "Admin", "Feedback", "View Feedback"]
    choice = st.selectbox("Choose user type from the given options:", type)

    st.markdown('<div class="title">AI Resume Analyser</div>', unsafe_allow_html=True)

    if choice == 'Job Seeker':
        pdf_file = st.file_uploader("Upload your Resume", type=["pdf"])
        
        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()

            if resume_data:
                resume_text = pdf_reader(save_image_path)

                st.markdown('<div class="header">Resume Analysis</div>', unsafe_allow_html=True)
                st.markdown('<div class="success-message">Hello ' + resume_data['name'] + '</div>', unsafe_allow_html=True)
                st.markdown('<div class="subheader">Your Basic Info</div>', unsafe_allow_html=True)
                
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass

                cand_level = ''
                if resume_data['no_of_pages'] == 0:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 1:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 2:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''', unsafe_allow_html=True)

                st.subheader("Skills Recommendation")
                keywords = st_tags(label='##### Skills that you have', value=resume_data['skills'])


                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy','Java','Android SDK','Android Studio','Emulator','Version Control',' APIs and Databases']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode','Objective-C','iOS SDK','Instruments','Alamofire']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                # 2. Marketing
                marketing_keyword = ['seo', 'content marketing', 'email marketing', 'social media marketing', 
                     'ppc', 'brand management', 'market research', 'google analytics', 
                     'copywriting', 'customer segmentation']

                # 3. Finance
                finance_keyword = ['financial modeling', 'corporate finance', 'investment analysis', 
                                'portfolio management', 'risk management', 'budgeting', 'accounting', 
                                'financial planning', 'taxation', 'auditing', 'financial reporting']

                # 4. Human Resources (HR)
                hr_keyword = ['recruitment', 'performance management', 'employee relations', 'training and development', 
                            'hr policies', 'compensation and benefits', 'workforce planning', 'conflict resolution', 
                            'hr analytics', 'talent acquisition']

                # 5. Healthcare
                healthcare_keyword = ['clinical research', 'patient care', 'healthcare administration', 
                                    'public health', 'healthcare management', 'medical billing', 
                                    'health informatics', 'electronic medical records', 'healthcare compliance']

                # 6. Education
                education_keyword = ['curriculum development', 'lesson planning', 'classroom management', 
                                    'student assessment', 'educational technology', 'instructional design', 
                                    'e-learning', 'special education', 'pedagogy', 'early childhood education']

                # 7. Law
                law_keyword = ['legal research', 'contract law', 'litigation', 'compliance', 'intellectual property', 
                            'negotiation', 'corporate law', 'dispute resolution', 'employment law', 
                            'legal writing', 'civil litigation']

                # 8. Engineering
                engineering_keyword = ['mechanical engineering', 'electrical engineering', 'civil engineering', 
                                    'project management', 'autocad', 'solidworks', 'matlab', 'fea', 
                                    'cad modeling', 'engineering design', 'manufacturing']

                # 9. Sales
                sales_keyword = ['lead generation', 'negotiation', 'account management', 'b2b sales', 
                                'crm', 'sales forecasting', 'cold calling', 'closing deals', 'territory management']

                # 10. Graphic Design
                design_keyword = ['photoshop', 'illustrator', 'indesign', 'typography', 'branding', 
                                'ui/ux design', 'motion graphics', 'sketch', 'figma', 'layout design', 
                                'prototyping', 'wireframing']

                # 11. Construction Management
                construction_keyword = ['project planning', 'cost estimation', 'construction safety', 
                                        'blueprint reading', 'contract management', 'scheduling', 'risk management', 
                                        'quality control', 'building codes', 'construction materials']
                
                
                reco_field = ''
                rec_course = ''

                for i in resume_data['skills']:
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("Our analysis says you are looking for Data Science Jobs.")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                              'Streamlit']
                        recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills['skills'], key='2')
                        st.warning("Note: Adding this skills to resume will boost the chances of getting a Job")
                        rec_course = course_recommender(ds_course)
                        break

                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("Our analysis says you are looking for Web Development Jobs")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='3')
                        st.warning("Note: Adding this skills to resume will boost the chances of getting a Job")
                        rec_course = course_recommender(web_course)
                        break

                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("Our analysis says you are looking for Android App Development Jobs")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='4')
                        st.warning("Note: Adding this skills to resume will boost the chances of getting a Job")
                        rec_course = course_recommender(android_course)
                        break

                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("Our analysis says you are looking for IOS App Development Jobs")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='5')
                        st.warning("Note: Adding this skills to resume will boost the chances of getting a Job")
                        rec_course = course_recommender(ios_course)
                        break

                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("Our analysis says you are looking for UI-UX Development Jobs")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
                        recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='6')
                        st.warning("Note: Adding this skills to resume will boost the chances of getting a Job")
                        rec_course = course_recommender(uiux_course)

                        break

                        # 1. Marketing
                    elif i.lower() in marketing_keyword:
                            print(i.lower())
                            reco_field = 'Marketing'
                            st.success("Our analysis says you are looking for Marketing Jobs.")
                            recommended_skills = ['SEO', 'Content Marketing', 'Email Marketing', 'Social Media Marketing',
                                                'PPC', 'Market Research', 'Brand Management', 'Copywriting', 'Google Analytics',
                                                'Customer Segmentation', 'CRM Tools', 'Influencer Marketing']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='7')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(marketing_course)
                            break

                        # 2. Finance
                    elif i.lower() in finance_keyword:
                            print(i.lower())
                            reco_field = 'Finance'
                            st.success("Our analysis says you are looking for Finance Jobs.")
                            recommended_skills = ['Financial Modeling', 'Risk Management', 'Corporate Finance',
                                                'Investment Analysis', 'Portfolio Management', 'Financial Planning',
                                                'Data Analysis', 'Accounting', 'Budgeting', 'Taxation', 'Auditing',
                                                'Financial Reporting']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='8')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(finance_course)
                            break

                        # 3. Human Resources
                    elif i.lower() in hr_keyword:
                            print(i.lower())
                            reco_field = 'Human Resources'
                            st.success("Our analysis says you are looking for Human Resources Jobs.")
                            recommended_skills = ['Recruitment', 'Employee Relations', 'Performance Management',
                                                'HR Policies', 'Training & Development', 'Conflict Resolution',
                                                'Compensation & Benefits', 'Workforce Planning', 'Talent Acquisition',
                                                'HR Analytics', 'Labor Laws']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='9')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(hr_course)
                            break

                        # 4. Healthcare
                    elif i.lower() in healthcare_keyword:
                            print(i.lower())
                            reco_field = 'Healthcare'
                            st.success("Our analysis says you are looking for Healthcare Jobs.")
                            recommended_skills = ['Clinical Research', 'Patient Care', 'Healthcare Administration',
                                                'Public Health', 'Medical Terminology', 'Healthcare Management',
                                                'Electronic Medical Records (EMR)', 'Healthcare Compliance',
                                                'Medical Billing', 'Health Informatics']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='10')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(healthcare_course)
                            break

                        # 5. Education
                    elif i.lower() in education_keyword:
                            print(i.lower())
                            reco_field = 'Education'
                            st.success("Our analysis says you are looking for Education Jobs.")
                            recommended_skills = ['Curriculum Development', 'Lesson Planning', 'Classroom Management',
                                                'Student Assessment', 'Educational Technology', 'Special Education',
                                                'Instructional Design', 'E-Learning', 'Pedagogy', 'Behavior Management',
                                                'Early Childhood Education']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='11')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(education_course)
                            break

                        # 6. Law
                    elif i.lower() in law_keyword:
                            print(i.lower())
                            reco_field = 'Law'
                            st.success("Our analysis says you are looking for Law Jobs.")
                            recommended_skills = ['Legal Research', 'Contract Law', 'Litigation', 'Legal Writing',
                                                'Compliance', 'Intellectual Property', 'Negotiation', 'Corporate Law',
                                                'Dispute Resolution', 'Civil Litigation', 'Employment Law']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='12')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(law_course)
                            break

                        # 7. Engineering
                    elif i.lower() in engineering_keyword:
                            print(i.lower())
                            reco_field = 'Engineering'
                            st.success("Our analysis says you are looking for Engineering Jobs.")
                            recommended_skills = ['Mechanical Engineering','Automobile Engineering', 'Electrical Engineering', 'Civil Engineering',
                                                'Project Management', 'AutoCAD', 'SolidWorks', 'MATLAB',
                                                'Engineering Design', 'FEA', 'CAD Modeling', 'Manufacturing']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='13')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(engineering_course)
                            break   

                        # 8. Sales
                    elif i.lower() in sales_keyword:
                            print(i.lower())
                            reco_field = 'Sales'
                            st.success("Our analysis says you are looking for Sales Jobs.")
                            recommended_skills = ['Negotiation', 'Lead Generation', 'Account Management', 'B2B Sales',
                                                'Customer Relationship Management (CRM)', 'Sales Forecasting',
                                                'Cold Calling', 'Closing Deals', 'Client Relations', 'Territory Management']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='14')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(sales_course)
                            break

                        # 9. Graphic Design
                    elif i.lower() in design_keyword:
                            print(i.lower())
                            reco_field = 'Graphic Design'
                            st.success("Our analysis says you are looking for Graphic Design Jobs.")
                            recommended_skills = ['Adobe Photoshop', 'Illustrator', 'InDesign', 'Typography', 'Branding',
                                                'Layout Design', 'UI/UX Design', 'Motion Graphics', 'Prototyping', 'Wireframing',
                                                'Sketch', 'Figma']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='15')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(design_course)
                            break

                        # 10. Construction Management
                    elif i.lower() in construction_keyword:
                            print(i.lower())
                            reco_field = 'Construction Management'
                            st.success("Our analysis says you are looking for Construction Management Jobs.")
                            recommended_skills = ['Project Planning', 'Risk Management', 'Cost Estimation',
                                                'Construction Safety', 'Blueprint Reading', 'Scheduling',
                                                'Contract Management', 'Quality Control', 'Building Codes',
                                                'Construction Materials']
                            recommended_keywords = st_tags(label='##### Recommended to improve your skills',
                                                        text='Recommended skills generated from System',
                                                        value=recommended_skills, key='16')
                            st.warning("Note: Adding these skills to resume will boost the chances of getting a Job")
                            rec_course = course_recommender(construction_course)
                            break

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                st.subheader("Resume Tips & Ideas")
                resume_score = 0
                if 'Objective' or 'Summary' in resume_text:
                    resume_score = resume_score+6
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                if 'Education' or 'School' or 'College'  in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'INTERNSHIPS'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIP'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internships'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                elif 'Internship'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'SKILLS'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'SKILL'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skills'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                elif 'Skill'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                if 'HOBBIES' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                elif 'Hobbies' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'INTERESTS'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                elif 'Interests'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Interest. It will show your interest other that job.</h4>''',unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                elif 'Achievements' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certifications' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                elif 'Certification' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                if 'PROJECTS' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'PROJECT' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Projects' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                elif 'Project' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<h5 style='text-align: left; color: green;text-align: justify;'>+ Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: red;text-align: justify;'>- Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                st.subheader("Resume Score")
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    my_bar.progress(percent_complete + 1)
                st.success(' Your Resume Writing Score: ' + str(score) + ' out of 100')
                st.warning(
                    "Note: This score is calculated based on the content that you have added in your Resume.")

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                            str(recommended_skills), str(rec_course))

            else:
                st.error('Something went wrong..')

    if choice == 'Admin':
        
        st.success('Welcome to Admin Side')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'admin' and ad_password == 'admin':
                st.success("Welcome Admin")
                collection = db.user_data
                data = list(collection.find())
                df = pd.DataFrame(data)
                df['_id'] = df['_id'].astype(str)
                df.columns = ['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                  'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                  'Recommended Course']

                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)

                st.subheader("Pie-Chart for Resume Score")
                fig = px.pie(df, names='Resume Score', title='Resume Score From 1 to 100', hole=.3)
                st.plotly_chart(fig)

                st.subheader("Pie-Chart for User's Experience Level")
                fig = px.pie(df, names='User Level', title="Pie-Chart for User's Experienced Level", hole=.3)
                st.plotly_chart(fig)

                st.subheader("Pie-Chart for Predicted Field")
                fig = px.pie(df, names='Predicted Field', title='Predicted Field according to the Skills', hole=.3)
                st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")

    if choice == 'Feedback':
        # Timestamp
        ts = datetime.datetime.now()
        timestamp = ts.strftime('%Y-%m-%d_%H:%M:%S')

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                insert_feedback(feed_name, feed_email, feed_score, comments, timestamp)
                st.success("Thanks! Your Feedback was recorded.")

    elif choice == 'View Feedback':
        f_collection = db.user_feedback
        # Query to fetch data from MongoDB
        feedback_data = list(f_collection.find({}))
        if feedback_data:
            # Convert to DataFrame
            plotfeed_data = pd.DataFrame(feedback_data)
            
            # Process feed_score data
            labels = plotfeed_data['feed_score'].astype(str).unique()
            values = plotfeed_data['feed_score'].astype(str).value_counts()

            # Plotting pie chart for user ratings
            st.subheader("**Past User Ratings**")
            fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
            st.plotly_chart(fig)
        else:
            st.write("No feedback data available.")
            

run()