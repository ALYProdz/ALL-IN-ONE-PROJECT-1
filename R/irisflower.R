#Load libraris
library(tidyverse)
library(dplyr)
library(datasets)
#Load the data
iris_data <- iris
#Turn the data into a datafram

df <-as.data.frame(iris_data)
#Rename the data columns

df <- df%>%
  rename("Sep_Len" = "Sepal.Length", "Sep_Wid"= "Sepal.Width", "Pet_L"= "Petal.Length", "Pet_Wid"="Petal.Width")

#Head

#Inspect the Data
head(df, n = 10)
#Str data
str(df)
#Glimpse Data
glimpse(df)
#Col namea

colnames(df)
#Summary Data
summary(df)

#Sum of sepal length
sum_sep_len <- df%>%
  summarize(sum_s = sum(df$Sep_Len))
#Value counts of sepal length
Val_count_sep_l <- df%>%
  count(Sep_Len)%>%
  arrange(desc(n))

#Sum of sepal width

sum_sep_wid <- df%>%
  summarize(sum_s = sum(df$Sep_Wid))
#Value count sepa width 

Val_count_sep_w <- df%>%
  count(Sep_Wid)%>%
  arrange(desc(n))

#Sum petal width

sum_pet_wid <- df%>%
  summarize(sum_s = sum(df$Pet_Wid))

#value count of petal width
Val_count_pet_w <- df%>%
  count(Pet_Wid)%>%
  arrange(desc(n))


#Sum of petal length

sum_pet_l <- df%>%
  summarize(sum_s = sum(df$Pet_L))

#Value count of petal width

Val_count_pet_l <- df%>%
  count(Pet_L)%>%
  arrange(desc(n))


#Visualize

#Correlation bwteen sepal length and sepal widt 
seplysepw <- ggplot(df, aes(x = Sep_Len, y = Sep_Wid, color =Species))+geom_point()+ggtitle("Corelation between sepal lenght and sepal width")

#Correlation bwteen petal length and petal width 
petalypetalw <- ggplot(df, aes(x = Pet_L, y = Pet_Wid, color =Species))+geom_point()+ggtitle("Corelation between petal lenght and petal width")

#Histogram sepal length and sepal width 

hist_sepal <- ggplot(df, aes(x = Sep_Len, color = Species))+geom_histogram( bins = 30)+ggtitle("Distribution of Sepal Length")

