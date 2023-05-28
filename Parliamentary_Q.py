import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud


driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get('https://sansad.in/ls/questions/questions-and-answers')



ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

dataf=[]   #final dataset
rown= 1    #question number

while True:
    
    # Extract data from the current page
    WebDriverWait(driver, 5,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.CLASS_NAME,"mui-style-1l45qeu"))) 
    table_rows = driver.find_elements(By.CSS_SELECTOR, "table tr")  # Example CSS selector for table rows
    
   
# Process and extract data from rows as needed
    for row in table_rows:
   
   
     cells=row.find_elements(By.CSS_SELECTOR,"td")
     
     cells=cells[1:]
     if len(cells) > 1:
      cells=[cells[5],cells[0],cells[2],cells[3]]  #Cleaning Data for only required fields
     datarow=[rown]
     for cell in cells:
        data = cell.text
        if data=="":
           continue

        datarow.append(data)
     if len(datarow)==1:
        continue 
     dataf.append(datarow)
     rown=rown+1
     
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mainContent"]/div/div[1]/main/div/div[2]/div/div[2]/div/div/div/div[2]/div[4]/nav/ul/li[10]/button'))).click() 
    #locating and clicking the next buttton and waiting for the next page to reload 
    next_button=driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div[1]/main/div/div[2]/div/div[2]/div/div/div/div[2]/div[4]/nav/ul/li[10]/button') #storing the next button element
    if not next_button.is_enabled():   #checking if next_button is disabled and thus exiting the loop
       break
    
       
csv_file = "parliamentary_questions.csv"    #filename

# Write the data to the CSV file
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        ["Q.No.","Date","Text", "Asking Member", "Addressed Ministry"])   #column-headers
    writer.writerows(dataf)

print("Scraping complete.")

# Reading the CSV file into a pandas DataFrame
df = pd.read_csv('parliamentary_questions.csv')


#Conducting Data Analysis on collected info

# Calculating the number of questions asked by each member
member_counts = df['Asking Member'].value_counts()
print("Number of questions asked by each member:")
print(member_counts)

# Calculating the number of questions asked by each ministry
ministry_counts = df['Addressed Ministry'].value_counts()
print("Number of questions asked by each ministry:")
print(ministry_counts)

# Calculate the average length of questions
df['Question Length'] = df['Text'].str.len()
average_question_length = df['Question Length'].mean()
print("\nAverage length of questions:")
print(average_question_length)

#Identifying the top asking members based on the number of questions asked
top_asking_members = member_counts.head(10)  # Change the number to display more or fewer members
print("Top Asking Members:")
print(top_asking_members)

# Calculating the distribution of questions over time (by year)
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
question_count_by_year = df['Year'].value_counts().sort_index()
print("Distribution of questions by year:")
print(question_count_by_year)

# Calculating the distribution of questions over time (by month)
df['Month'] = df['Date'].dt.month_name()
question_count_by_month = df['Month'].value_counts().sort_index()
print("Distribution of questions by month:")
print(question_count_by_month)

#Calculating descriptive statistics for question length
question_lengths = df['Text'].str.len()  # Assuming 'Text' is the column containing the question text
question_stats = question_lengths.describe()
print("Question Length Statistics:")
print(question_stats)

# Calculating descriptive statistics for member frequency
member_counts = df['Asking Member'].value_counts()  # Assuming 'Asking Member' is the column containing member names
member_stats = member_counts.describe()
print("Member Frequency Statistics:")
print(member_stats)

#Identifying the most probable keywords used in the questions
# Creating a CountVectorizer object
vectorizer = CountVectorizer(stop_words='english')
# Fit and transform the question text to obtain the word counts
word_counts = vectorizer.fit_transform(df['Text'])
# Get the most probable keywords and their frequencies
keywords = vectorizer.get_feature_names_out()
keyword_frequencies = word_counts.sum(axis=0)
# Creating a dictionary of keywords and their frequencies
keyword_dict = dict(zip(keywords, keyword_frequencies.A1))
# Sorting the keywords based on frequency in descending order
sorted_keywords = sorted(keyword_dict.items(), key=lambda x: x[1], reverse=True)
# Printing the top 10 most probable keywords
print("Top 10 Most Probable Keywords in Questions:")
for keyword, frequency in sorted_keywords[:10]:
    print(keyword, "-", frequency)

# WordCloud
all_questions = ' '.join(df['Text'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_questions)
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Most Frequent Words in Questions')
plt.show()    

# Plotting the number of questions by member
plt.figure(figsize=(12, 6))
member_counts.plot(kind='bar', color='skyblue')
plt.xlabel('Member')
plt.ylabel('Number of Questions')
plt.title('Number of Questions Asked by Each Member')
plt.xticks(rotation=45)
plt.show()

# Plotting the number of questions by ministry
plt.figure(figsize=(12, 6))
ministry_counts.plot(kind='bar', color='lightgreen')
plt.xlabel('Ministry')
plt.ylabel('Number of Questions')
plt.title('Number of Questions Asked by Each Ministry')
plt.xticks(rotation=45)
plt.show()

# Plotting the distribution of questions over time (by year)
plt.figure(figsize=(12, 6))
question_count_by_year.plot(kind='bar', color='orange')
plt.xlabel('Year')
plt.ylabel('Number of Questions')
plt.title('Distribution of Questions by Year')
plt.xticks(rotation=45)
plt.show()

# Plotting the distribution of questions over time (by month)
plt.figure(figsize=(12, 6))
question_count_by_month.plot(kind='bar', color='purple')
plt.xlabel('Month')
plt.ylabel('Number of Questions')
plt.title('Distribution of Questions by Month')
plt.xticks(rotation=45)
plt.show()

#Plotting the distribution of question word counts
plt.figure(figsize=(10, 6))
plt.hist(df['Text'].apply(lambda x: len(x.split())), bins=20)
plt.xlabel('Word Count')
plt.ylabel('Number of Questions')
plt.title('Distribution of Question Word Counts')
plt.show()