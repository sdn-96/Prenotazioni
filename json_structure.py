'''
json structure for base retrived data
{
  "type": "base"
  "columns": [
    "Appartamento",
    "Nome",
    "Nazione",
    "Check in",
    "Check out",
    "Notti",
    "Totale pernottamento",
    "Tot proprietario",
    "Netto proprietario",
    ""
  ],
  "rows": [
    [
      "L. BRIENNO",
      "3540/2024",
      "",
      "06/06/2024",
      "13/06/2024",
      "7",
      "€\t\t\t\t\t\t\t\t\t\t611,56",
      "€395,96",
      "€395,96",
      ""
    ],
    [
    ...
    ]   
  ]
}
'''
'''
json structure for base changes data
{
  "type": "change",
  "totali": {
      "Totale pernottamento": "€XXXXX",
      "Tot proprietario": "€XXXXX",
      "Netto proprietario": "€XXXXX"
  },
  "columns": [
    "Change",
    "Appartamento",
    "Nome",
    "Nazione",
    "Check in",
    "Check out",
    "Notti",
    "Totale pernottamento",
    "Tot proprietario",
    "Netto proprietario",
    ""
  ],
  "rows": [
    [
      "added"/"removed"/"modified"
      "L. BRIENNO",
      "3540/2024",
      "",
      "06/06/2024",
      "13/06/2024",
      "7",
      "€\t\t\t\t\t\t\t\t\t\t611,56",
      "€395,96",
      "€395,96",
      ""
    ],
    [
    ...
    ]   
  ]
}
'''
