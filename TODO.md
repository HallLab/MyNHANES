# TODO List

## High Priority

- [ ] Present the system to the team
- [ ] Determine who is interested in participating in the project and paper
- [ ] Decide whether to apply for the Grant and establish a timeline
- [ ] Develop the paper
- [ ] Improve TAGs
    Demographics – for variables like age, gender, race, and ethnicity.
    Lifestyle – to classify variables related to diet, exercise, alcohol consumption, and smoking.
    Clinical Outcomes – for health outcomes such as diagnosed diseases or conditions.
    Medications – for variables tracking drug use.
    Biomarkers – to tag biological measures like cholesterol, glucose, or hormone levels.
    Symptoms – for tracking reported health symptoms.
    Environmental – for variables related to environmental exposures like pollutants or chemicals.

## Medium Priority

- [ ] Create backend tests
- [ ] Develop new transformation rules
- [ ] Improve the query mechanism
- [ ] Enhance documentation

## Low Priority

- [ ] Design new HTML interfaces
- [ ] Implement QueryTable and visualizations
- [ ] Improve the transformations interface and develop a testing process


## Other
kill -9 $(lsof -t -i:8000)

## to the paper:
- Tagging System: Present the types of tags (e.g., Exposures, Demographics, Clinical Outcomes) and the number of variables classified under each.
- Transformation Rules: Demonstrate the application of 3-5 transformation rules, showcasing flexibility.
- Master Data Loading: Show the time taken to load datasets and the required disk space.
- Query Performance: Measure and display query response times.
- Scalability: Highlight the transition from SQLite to PostgreSQL for larger datasets.
- Version Control: Demonstrate reproducibility with version-controlled transformation rules.
- Custom Rule Creation: Showcase user-generated rules.
- Visualization: Explore visualizations for normalized data.