
#Load the correct library for the 
library(readr)
library(dplyr)
library(ggplot2)

#Load the data

df <- read.csv("stack_overflow_data.csv")


#Check the head data

head(df)

tail(df)
#Question 1: What percentage of the total number of questions asked in 2020 had the R tag?

#Find the data percentage

data_percentage <- df%>%
  mutate(percentage = 100 *( num_questions/year_total))

print(data_percentage)

#Filter R over the times

r_over_time <- data_percentage%>%
  filter(tag == "r")

#Visualize R over time 

plot_r_over_time <- ggplot(r_over_time) + geom_line(aes(x = year, y = percentage))+ggtitle("R prog lang Over time")

#Filter for the year 2020

r_202 <- r_over_time%>%
  filter(year == "2020")

print(r_202)

#Question 2: What were the five most asked-about tags between 2015-2020?

sorted_tag <- df%>%
  filter(year >= 2015)%>%
  group_by(tag)%>%
  summarize(tag_total = sum(num_questions))%>%
  arrange(desc(tag_total))
#Get the five largest tags
# Another way of doing the below is by selecting the column with $: highest_tags <- head(sorted_tags$tag, n = 5)
largest_tag <- sorted_tag%>%
  select(tag)%>%
  head(n = 5)


data_subset <- data_percentage %>% 
  filter(tag %in% largest_tag, year >= 2015)

#Plot tags over time on a line plot using color to represent tag

r_over_time_3 <- data_percentage%>%
  filter(tag == "r", year =="2020")

print(r_over_time_3)


#Now Python over the time

py_over_time <- data_percentage%>%
  filter(tag == "python")


sorted_tag_2 <- df%>%
  filter(year >= 2012)%>%
  group_by(tag)%>%
  summarize(tag_total = sum(num_questions))%>%
  arrange(desc(tag_total))

#Python over the time.
plot_py_over_time <- ggplot(py_over_time) + geom_line(aes(x = year, y = percentage))+ggtitle("Python programming languages Over time")


#CSS over the time

css_over_time <- data_percentage%>%
  filter(tag == "css")

#CSS over the time
plot_css_over_time <- ggplot(css_over_time) + geom_line(aes(x = year, y = percentage))+ggtitle("CSS Over the time")
