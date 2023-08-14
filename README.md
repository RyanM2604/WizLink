# README

Welcome to WizLink's README! This README provides an overview of WizLink and how to set it up and use it.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This Flask application is designed to [describe the purpose or functionality of your application].

## Installation

1. Clone the repository:

  ```
  git clone <repository_url>
  cd <repository_directory>
  ```
2. Create a virtual environment:

  ```
  python -m venv venv
  ```

3. Activate the virtual environment:

* On Windows:

  `venv\Scripts\activate`

* On macOS and Linux:

  `source venv/bin/activate`

4. Install the required packages:
  
  ```
  pip install -r requirements.txt
  ```

5. Set up environment variables:

Create a **.env** file in the root directory and add the necessary environment variables. Refer to **.env.example** for the required variables.

## Usage
Run the Flask application:

```
flask run
```

Access the application in your web browser:

Open your web browser and go to: http://127.0.0.1:5000

## Endpoints
* **/**: Landing page.
* **/register**: User registration page.
* **/login**: User login page.
* **/logout**: Log out the user.
* **/tags**: Page to select and submit tags.
* **/submit-tags**: Endpoint to handle tag submission.
* **/call**: List and create video call rooms.
* **/join-room**: Join a video call room.
* **/delete-room**: Delete a video call room.
* **/publish**: Publish a guide or post.
* **/guides**: Display a list of guides or posts.
* **/post/<pid>**: View a specific guide or post.
* **/leaderboard**: Display the user leaderboard.
* **/awards**: Display user awards based on points.

## Contributing
Contributions are welcome! If you find a bug or have suggestions for improvements, feel free to open an issue or submit a pull request. Please make sure to follow the code style and adhere to any project guidelines.

## License
[MIT License]
