## Roommate Match Description 
Roommate Match is student housing management portal that helps students find compatible roomates and form roommate groups of two to four students. When a student logs in they can choose to view other students, send requests, view the status of sent requests, or update their prefences or interests. Once a student accepts another student's request the admin must approve the pairing before the pairing becomes finizalized. Once students are assigned to a group they cannot send requests to other students. The admin can approve or deny pairings, and create new students. 

## System Test Cases
#### test_update_request_list_accepted 
Creates three students. One student sends requests to the other two students. Both students accept the request and updateStatus() marks the request as accepted. The test first confirms that the request was successfully added to the system's request list by checking that there is exactly one request. Then, when updateRequestList() is called, the accepted requests should be removed from the request list and moved into the pairing list. When finalize pairing is called, it simulates the admin approving the pairing. The pairing is removed from the pairing list, and the students are assigned to the same groupID. Lastly, we check all three students have the same groupID.
#### test_update_request_list_rejected 
Creates three students. One student sends requests to the other two students. Both students reject the request and updateStatus() marks the request as rejected. The test first confirms that the request was successfully added to the system's request list by checking that there is exactly one request. Then, when updateRequestList() is called, the rejected requests should be removed from the request list. Then we check that the request list is empty and the pairing list is empty. Lastly, we check all three students groupID is still -1.

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/2HAsn8j_)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=23409764)

Client Pitch: https://docs.google.com/document/d/1DDQLSBJ6T8TasFYi-sCNYtr0rpkmOyzu6-dGCkTyK6w/edit?usp=sharing

Sprint Backlog: https://docs.google.com/document/d/1Ja-57dA5BZ617KdQ6HQ01w6K-lKyyLGOxOXHXSWbuKI/edit?usp=sharing

Scrum Master documentation: https://docs.google.com/document/d/1CzXzZboKK6pSPUpFnAa0vyw8HYxbTzC7BWcaUR7b8rQ/edit?usp=sharing

### Conceptual / Class Diagram
![UML Class Diagram](UMLClassDiagram.png)
