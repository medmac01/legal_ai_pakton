// Define available questions
export const availableQuestions = [
  {
    id: 'EmotionsQuestion',
    title: 'Question 1',
    description: 'If an application recognizes the emotions of a natural person, how is it classified according to the Regulation?',
    filePath: `${process.env.PUBLIC_URL}/data/human_evaluation/EmotionsQuestion.csv`,
    responseLink: 'https://docs.google.com/spreadsheets/d/1RI_e-lqhbTVh_q1ag_UmURSM7cUTzd8vjNNCCONyDBU/edit?usp=sharing',
    paktonResponse: 'https://pakton.site/examples/?num=8',
    gptResponse: 'https://drive.google.com/file/d/1SP1DOTo1FwMKOVlrlaxCXcRD0uS4Mm6f/view?usp=sharing'
  },
  {
    id: 'ComplaintsQuestion',
    title: 'Question 2',
    description: 'Who has the right to lodge a complaint according to the Regulation?',
    filePath: `${process.env.PUBLIC_URL}/data/human_evaluation/ComplaintsQuestion.csv`,
    responseLink: 'https://docs.google.com/spreadsheets/d/1NlaMYkKm-6WOPHU-KP_aY9GYVwAsLgoJRJFob0oZmLA/edit?usp=sharing',
    paktonResponse: 'https://pakton.site/examples/?num=11',
    gptResponse: 'https://drive.google.com/file/d/1Pc9WDbAuFXbyAUc1bGHQsMrq6jTWvgTE/view?usp=drive_link'
  },
  {
    id: 'ObligationsQuestion',
    title: 'Question 3',
    description: 'What are the obligations for providers for general-purpose AI models?',
    filePath: `${process.env.PUBLIC_URL}/data/human_evaluation/ObligationsQuestion.csv`,
    responseLink: 'https://docs.google.com/spreadsheets/d/1wZqP5mkPL765xgb9eKphIOKtSBatVYNZ3Y7Cjdt5GFg/edit?usp=sharing',
    paktonResponse: 'https://pakton.site/examples/?num=9',
    gptResponse: 'https://drive.google.com/file/d/1rh9yfKyH6wKT67951A648LP0DRU6Chyp/view?usp=sharing'
  },
  {
    id: 'ScopeQuestion',
    title: 'Question 4',
    description: 'What is the Scope of the Regulation?',
    filePath: `${process.env.PUBLIC_URL}/data/human_evaluation/ScopeQuestion.csv`,
    responseLink: 'https://docs.google.com/spreadsheets/d/1Vs5X-YQ1VuWnq_3JYKv4uKKbRc0VYpC7OnOnik_23j4/edit?usp=sharing',
    paktonResponse: 'https://pakton.site/examples/?num=1',
    gptResponse: 'https://drive.google.com/file/d/1Ju_X3tvYPl2ATjyUvh7ERRU2Qu_3ESuG/view?usp=sharing'
  },
  {
    id: 'RiskArticlesQuestion',
    title: 'Question 5',
    description: 'Which articles regulate the high-risk use of AI?',
    filePath: `${process.env.PUBLIC_URL}/data/human_evaluation/RiskArticlesQuestion.csv`,
    responseLink: 'https://docs.google.com/spreadsheets/d/1G3ZLNFEapEsIfebEIZFNd3__TAaQ68Fok_7lhCMEHSw/edit?usp=sharing',
    paktonResponse: 'https://pakton.site/examples/?num=5',
    gptResponse: 'https://drive.google.com/file/d/1FDN2rp4pPCpJQdUrA-Ej8mb6-itP8oCH/view?usp=sharing'
  },
  {
    id: 'AIdefinitionQuestion',
    title: 'Question 6',
    description: 'What is the definition of an "AI system"?',
    filePath: `${process.env.PUBLIC_URL}/data/human_evaluation/AIdefinitionQuestion.csv`,
    responseLink: 'https://docs.google.com/spreadsheets/d/1goclG-Zdhp6-0DXR38JBaZID7RoIFEK3nWx5uvD8pC0/edit?usp=sharing',
    paktonResponse: 'https://pakton.site/examples/?num=2',
    gptResponse: 'https://drive.google.com/file/d/18e7Wz5rkWg5XjvhAYpURZlRqd7CnZsKJ/view?usp=sharing'
  }
];