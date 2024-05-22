
# CI/CD Pipeline

CI/CD Pipeline for Databricks with branching strategy.



## Deployment

To deploy this project your repo should have three branches:

-development

-staging

-production

One environment (production) configured with the approvers required


## Workflow of Pipeline
To achieve CI/CD on databricks this repo will be linked on databricks through all the three branches:dev,staging and production.

First all the development and testing will be done on development branch.

Once development is done then it will be merge to staging branch and when any one commit any changes through staging branch then it will go for  manual approval through email and as well as github.

Upon successful approval,it will be merged to production branch.
