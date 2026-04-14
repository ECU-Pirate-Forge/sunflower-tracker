# Code Review Structure
The purpose of this README file is to act as a guildeline and define the specific instructions necessary to ensure all members of the Sunflower Tracker group are responsibly and accurately committing, pushing, and merging their code and branches as specified and explained during previous developer meetings.

---

## Main Branch vs Dev Branch
For this project, we are following the standard workflow of having a development branch (called "_dev_" in our repository) alongside our main branch. For Sunflower Tracker, the main branch will represent the latest, stable build that is ready to be seen by others outside of the development team. In layman's terms, this is the public build that would be available to consumers. The dev branch is meant to hold the latest changes that we plan to push into the main branch. Using the dev branch, we can run extensive tests to ensure that the code merged from other branches are working as intended, and ensure that we have had enough reviewers go through the code and sign off on the changes and additions being acceptable to merge into main.

To ensure that all tasks are being done without overwriting each other's code, our work will be performed in other feature branches created by the development team for whatever task we are working on in relation to what is in our backlog. Under <u>__NO__</u> circumstances should we be pushing changes directly into the main branch.

---

## Conducting Proper Work & Code Review
Each item in the product backlog will have a user story and an acceptance criteria. A user story is used to describe the overall expectations of what a potential consumer would expect from this feature. An acceptance criteria is a checklist of specific requirements for a feature that need to be prioritized and completed before the item in the backlog can be reviewed and finished. In order to ensure that your code is ready for review, the following steps need to be taken and completed.
- When a task is created, the task should have been given a clear user story that is short and to the point, but also gives you enough room to work with. In addition to this, clearly outline and state what pieces of your work are most important in the acceptance criteria, as these should be prioritized above all else when working on a feature.
- Prioritize working on items with the highest priority if you have multiple tasks assigned to you. This ensures what is needed the most gets done the fastest.
- When you start a task that you were assigned, update the item's <u>status</u>. Item statuses can be found on the right menu after clicking on an item in the product backlog. Once you have begun working on a task, you should set the status to _"In progress"_. When you are finished, the task should be set to _"In review"_ as an indicator that you are ready for another developer to look over your work and sign off on your changes.
    - When your work is ready for review, everything should be pushed into your branch on GitHub, and a merge request should be made. Merge requests have to be reviewed and checked for conflicts before they can be accepted and merged into the correct branch. <u>__Do NOT push or merge directly to main.__</u>
    - To ensure that your acceptance criteria is properly met and that others can verify this, thoroughly comment your code and ensure that your comments are easy to find in relation to your acceptance criteria. _(e.g: If your criteria states that "Feature A should have a 'movable light source', there should be comments in Feature A's code that directly mention 'movable light source' to make sure the development team can find it easily.)_
- Provide adequate statements in your commitment messages to give a clear summary of what you have done.
