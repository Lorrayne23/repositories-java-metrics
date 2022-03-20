import math
import pandas as pd
import requests
from datetime import datetime
from datetime import date
import openpyxl
token = input("Entre com seu token: ")

headers = {"Authorization": f"Bearer {token}"}

def run_query(cursor):
  f_cursor = "null" if cursor is None else "\"" + cursor + "\""
  query = """{
  search(query: "stars:>100", type: REPOSITORY, first: 20, after:""" + f_cursor + """) {
    pageInfo {
        endCursor
        hasNextPage
    } 
    nodes {
      ... on Repository {
        nameWithOwner
        url
        createdAt
        releases {
          totalCount
        }
  }
}
"""
  request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
  if request.status_code == 200:
      return request.json()
  else:
      raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

data = []

def save_file(result):
  print(result)
  results = result["data"]["search"]["nodes"]
  for r in results:
    name = r["nameWithOwner"]
    today = date.today()

    age = (today - created_at).days # Calcula diferença de dias da criação do repositório
    total_releases = r["releases"]["totalCount"]
    primary_language = "None" if r["primaryLanguage"] is None else r["primaryLanguage"]["name"]
    total_pull_requests = r["mergedPullRequests"]["totalCount"]
    today_minutes = datetime.utcnow()
    updated_at =  datetime.strptime(r["updatedAt"], "%Y-%m-%dT%H:%M:%SZ")
    updated_minutes = today_minutes - updated_at
    updated = math.modf(updated_minutes.seconds / 60)[1]
    closed_issues = r["closed"]["totalCount"]
    total_issues = r["total"]["totalCount"]
    data.append([name, age, total_pull_requests, total_releases, updated, primary_language, closed_issues, total_issues])

  columns = ["Name", "Age", "Total Pull Requests", "Total Releases", "Updated", "Primary Language", "Closed Issues", "Total Issues"]
  df = pd.DataFrame(data, columns=columns)
  df.to_excel("repositorios_populares.xlsx")
  df.to_csv("repositorios_populares.csv")

pages = 50
endCursor = None

for page in range(pages):
  result = run_query(endCursor)
  save_file(result)
  has_next = result["data"]["search"]["pageInfo"]["hasNextPage"]
  if not has_next:
      break
  endCursor = result["data"]["search"]["pageInfo"]["endCursor"]

