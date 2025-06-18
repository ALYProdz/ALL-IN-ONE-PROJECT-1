df <- read.csv("netflix_data.csv")
#Print all the action movies.

#1 _ take a subset of all the movies from the data

netflix_movie_types <- df%>%
  filter(type =="Movie")

#Take a subset of the movies in 1990 years.

movies_re_1990 <- netflix_movie_types%>%
  filter((release_year>=1990)&(release_year)<2000)%>%
  arrange(desc(release_year))
movies_re_1990_dur <- movies_re_1990%>%
  select(duration)

#Take action movies only
action_movie_90 <- movies_re_1990%>%
  filter(genre =="Action")%>%
  group_by(country)%>%
  arrange(desc(country))
