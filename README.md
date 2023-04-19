## A data processing and augmentation project

🤖 Part 2 of [Explorer AI](https://github.com/kristenvonbecker/Explorer_AI)

---

This repo contains a framework for cleaning and enhancing text data scraped from 
[exploratorium.edu](https://www.exploratorium.edu), the official website of the Exploratorium, a science museum 
located in San Francisco, CA. The raw text data used in this project was aquiried in 
[scrapy_project](https://github.com/kristenvonbecker/scrapy_project); please see that repo for details about the raw 
data. The goal of the present project is to transform the raw data into a (comprehensive) knowledgebase centered around 
the Exploratorium's exhibits. There are two main objectives:

1. Build a database containing information about each the Exploratorium's 
[exhibits](https://www.exploratorium.edu/exhibits) and [galleries](https://www.exploratorium.edu/visit/galleries).
This database includes the following text fields:

   - Exhibits:
     - `id` is unique identifier for the exhibit
     - `title` is the exhibit's official title
     - `aliases` gives a list of alternate exhibit titles, if any
     - `tagline` is a catchy short description of the exhibt, taken from raw data
     - `location` gives the (current) location of the exhibit (e.g. gallery) within the museum, or indicates that the
exhibit is not currently on view
     - `creators` is a list of the exhibit creators' names, obtained via raw data and AI
     - `year` gives the year the exhibit first opened at the museum, obtained via raw data and AI
     - `keywords` gives a list of keywords for the exhibit, sourced from both raw data and AI
     - `fun-facts` is an AI-generated list of fun facts about the exhibit
     - `summary` is an AI-generated summary of the exhibit, based on its description in the raw data
     - `collections` gives a list of collections (i.e. groupings of exhibits, based on some theme) that the exhibit 
belongs to, if any
     - `related-exhibits` is a list of IDs for related exhibits, if any
     
   - Galleries:
     - `id` is the unique identifier of the gallery
     - `title` is the gallery's full title
     - `tagline` is a (catchy) short description of the gallery, taken from raw data
     - `description` gives a longer description of the gallery, taken from raw data
     - `curator-statement` is a statement by the curators about the gallery
     - `summary` is an AI-generated summary of the gallery, based on its online description
     - `keywords` is an AI-generated list of keywords about the gallery
     - `fun-facts` is an AI-generated list of fun facts about the gallery

    The AI-generated fields listed above were obtained from pre-trained language models available through Google's 
Cloud Natural Language API (specifically, the `analyze_entities` endpoint of 
[language.v1](https://cloud.google.com/natural-language/docs/reference/rpc/google.cloud.language.v1)) and Open AI's 
[GPT-3](https://platform.openai.com/docs/models/gpt-3) API (in particular, the `completion` endpoint using the Davinci 
model). 
     
2. Gather information about the concepts and phenomena which are illustrated by each of the Exploratorium's exhibits.
This data is composed of (full text content of) Encyclopedia Britannica articles with titles related to exhibit keywords. 
The articles are obtained through the [Encyclopedia Britannica API](https://encyclopaediaapi.com/).
